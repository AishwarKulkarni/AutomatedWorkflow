"""
ahk_bridge.py — Persistent AHK subprocess manager.

Responsibilities:
  - Spawns `agent_runner.ahk` as a subprocess with piped stdin/stdout/stderr.
  - Exposes a synchronous `call(action_name, args, target_app)` method that
    writes a JSON command and blocks until a JSON result line is returned.
  - Watches for unexpected process death and restarts automatically.
  - Captures AHK stderr and logs it for debugging.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import threading
import time
from typing import Any

logger = logging.getLogger(__name__)

# Result returned when the bridge itself encounters an error (not AHK)
def _error_result(message: str, duration_ms: int = 0) -> dict[str, Any]:
    return {
        "success": False,
        "output": "",
        "error": message,
        "duration_ms": duration_ms,
    }


class AHKBridge:
    """Manages a persistent AHK subprocess and provides a synchronous call interface."""

    _RUNNER_PATH = os.path.join("src", "automation", "autohotkey", "agent_runner.ahk")
    _RESTART_DELAY_S = 1.0   # seconds to wait before restarting after a crash

    def __init__(self) -> None:
        self._proc: subprocess.Popen | None = None
        self._lock = threading.Lock()      # serialises concurrent call() invocations
        self._stderr_thread: threading.Thread | None = None
        self._watcher_thread: threading.Thread | None = None
        self._running = False              # set False to stop background threads

    # ── Public API ────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Spawn the AHK subprocess. Called once on application startup."""
        self._running = True
        self._spawn()
        self._start_watcher()

    def stop(self) -> None:
        """Terminate the AHK process on application shutdown."""
        self._running = False
        self._kill_proc()

    def call(
        self,
        action_name: str,
        args: list[str] | None = None,
        target_app: str | None = None,
    ) -> dict[str, Any]:
        """
        Send a single action to AHK and return the structured result.

        Returns a dict with keys: success (bool), output (str), error (str),
        duration_ms (int).  Never raises; failures are encoded in the result.
        """
        if args is None:
            args = []

        command: dict[str, Any] = {"action": action_name, "args": args}
        if target_app:
            command["target_app"] = target_app

        with self._lock:
            if self._proc is None or self._proc.poll() is not None:
                return _error_result("AHK process is not running")

            t_start = time.monotonic()
            try:
                line = json.dumps(command) + "\n"
                self._proc.stdin.write(line.encode("utf-8"))
                self._proc.stdin.flush()
            except OSError as exc:
                return _error_result(f"Failed to write command to AHK: {exc}")

            try:
                raw = self._proc.stdout.readline()
                duration_ms = int((time.monotonic() - t_start) * 1000)
                if not raw:
                    return _error_result("AHK process closed stdout unexpectedly", duration_ms)
                result = json.loads(raw.decode("utf-8").strip())
                # Ensure duration_ms from AHK is preserved, but add wall-clock as fallback
                if "duration_ms" not in result:
                    result["duration_ms"] = duration_ms
                return result
            except json.JSONDecodeError as exc:
                return _error_result(f"Invalid JSON from AHK: {exc}")
            except OSError as exc:
                return _error_result(f"Failed to read result from AHK: {exc}")

    # ── Internal ──────────────────────────────────────────────────────────────

    def _spawn(self) -> None:
        """Launch the AHK subprocess."""
        ahk_exe = os.getenv("AHK_PATH", "AutoHotkey.exe")
        try:
            self._proc = subprocess.Popen(
                [ahk_exe, self._RUNNER_PATH],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd(),
            )
            logger.info("AHKBridge: spawned PID %d", self._proc.pid)
            # Start a background thread to drain and log stderr
            self._stderr_thread = threading.Thread(
                target=self._drain_stderr, daemon=True
            )
            self._stderr_thread.start()
        except FileNotFoundError:
            logger.error(
                "AHKBridge: could not find AHK executable '%s'. "
                "Set AHK_PATH in .env to the full path.",
                ahk_exe,
            )
            self._proc = None

    def _kill_proc(self) -> None:
        """Terminate the AHK process if it is alive."""
        if self._proc is not None:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=3)
            except Exception:
                try:
                    self._proc.kill()
                except Exception:
                    pass
            self._proc = None

    def _drain_stderr(self) -> None:
        """Read AHK stderr and log each line. Runs in a daemon thread."""
        proc = self._proc
        if proc is None:
            return
        try:
            for raw in proc.stderr:
                line = raw.decode("utf-8", errors="replace").rstrip()
                if line:
                    logger.warning("AHK stderr: %s", line)
        except Exception:
            pass

    def _start_watcher(self) -> None:
        """Start a background thread that watches for unexpected process death."""
        self._watcher_thread = threading.Thread(
            target=self._watch_loop, daemon=True
        )
        self._watcher_thread.start()

    def _watch_loop(self) -> None:
        """Poll the process and restart it if it exits unexpectedly."""
        while self._running:
            time.sleep(0.5)
            if not self._running:
                break
            if self._proc is not None and self._proc.poll() is not None:
                logger.warning(
                    "AHKBridge: process exited unexpectedly (code %d). Restarting in %.1fs…",
                    self._proc.returncode,
                    self._RESTART_DELAY_S,
                )
                time.sleep(self._RESTART_DELAY_S)
                if self._running:
                    with self._lock:
                        self._spawn()

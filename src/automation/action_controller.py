import os
import re
from typing import Any
from automation.ahk_bridge import AHKBridge

class ActionController:
    """
    A deep module that encapsulates all AutoHotkey interactions.
    Handles manifest parsing, system prompt generation, and action execution.
    """
    _MANIFEST_PATH = os.path.join(".agents", "context", "ahk_manifest.md")
    
    def __init__(self):
        self._ahk = AHKBridge()
        self._manifest = self._load_manifest()

    def start(self):
        self._ahk.start()
        
    def stop(self):
        self._ahk.stop()

    def _load_manifest(self) -> dict:
        try:
            with open(self._MANIFEST_PATH, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            return {"action_names": [], "prompt_block": ""}

        action_names = []
        actions_match = re.search(r"## Actions\s*\n([\s\S]*?)(?=\n## |\Z)", content)
        if actions_match:
            actions_section = actions_match.group(1)
            found = re.findall(r"\|\s*`?([A-Za-z][A-Za-z0-9_]*)`?\s*\|", actions_section)
            seen = set()
            for name in found:
                if name not in ['Action', 'Signature', 'Description'] and name not in seen:
                    seen.add(name)
                    action_names.append(name)

        return {"action_names": action_names}

    def get_system_prompt_additions(self) -> str:
        """Returns a concise system prompt block with available apps and actions."""
        additions = "You can automate tasks using AutoHotkey. For detailed information on features like Workflows, UIAutomation, or App Instructions, use the `read_context_file` tool to read 'notch_features.md'.\n\n"
        
        # Inject manifest directly into the system prompt as the single source of truth
        if os.path.exists(self._MANIFEST_PATH):
            with open(self._MANIFEST_PATH, "r", encoding="utf-8") as f:
                additions += f"--- AHK MANIFEST (SINGLE SOURCE OF TRUTH) ---\n{f.read()}\n-------------------------------------------\n\n"
        
        valid_actions = self._manifest.get("action_names", [])
        if valid_actions:
            additions += f"Valid Action Names: {', '.join(valid_actions)}\n\n"
            
        available_apps = {}
        try:
            with open("src/automation/autohotkey/apps.ahk", "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("Global ") and ":=" in line:
                        parts = line.split(":=")
                        var_name = parts[0].replace("Global", "").strip()
                        app_val = parts[1].strip().strip('"')
                        available_apps[var_name] = app_val
        except Exception:
            pass
        
        if available_apps:
            additions += "Available apps you can control (pass the exact variable name to target_app):\n"
            for name, val in available_apps.items():
                additions += f"- {name}: '{val}'\n"
            
        return additions

    def execute_action(self, action_name: str, args: list[str] | None = None, target_app: str | None = None) -> dict[str, Any]:
        """Validates the action name and delegates to AHKBridge."""
        valid_actions = self._manifest.get("action_names", [])
        if valid_actions and action_name not in valid_actions:
            return {
                "success": False,
                "output": "",
                "error": f"Unknown action '{action_name}'. Valid actions: {', '.join(valid_actions)}",
                "duration_ms": 0,
            }
        
        return self._ahk.call(action_name, args, target_app)


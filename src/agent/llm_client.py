import os
import json
import time
import requests
from typing import Iterator, Tuple

class LLMClient:
    """Client for communicating with the Groq API."""
    MAX_RATE_LIMIT_RETRIES = 3
    RATE_LIMIT_RETRY_SECONDS = 2
    MAX_RETRY_DELAY_SECONDS = 30

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def stream_chat(self, messages: list[dict], tools: list[dict], is_cancelled_func) -> Iterator[Tuple[str, dict]]:
        """
        Streams chat responses.
        Yields (chunk_text, tool_calls_dict) where tool_calls_dict is populated if any occur.
        """
        if not self.is_configured():
            raise ValueError("No GROQ_API_KEY set in .env")

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"model": self.model, "messages": messages, "stream": True, "tools": tools}
        tool_calls = {}

        for attempt in range(self.MAX_RATE_LIMIT_RETRIES + 1):
            if is_cancelled_func():
                return

            response = requests.post(self.api_url, headers=headers, json=payload, stream=True, timeout=60)
            if response.status_code == 429 and attempt < self.MAX_RATE_LIMIT_RETRIES:
                retry_after = response.headers.get("Retry-After")
                try:
                    delay = float(retry_after) if retry_after is not None else self.RATE_LIMIT_RETRY_SECONDS * (2 ** attempt)
                except (TypeError, ValueError):
                    delay = self.RATE_LIMIT_RETRY_SECONDS * (2 ** attempt)
                response.close()

                # Wait in short intervals so stopping Notch cancels a pending retry promptly.
                deadline = time.monotonic() + min(max(delay, 0), self.MAX_RETRY_DELAY_SECONDS)
                while not is_cancelled_func() and time.monotonic() < deadline:
                    time.sleep(min(0.2, deadline - time.monotonic()))
                if is_cancelled_func():
                    return
                continue

            try:
                response.raise_for_status()
                with response as r:
                    for line in r.iter_lines():
                        if is_cancelled_func():
                            break
                        if not line:
                            continue
                        line = line.decode("utf-8")
                        if not line.startswith("data: "):
                            continue
                        payload_str = line[6:]
                        if payload_str == "[DONE]":
                            break

                        try:
                            delta = json.loads(payload_str)["choices"][0]["delta"]

                            content_chunk = delta.get("content", "")

                            if "tool_calls" in delta:
                                for tc in delta["tool_calls"]:
                                    idx = tc["index"]
                                    if idx not in tool_calls:
                                        tool_calls[idx] = {
                                            "id": tc.get("id"),
                                            "name": tc.get("function", {}).get("name", ""),
                                            "arguments": ""
                                        }
                                    if "function" in tc and "arguments" in tc["function"]:
                                        tool_calls[idx]["arguments"] += tc["function"]["arguments"]

                            yield content_chunk, tool_calls
                        except (json.JSONDecodeError, KeyError, IndexError):
                            pass
            finally:
                response.close()
            return

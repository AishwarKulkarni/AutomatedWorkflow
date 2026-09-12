import os
import json
import requests
from typing import Iterator, Tuple

class LLMClient:
    """Client for communicating with the Groq API."""
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

        with requests.post(self.api_url, headers=headers, json=payload, stream=True, timeout=60) as r:
            r.raise_for_status()
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

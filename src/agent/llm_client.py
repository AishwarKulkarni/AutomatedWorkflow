import os
import json
import requests
from typing import Iterator, Tuple

class LLMClient:
    """Client for communicating with the OpenRouter API."""
    def __init__(self):
        self.set_client("OpenRouter")

    def set_client(self, client_type: str):
        self.client_type = client_type
        if client_type == "OpenRouter":
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            self.model = os.getenv("OPENROUTER_MODEL", "")
            self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        elif client_type == "Groq":
            self.api_key = os.getenv("GROQ_API_KEY")
            self.model = os.getenv("GROQ_MODEL", "")
            self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        elif client_type == "Gemini":
            self.api_key = os.getenv("GEMINI_API_KEY")
            self.model = os.getenv("GEMINI_MODEL", "")
            self.api_url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def stream_chat(self, messages: list[dict], tools: list[dict], is_cancelled_func) -> Iterator[Tuple[str, dict]]:
        """
        Streams chat responses.
        Yields (chunk_text, tool_calls_dict) where tool_calls_dict is populated if any occur.
        """
        if not self.is_configured():
            raise ValueError(f"API key not set for {self.client_type}")

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"model": self.model, "messages": messages, "stream": True, "tools": tools}
        tool_calls = {}

        with requests.post(self.api_url, headers=headers, json=payload, stream=True, timeout=60) as r:
            if r.status_code != 200:
                try:
                    error_data = r.json()
                    error_msg = error_data.get("error", {}).get("message", r.text)
                except Exception:
                    error_msg = r.text
                raise Exception(f"API Error ({r.status_code}): {error_msg}")
            
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
                        for i, tc in enumerate(delta["tool_calls"]):
                            idx = tc.get("index", i)
                            if idx not in tool_calls:
                                import uuid
                                tc_id = tc.get("id")
                                if not tc_id:
                                    tc_id = "call_" + str(uuid.uuid4())[:8]
                                tool_calls[idx] = {
                                    "id": tc_id,
                                    "name": tc.get("function", {}).get("name", ""),
                                    "arguments": ""
                                }
                            if "function" in tc and "arguments" in tc["function"]:
                                tool_calls[idx]["arguments"] += tc["function"]["arguments"]
                    
                    yield content_chunk, tool_calls
                except (json.JSONDecodeError, KeyError, IndexError):
                    pass

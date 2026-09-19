"""
web_search.py — lightweight DuckDuckGo search wrapper used by the agent.

The LLM calls this when it is uncertain about an app-specific shortcut or UI
workflow.  We keep it dependency-light: only `duckduckgo-search` is required,
no API key needed.
"""

from __future__ import annotations


class WebSearchTool:
    """Thin wrapper around DuckDuckGo text search."""

    MAX_RESULTS = 3

    def search(self, query: str) -> str:
        """
        Search DuckDuckGo for *query* and return a formatted summary string.

        Returns a human-readable block of text containing up to MAX_RESULTS
        results (title + snippet + URL).  Never raises — on any error an
        error string is returned instead so the agent loop can continue.
        """
        try:
            from ddgs import DDGS  # lazy import; keeps startup fast

            results = list(DDGS().text(query, max_results=self.MAX_RESULTS))
            if not results:
                return f"No results found for: {query}"

            lines: list[str] = []
            for i, r in enumerate(results, 1):
                title = r.get("title", "").strip()
                body = r.get("body", "").strip()
                href = r.get("href", "").strip()
                lines.append(f"[{i}] {title}\n    {body}\n    {href}")

            return "\n\n".join(lines)

        except Exception as exc:  # network error, rate-limit, import error, …
            return f"web_search error: {exc}"

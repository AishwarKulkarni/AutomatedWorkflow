---
description: Analized Report of whole Project
---

# ⚠️ INSTRUCTION ⚠️

**Always update this file if any changes are made to the project architecture, features, dependencies, or significant file structures. This ensures that future agents always have the latest, most accurate context of the project.**

---

# Project Context: Notch Desktop Automation Assistant

## Overview

Notch is a Python-based desktop automation assistant that features a sleek, borderless UI built with PyQt6. It acts as an agent running in the background, which can be instantly toggled using a global hotkey (`Ctrl+Space`). The assistant communicates with the Groq API (using large language models) to determine actions based on user input, and then uses a persistent AutoHotkey (AHK v2) subprocess to seamlessly execute these desktop automation commands.

The LLM also has access to a `web_search` tool backed by DuckDuckGo (via the `ddgs` package) for general queries. For app-specific shortcuts or UI workflows, the LLM relies on a local knowledge base of per-app instructions stored in `.agents/context/apps/`. If a shortcut is missing, it will ask the user and learn it, rather than searching the web.

## Architecture and Data Flow

1. **User Input:** The user triggers the UI via `Ctrl+Space` and inputs a request in the Notch chat window.
2. **LLM Processing:** The `AgentManager` sends the chat history to the Groq API via `LLMClient`, providing a system prompt and two tools: `execute_actions` and `web_search`.
3. **Knowledge Retrieval:** If the LLM is uncertain about the exact steps or shortcut for an app, it checks the corresponding instruction file in `.agents/context/apps/`. If the information isn't there, it asks the user and updates the file for future use.
4. **Tool Invocation:** The LLM calls `execute_actions` with a **batch array** of actions (each having an `action_name`, `args`, and optional `target_app`).
5. **Validation & Execution:** The `AgentManager` runs each action sequentially via `ActionController`, stopping the batch early if any action fails.
6. **AHK Bridge:** The `AHKBridge` sends a JSON command to the persistent `agent_runner.ahk` script via `stdin`.
7. **Result:** The AHK script executes the Windows automation, captures the result, and writes a JSON response back to `stdout`. The batch result array is fed back into the LLM chat history.

## Directory Structure and Key Files

### Root

- `.env`: Stores environment variables like `GROQ_API_KEY` and `GROQ_MODEL`.
- `requirements.txt`: Python dependencies (`PyQt6`, `requests`, `python-dotenv`, `keyboard`, `pytest`, `duckduckgo-search`, `ddgs`).
- `.agents/context/ahk_manifest.md`: Contains the manifest defining available AHK actions and automation guidelines for the LLM.
- `.agents/context/apps/`: Contains per-app markdown files (e.g., `Notepad.md`) detailing specific shortcuts, workflows, and UI quirks learned by the LLM.

### `src/` (Python Source)

- `main.py`: Entry point. Loads environment variables and initializes the `Notch` UI.
- **`ui/ui.py`**: The main interface. A borderless PyQt6 window that stays on top. Handles state (collapsed vs. expanded), renders chat history including:
  - `execute_actions` → renders each action in the batch as `Executing: <name>(<args>)`
  - `web_search` → renders a muted `🔍 Searched: "..."` chip
- **`agent/agent.py`**: Contains `AgentManager` which orchestrates the conversational loop. Manages chat history, invokes the LLM, parses tool calls, and handles execution results for both tools.
- **`agent/llm_client.py`**: A lightweight HTTP client using `requests` to stream completions from Groq's OpenAI-compatible API.
- **`agent/web_search.py`**: `WebSearchTool` — wraps `ddgs.DDGS` to search DuckDuckGo. Lazy-imports the library, returns top-3 results as a formatted string (title + snippet + URL). Never raises; returns an error string on failure.
- **`automation/action_controller.py`**: The `ActionController` parses `.agents/context/ahk_manifest.md` (or fallback variables from `apps.ahk`) to provide the system prompt with valid tools. Dispatches valid actions to the AHK Bridge.
- **`automation/ahk_bridge.py`**: A robust manager for the AutoHotkey subprocess. Spawns `agent_runner.ahk`, handles JSON IPC via `stdin`/`stdout`, captures `stderr` for logging, and automatically restarts the AHK process if it crashes.
- **`utils/utils.py`**: OS-level helpers, including `_steal_windows_focus` (to reliably foreground the app on Windows) and `HotkeyThread` (listens for `Ctrl+Space` globally).

### `src/automation/autohotkey/` (AHK Scripts)

- **`agent_runner.ahk`**: A persistent AHK v2 script that loops on `stdin`. Parses incoming JSON commands, resolves variable references for target applications, dynamically invokes the appropriate AHK functions, and returns a JSON result on `stdout`.
- `controls.ahk`, `apps.ahk`, `libraries/JSON.ahk`: Supporting AHK scripts defining window controls, application targets, and JSON parsing.

## Technology Stack

- **Language:** Python 3, AutoHotkey v2
- **UI Framework:** PyQt6
- **LLM Provider:** Groq API (OpenAI-compatible endpoints)
- **Key Libraries:** `keyboard` (global hotkeys), `requests` (LLM API), `python-dotenv`, `ddgs` (DuckDuckGo web search).

## LLM Tools Reference

| Tool | When used | Schema |
|---|---|---|
| `execute_actions` | Run one or more desktop automation actions as a batch | `{ actions: [{ action_name, args[], target_app? }] }` |
| `web_search` | Look up general information (Note: not to be used for app shortcuts) | `{ query: string }` |

The system prompt instructs the model: *"Before attempting to automate an unfamiliar application, always check if an instruction file exists in `.agents/context/apps/[AppName].md`. If the file doesn't exist or is missing a shortcut, DO NOT search the web. Instead, stop and ask the user for the correct shortcut, then self-learn by updating the file."*

## Important Design Patterns

- **Persistent IPC:** Instead of spawning a new AHK process per command (slow), `ahk_bridge.py` maintains a long-running subprocess of `agent_runner.ahk`.
- **Batched Actions:** `execute_actions` accepts an array of actions executed sequentially. The batch stops early on the first failure — the full result array (with per-action outcomes) is returned to the LLM.
- **Per-App Self-Learning:** The LLM maintains a local knowledge base of app instructions. It asks the user for missing shortcuts and updates `.agents/context/apps/` dynamically, avoiding brittle web searches.
- **System Prompt Injection:** The LLM's system prompt dynamically loads available apps and actions parsed by `ActionController` from `ahk_manifest.md` and `apps.ahk`.
- **Deep Modules:** Classes like `AgentManager`, `ActionController`, and `WebSearchTool` encapsulate large portions of logic to keep the top-level application structure simple.


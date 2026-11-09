# Project Context: Notch Desktop Automation Assistant

## Overview

**Notch** is a Python-based desktop AI assistant featuring a floating, dynamic-island-style borderless UI built with PyQt6. It runs continuously in the background and can be summoned using global hotkeys (`Ctrl+Space` to toggle the UI, and `` ` `` for push-to-talk voice interaction). 

Notch combines natural voice interaction (Speech-to-Text via `faster-whisper` and Text-to-Speech via `edge-tts`) with a streaming conversational agent powered by the Groq API. For desktop actions, Notch interacts with Windows through a persistent AutoHotkey v2 (AHK) subprocess that executes structured, batch automation sequences.

Execution is protected by a **Strict Workflow Gate**: Notch only performs desktop automation if the user's intent matches a predefined workflow catalog in `workflows/`.

---

## Architecture and Data Flow

```
┌────────────────────────────────────────────────────────┐
│                      Notch UI                          │
│   (PyQt6 Dynamic Island / Collapsible Floating Notch)  │
│   • Global Hotkeys: Ctrl+Space (Toggle), ` (Voice)     │
│   • Smooth Apple-like fluid WaveWidget (60 FPS)        │
└──────────────┬──────────────────────────┬──────────────┘
               │                          │
        User Voice/Audio            Text & Actions
               │                          │
        ┌──────▼──────┐            ┌──────▼───────────────────┐
        │ Voice Layer │            │      AgentManager        │
        │ • STT:      │            │       (QThread)          │
        │   Whisper   │            └──────────┬───────────────┘
        │ • TTS:      │                       │
        │   edge-tts  │                       ├────────────────────────────┐
        └─────────────┘                       ▼                            ▼
                                    ┌──────────────────┐          ┌─────────────────┐
                                    │    LLMClient     │          │ActionController │
                                    │(Groq Cloud API)  │          │ (Workflow Gate) │
                                    └──────────────────┘          └────────┬────────┘
                                                                           │ stdin / stdout (JSON)
                                                                  ┌────────▼────────┐
                                                                  │ agent_runner.ahk│
                                                                  │  (AutoHotkey v2)│
                                                                  │ • FocusApp      │
                                                                  │ • Copy/Paste    │
                                                                  │ • SendShortcut  │
                                                                  └─────────────────┘
```

1. **User Input:**
   - **Keyboard:** The user toggles the UI with `Ctrl+Space` and types into the notch search box.
   - **Voice:** The user presses or toggles `` ` `` (backtick). `VoiceTranscriber` records 16kHz audio via `sounddevice` and transcribes it locally using `faster-whisper`.
2. **Catalog & Prompt Assembly:**
   - `AgentManager` injects `BASE_SYSTEM_PROMPT` (Notch persona: plain-text conversational, no markdown formatting, addresses user as "Boss"), dynamically scans `workflows/` via `workflow_manager.py` to build the catalog, and attaches available target apps from `ActionController`.
3. **LLM Invocation & Streaming:**
   - `LLMClient` opens a streaming SSE connection to Groq API (`/chat/completions`) offering tools: `read_workflow` and `execute_actions`.
   - Text chunks are streamed directly to the UI chat browser and spoken aloud via `TTSManager` (`edge-tts`).
4. **Two-Step Workflow Execution:**
   - If a request matches an available workflow, the LLM first calls `read_workflow` with the target workflow name to retrieve its steps.
   - The LLM compiles the layman workflow steps into a structured `execute_actions` batch call.
   - If no workflow matches, the LLM refuses action execution conversationally and suggests available workflows.
5. **Action Validation & Dispatch:**
   - `ActionController` validates action names against `.agents/context/ahk_manifest.md` (the Single Source of Truth for allowed actions).
   - Valid actions are dispatched to `AHKBridge`.
6. **Persistent AHK Bridge:**
   - `AHKBridge` sends a JSON command line to `src/automation/autohotkey/agent_runner.ahk` via `stdin`.
   - The persistent AHK process activates target apps (`FocusApp`), sends shortcuts, or uses clipboard injection (`CopyToClipboard` + `Paste`) for fast text insertion.
   - AHK writes JSON execution results back to `stdout`. Execution halts immediately if any action in the batch fails.

---

## Directory Structure and Key Files

### Root
- `.env`: API credentials (`GROQ_API_KEY`, `GROQ_MODEL`).
- `requirements.txt`: Python dependencies (`PyQt6`, `requests`, `python-dotenv`, `keyboard`, `faster-whisper`, `sounddevice`, `numpy`, `scipy`, `edge-tts`, `pytest`).
- `run_notch.bat`: Quick launcher activating `venv` and starting `src/main.py`.
- `CONTEXT.md`: This architecture context file.
- `AGENTS.md`: Guidelines and context for AI coding assistants working on this repo.
- `workflows/`: Markdown files defining approved workflows with YAML frontmatter (e.g., `notepad_letter.md`).
- `conversations/`: Auto-saved user chat transcripts with timestamps.
- `.agents/context/ahk_manifest.md`: Single source of truth defining available AHK actions, app mappings, and AI automation guidelines.

### `src/` (Python Source)

- **`main.py`**: Entry point. Loads `.env`, creates `QApplication`, and displays the `Notch` window.
- **`ui/ui.py`**:
  - `Notch`: Frameless, always-on-top, draggable floating pill widget. Smoothly animates between collapsed state (170×60) and expanded state (460×520).
  - `WaveWidget`: 60 FPS custom-painted audio wave animation for listening/processing states.
  - Integrates `VoiceTranscriber`, `TTSManager`, and `AgentManager`.
- **`agent/`**:
  - `agent.py` (`AgentManager`): `QThread` running the conversational loop, parsing tool calls, and coordinating execution.
  - `llm_client.py` (`LLMClient`): Streams chat completions from Groq's API with cancellation support.
  - `tools.py` (`AGENT_TOOLS`): OpenAI-compatible tool specifications for `read_workflow` and `execute_actions`.
  - `prompts.py` (`BASE_SYSTEM_PROMPT`): Persona instructions (plain text speech, Boss styling, workflow rules).
  - `workflow_manager.py`: Parses frontmatter and steps from `workflows/*.md` and generates catalog prompts.
- **`voice/`**:
  - `transcriber.py` (`VoiceTranscriber`): Streams microphone input via `sounddevice` and transcribes using `faster-whisper` (`base` model, `int8` CPU).
  - `tts.py` (`TTSManager`, `TTSWorker`): Generates speech using `edge-tts` (`en-US-AriaNeural`) and plays back via Qt Multimedia (`QMediaPlayer`).
- **`automation/`**:
  - `action_controller.py` (`ActionController`): Validates actions against `ahk_manifest.md` and provides system prompt additions.
  - `ahk_bridge.py` (`AHKBridge`): Manages the persistent AHK subprocess with auto-restart watchdog, mutex locking, and JSON IPC over `stdin`/`stdout`.
- **`utils/utils.py`**:
  - `HotkeyThread`: Global hotkey listener for `Ctrl+Space` (toggle UI) and `` ` `` (voice).
  - `_steal_windows_focus`: Win32 `keybd_event` sequence ensuring Notch takes foreground focus upon activation.

### `src/automation/autohotkey/` (AHK Scripts)
- **`agent_runner.ahk`**: Persistent daemon script reading JSON commands on `stdin` and returning JSON results on `stdout`.
- **`apps.ahk`**: Application target titles (`WinTitle`) and executable paths (`App_Notepad`, `App_Brave`, `App_Antigravity`).
- **`controls.ahk`**: Core implementation of automation actions (`FocusApp`, `SendShortcut`, `TypeText`, `CopyToClipboard`, `Paste`, `ClickAt`, `ToggleVoiceTyping`).
- **`libraries/JSON.ahk`**: AHK v2 JSON parsing and stringifying library.

---

## Technology Stack

- **Languages:** Python 3.13, AutoHotkey v2
- **UI Framework:** PyQt6 (6.8.1)
- **Speech & Audio:** `faster-whisper`, `sounddevice`, `numpy`, `scipy`, `edge-tts`
- **LLM Engine:** Groq API (e.g., Llama 3 models) via `requests` streaming
- **OS Automation:** AutoHotkey v2 over persistent standard I/O pipes
- **Global Hotkeys:** `keyboard`

---

## LLM Tools Reference

| Tool | Purpose | Schema |
|---|---|---|
| `read_workflow` | Reads the full instructions and steps of a specific workflow from `workflows/`. | `{ workflow_name: string }` |
| `execute_actions` | Executes an array of desktop automation actions sequentially as a single batch. | `{ actions: [{ action_name, args[], target_app? }] }` |

---

## Key Design Patterns & Invariants

1. **Strict Workflow Gate:** The LLM must never execute uncataloged actions. If no workflow matches, it must respond conversationally and explain what it can do.
2. **Two-Phase Action Execution:** When a workflow matches, the agent reads the workflow definition first (`read_workflow`), then compiles the actions into a single `execute_actions` batch call.
3. **Fail-Fast Safety:** If any action within an `execute_actions` batch fails, execution terminates immediately to avoid typing into unintended windows.
4. **Persistent IPC Daemon:** Rather than launching a new AHK process per command, `AHKBridge` maintains a long-lived subprocess with thread-safe request serialization.
5. **No Markdown in Agent Responses:** Responses are delivered conversationally in plain text as if spoken aloud (suitable for direct TTS consumption).

---
description: Analized Report of whole Project
---

# ⚠️ INSTRUCTION ⚠️

**Always update this file if any changes are made to the project architecture, features, dependencies, or significant file structures. This ensures that future agents always have the latest, most accurate context of the project.**

> **Last Updated:** Branch `feature/voice-feedback`, Commit `d029936 Added Voice Cmds Feature & some Improvemnts`

# Notch Automated Workflow Project Analysis

This document provides a detailed analysis of the **Notch** project, a highly advanced desktop AI assistant built in Python that combines LLM reasoning, voice interaction, and desktop automation via AutoHotkey.

## 1. Project Architecture & Stack

The project is structured as a modular Python desktop application.

**Core Stack:**

- **UI Framework:** PyQt6 (for the modern, responsive widget overlay).
- **LLM Integration:** OpenRouter API streaming completions (`requests`, `json`).
- **Automation:** AutoHotkey (AHK) for low-level OS and application control.
- **Voice/Audio:** `faster-whisper` (transcription), `edge-tts` (synthesis), `sounddevice`, `pygame`.
- **Environment:** `python-dotenv` for configuration, `keyboard` for global hotkeys.

**Directory Structure:**

- `src/agent/`: Contains the LLM client, prompt generation, tool registry, and workflow management.
- `src/agent/tools/`: Dynamically loaded Python tools exposed to the LLM (e.g., executing AHK actions, reading context).
- `src/automation/`: Manages the AHK subprocess bridge and action manifest parsing.
- `src/automation/autohotkey/`: The AHK scripts themselves (`agent_runner.ahk`, `apps.ahk`, etc.).
- `src/ui/`: Contains the PyQt6 user interface (`ui.py`).
- `src/voice/`: Handles speech-to-text (transcriber) and text-to-speech (synthesizer).
- `workflows/` & `.agents/`: Storage for chat histories and predefined markdown workflows.

---

## 2. Key Features and Implementation

### A. Dynamic, "Spotlight-Style" User Interface

The UI (`src/ui/ui.py`) is designed to be unobtrusive and highly polished, similar to Apple's Spotlight or Dynamic Island.

- **Implementation:** Built using a frameless `QMainWindow` with a translucent background. It stays on top (`WindowStaysOnTopHint`) and handles global focus stealing when activated.
- **Animations:** Uses `QPropertyAnimation` for smooth expansion and collapsing based on whether the agent is active or idle.
- **Visuals:** Features an animated liquid/organic audio visualizer (`WaveWidget`) that renders via `QPainter` with math functions (`math.sin`) for organic wave motion.
- **Chat Display:** Renders the conversation history using a `QTextBrowser`, displaying user messages, agent responses, and dynamically formatting LLM tool calls (like executing AHK actions or searching the web).
- **Auto-completion:** Typing `/` in the input field triggers a dropdown (`QListWidget`) suggesting available markdown workflows based on files in `.agents/context/workflows/`.

### B. LLM Agent & Conversational Loop

The core intelligence is driven by `src/agent/agent.py` and `llm_client.py`.

- **Streaming Client:** Communicates with OpenRouter. The `stream_chat` method yields text chunks for the UI to display in real-time and accumulates JSON arguments for tool calls.
- **System Prompt Injection:** The agent is instructed to act as "Notch", a crisp, professional British butler. The `ActionController` dynamically injects the `ahk_manifest.md` (the Single Source of Truth for valid AHK actions) directly into the system prompt.
- **Tool Execution Loop:** When the LLM calls a tool, the agent parses the JSON, executes the tool via the `ToolRegistry`, appends the tool's result to the history, and immediately streams a follow-up response in a continuous loop.
- **Failsafe:** Implements an automatic stop if 3 consecutive tool failures occur to prevent infinite API loops.

### C. Persistent Desktop Automation (AHK Bridge)

Instead of launching a slow AutoHotkey executable for every individual action, the project uses a highly efficient persistent bridge (`src/automation/ahk_bridge.py`).

- **Subprocess Management:** It spawns `agent_runner.ahk` via `subprocess.Popen` with piped `stdin` and `stdout`.
- **JSON IPC (Inter-Process Communication):** The Python bridge sends commands as JSON strings over `stdin`. The AHK script reads these, executes the requested action (defined in `controls.ahk` or `apps.ahk`), and writes a JSON result back to `stdout`.
- **Action Controller:** `action_controller.py` acts as a middleman. It parses `.agents/context/ahk_manifest.md` using regex to discover valid action names and ensures the LLM can only request valid actions.

### D. Workflow Manager

The system can execute complex, multi-step procedures defined in markdown files (`src/agent/workflow_manager.py`).

- **Triggering:** The user can trigger workflows explicitly via `/workflow-name` or via natural language (e.g., "start the build workflow").
- **Parsing:** It reads a markdown file and splits it by `## ` headers, where each header represents a distinct task.
- **Execution:** It feeds tasks to the LLM one by one. The LLM is instructed to call a specific `mark_task_completed.py` tool when it finishes a task, triggering the `WorkflowManager` to advance to the next step and feed the next prompt.

### E. Voice Interaction & Hotkeys

- **Global Hotkeys:** Uses a background `HotkeyThread` (via the `keyboard` library) to globally toggle the UI visibility and the push-to-talk recording feature without needing window focus.
- **Transcription (STT):** `VoiceTranscriber` records system audio and uses `faster-whisper` for quick, local transcription. When ready, it automatically populates the input field and sends the message.
- **Synthesis (TTS):** `VoiceSynthesizer` uses `edge-tts` (specifically the `en-GB-RyanNeural` voice to match the British butler persona) to read the assistant's final responses aloud.

### F. Dynamic Tool Registry

- **Implementation:** `src/agent/tool_registry.py` uses `importlib` and `inspect` to dynamically discover and load any class inheriting from `BaseTool` inside the `src/agent/tools/` directory.
- **Scalability:** This makes it trivial to add new capabilities (like `execute_actions.py`, `read_context_file.py`, or web search) without modifying the core agent loop.

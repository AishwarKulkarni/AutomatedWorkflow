# Developer & Agent Guidelines for Notch

This file provides rules, architectural conventions, and instructions for AI agents and developers working on the **Notch Desktop Automation Assistant** codebase.

For an architectural breakdown and technology stack reference, see [CONTEXT.md](file:///c:/Flutter%20Drive/Personal%20Workspace/AutomatedWorkflow/CONTEXT.md).

---

## 1. Core Principles & Philosophy

1. **Deep Modules:** Classes like `AgentManager`, `ActionController`, `AHKBridge`, `VoiceTranscriber`, and `TTSManager` must hide implementation complexity behind simple, clean interfaces.
2. **Single Source of Truth:** 
   - AHK actions and capabilities: documented in [`.agents/context/ahk_manifest.md`](file:///c:/Flutter%20Drive/Personal%20Workspace/AutomatedWorkflow/.agents/context/ahk_manifest.md).
   - App usage guides: stored as markdown files with frontmatter in [`instructions/`](file:///c:/Flutter%20Drive/Personal%20Workspace/AutomatedWorkflow/instructions). Guides should explain how to use an app and include researched, sourced shortcuts.
3. **Fail-Fast Desktop Safety:** Never execute blind or unsolicited keystrokes. Desktop actions must be checked against the instruction catalog and approved action manifest before calling tools.
4. **TTS-Friendly Spoken Output:** The LLM output is spoken aloud by `edge-tts`. Keep agent persona prompts instruction-free from markdown bullets, bolding, asterisks, or markdown tables.

---

## 2. Coding Guidelines

### Python (`src/`)
- **Python Version:** 3.10+ (tested on Python 3.13 on Windows).
- **Threading Model:** Use PyQt6 `QThread` and signals/slots (`pyqtSignal`) for any long-running or blocking work (LLM streaming, hotkey monitoring, audio playback, model inference) to ensure the UI thread stays responsive at 60 FPS.
- **Error Handling:** Subprocess interactions (`AHKBridge`) and network requests (`LLMClient`) must handle disconnections, timeouts, and process terminations gracefully without crashing the Qt application.
- **Imports:** Keep imports clean and cross-platform safe where applicable, using `os.path.join` or `pathlib.Path`.

### AutoHotkey (`src/automation/autohotkey/`)
- **AHK Version:** AutoHotkey **v2** only. Do not mix v1 and v2 syntax.
- **Inter-Process Communication:** All communication through `agent_runner.ahk` must adhere to strict line-delimited JSON. Stderr is reserved for diagnostic logs.
- **Window Focus Safety:** Always verify window activation (`WinWaitActive`) before simulating keystrokes or mouse clicks.

---

## 3. Modifying & Adding App Instructions

To teach Notch a new capability:
1. Create an app usage guide in [`instructions/`](file:///c:/Flutter%20Drive/Personal%20Workspace/AutomatedWorkflow/instructions) (e.g. `instructions/my_app.md`).
2. Add YAML frontmatter at the top:
   ```markdown
   ---
   name: my_app
   description: Brief description of the app and usage covered by the guide.
   ---
   ```
3. Research the app, especially its shortcuts, and cite authoritative sources. Describe the interface and reusable app operations. `workflow_manager.py` will register the guide upon scan.

---

## 4. Documentation Maintenance Rule

Whenever you change features, dependencies, tools, or architectural boundaries:
- **Always update [CONTEXT.md](file:///c:/Flutter%20Drive/Personal%20Workspace/AutomatedWorkflow/CONTEXT.md)** to keep context accurate for subsequent agent sessions.




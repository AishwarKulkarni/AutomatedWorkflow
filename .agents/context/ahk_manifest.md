---
title: AHK Automation Manifest
version: "2.0"
---

# AHK Automation Manifest

This file is the **single source of truth** for what the LLM is allowed to automate.
Python reads it at startup to build the system prompt and to validate action names
before they are sent to AHK.

---

## Apps

| Variable Name     | Description                                      |
| ----------------- | ------------------------------------------------ |
| `App_Antigravity` | Google Antigravity IDE — standalone code editor with integrated agent features; not the separate Antigravity App desktop command center |
| `App_AntigravityApp` | Google Antigravity App — separate standalone agent command center, launched as `Antigravity.exe`; not the IDE |
| `App_Notepad`     | Windows Notepad — plain-text editor              |
| `App_Brave`       | Web Browser                                      |
| `App_ChatGPT`     | ChatGPT desktop app                              |

Pass the **variable name** (e.g. `App_Notepad`) as the `target_app` argument.
Actions that do not need a window context (e.g. `TypeText`, `ClickAt`, `SendShortcut`) may omit `target_app`.

---

## Actions

These are the available capabilities you can perform:

- **`FocusApp()`**: Bring the target app window to the foreground, launching it if necessary. Requires `target_app`.
- **`TypeText(text)`**: Type literal short text into the active window, without treating characters like '{' or '^' as modifiers. (For long text, prefer `CopyToClipboard` + `Paste`).
- **`CopyToClipboard(data)`**: Copy the given data to the system clipboard.
- **`Paste()`**: Paste the current clipboard content into the focused window.
- **`ClickAt(x, y)`**: Click at screen coordinates `x`, `y` (use as a last resort; prefer shortcuts).
- **`SendShortcut(shortcut)`**: Press a keyboard shortcut using AutoHotkey syntax (e.g., `^n` for Ctrl+N, `^s` for Ctrl+S, `!f` for Alt+F, `{Enter}`).
- **`ShowMessage(msg)`**: Display a tooltip message at the bottom of the screen.
- **`ClearMessage()`**: Remove the currently visible tooltip message.
- **`ClearTextField()`**: Select-all and delete the contents of the focused text field.
- **`ToggleVoiceTyping()`**: Toggle Windows Voice Typing (Win + H shortcut).

---

## AI Automation Guidelines

When automating tasks via AHK, act as a fast, reliable desktop automation executor. Adhere to these principles:

### Best Practices
1. **Always Focus First:** Start any app interaction by explicitly focusing the target app (e.g., `FocusApp("App_Notepad")`).
2. **Favor Keyboard Shortcuts:** Rely on standard shortcuts (e.g., `^s`, `^c`, `^v`, `!f`, `{Tab}`, `{Enter}`) over screen coordinates.
3. **Use Clipboard for Text:** Use `CopyToClipboard(data)` followed by `Paste()` for efficiency and reliability when entering text blocks.
4. **Batch Execution:** Compile the workflow's actions into a single `execute_actions` batch call so they run smoothly in sequence.
5. **Fail-Fast Safety:** If an action fails (e.g. application failed to activate), stop immediately rather than spamming shortcuts into whatever window is active.
6. **No Unsolicited Automation:** Only execute desktop automation if a matching workflow exists in your available workflows catalog. If no workflow matches, explain that to Boss conversationally.

---
app_name: "Notepad"
executable: "notepad.exe"
---
# Notepad Automation Guide

## Keyboard Shortcuts
| Task | Shortcut | Notes |
|---|---|---|
| New File | `^n` | |
| Open File | `^o` | Wait 500ms for file picker dialog |
| Save | `^s` | If new file, wait 500ms for save dialog |
| Save As | `^+s` | Wait 500ms for save dialog |
| Print | `^p` | Wait 500ms for print dialog |
| Find | `^f` | Wait 200ms for find dialog |
| Replace | `^h` | Wait 200ms for replace dialog |
| Select All | `^a` | |
| Undo | `^z` | |
| Exit | `!{F4}` | May prompt to save if unsaved changes exist |

## Common Workflows
- **Save a new file:** Press `^s`, wait 500ms for the Save As dialog to appear, type the file path, and press `{Enter}`.
- **Find and Replace text:** Press `^h`, type the search term, press `{Tab}`, type the replacement, and press `!a` (Alt+A) to replace all.
- **Open an existing file:** Press `^o`, wait 500ms, type the full path to the file, and press `{Enter}`.

## UI Quirks / Gotchas
- In Windows 11, Notepad has tabs. You can use `^{Tab}` and `^+{Tab}` to navigate between open tabs, and `^w` to close the current tab.
- The main text editing area is a standard Windows edit control (or RichEdit in modern versions) and generally exposes its text fully to UIA, making it easy to read or set values directly via automation if keyboard input is not preferred.
- The Save/Open dialogs are standard Windows File Picker dialogs, which run in a separate window context and can temporarily steal focus.

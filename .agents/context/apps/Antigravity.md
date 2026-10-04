---
app_name: "Antigravity IDE"
executable: "antigravity.exe"
---
# Antigravity IDE Automation Guide

## Keyboard Shortcuts
| Task | Shortcut | Notes |
|---|---|---|
| Command Palette | `^+p` | Wait 200ms for palette dropdown |
| Quick Open / File Search| `^p` | Wait 200ms for search input |
| Global Search | `^+f` | Focuses the search sidebar |
| Toggle Terminal | `^`` | Focuses or hides the integrated terminal |
| Toggle Sidebar | `^b` | |
| Open Settings | `^,` | Opens settings tab |
| Focus Chat / AI | `^+l` | Focuses the main AI chat window (if applicable) |
| Inline Chat | `^i` | Opens inline AI generation |
| Accept Inline Suggestion | `{Tab}` | When a ghost text suggestion is visible |
| Save File | `^s` | |
| Close Editor | `^w` | |
| Switch Editor Tab | `^{Tab}` | |

## Common Workflows
- **Open a specific file:** Press `^p`, wait 200ms, type the filename, wait for results to filter, and press `{Enter}`.
- **Run a command from palette:** Press `^+p`, wait 200ms, type the command name, and press `{Enter}`.
- **Focus Terminal to run a script:** Press `^``, wait 200ms, type the command (e.g., `npm run dev`), and press `{Enter}`.

## UI Quirks / Gotchas
- Antigravity IDE is built on web technologies (like Electron or similar), which means its UIA tree can be extremely deep and complex. Traversing the entire tree via UIA might be slow.
- Popups, dropdowns, and hover widgets (like the Command Palette or IntelliSense suggestions) are often transient and might disappear if the window loses focus.
- Keybindings can be highly customized by the user, so the default shortcuts listed above might be overridden in specific user environments.
- AI panels or sidebars might require waiting for content generation or loading states before interacting with elements within them.

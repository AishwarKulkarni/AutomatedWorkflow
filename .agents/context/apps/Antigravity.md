---
app_name: "Antigravity"
executable: "Antigravity.exe"
---

# Antigravity Automation Guide

## Keyboard Shortcuts

| Task                 | Shortcut   | Notes                                      |
| -------------------- | ---------- | ------------------------------------------ |
| Inline Command (IDE) | `^i`       | Opens instructive inline modality          |
| Accept Suggestion    | `{Tab}`    | Accepts autocomplete suggestion            |
| Cancel Suggestion    | `{Esc}`    | Cancels autocomplete                       |
| Accept Word          | `^{Right}` | Accepts suggestion word-by-word            |
| New Chat             | `^+l`      | Opens a new chat in Sidebar Chat Canvas    |
| Slash Command        | `/`        | Triggers slash command menu in Chat Canvas |
| Mention Context      | `@`        | Opens mention menu in Chat Canvas          |

## Common Workflows

- **Trigger Slash Command:** Type `/` in the chat canvas, wait for the menu to appear, type the command name, and press `{Enter}`.
- **Add Context:** Type `@` in the chat canvas, wait for the menu, type the context name (e.g., file name), and press `{Enter}`.
- **Inline Edit (IDE):** Select the target text block, press `^i`, wait for the input prompt to appear, type your instructions, and press `{Enter}`.

## Specific Workflows

- **Use a Skill:** Open the Chat Canvas, type or paste `/skill_name`, press `{Tab}` to select the desired skill, paste your prompt, and press `{Enter}` to execute.

## UI Quirks / Gotchas

- Antigravity consists of both the **Antigravity IDE** (`Code.exe`) and **Antigravity 2.0** desktop app (`Antigravity.exe`). Automation flows should target the correct window.
- When automating the Chat Canvas, ensure the chat input field has focus before typing.
- Slash commands (`/`) and context mentions (`@`) trigger asynchronous popup menus. Always include a small delay after typing `/` or `@` to allow the menu to render before sending further keystrokes.

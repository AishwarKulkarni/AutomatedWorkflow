---
name: antigravity_ide
description: Detailed usage reference for Google Antigravity IDE, including editor and agent surfaces, navigation, shortcuts, and safe review practices.
---

# Google Antigravity IDE Usage Guide

## App and platform

This guide covers the standalone Google Antigravity IDE on Windows: the code editor application with integrated agent capabilities. It is a different desktop application from **Antigravity App (Antigravity 2.0)**, the separate agent command center that has no IDE. Google distributes them as separate products/installers. Shortcuts and features are surface-specific; do not transfer Antigravity App, CLI, or host-editor shortcuts to the IDE unless the IDE documentation confirms them. Check the IDE's **Settings > Shortcuts** when a mapping is uncertain.

## Interface map

- **Editor view:** Work directly with project files, tabs, and code. Standard editor shortcuts may be available, but verify any editor-specific command in the app's shortcut list or command palette.
- **Integrated Agent Manager/panel:** Enter a task in the IDE's agent surface. Review plans, permission prompts, inline diffs, and results before accepting changes or running commands.
- **Inline review:** Agent edits appear in the editor with Accept and Reject controls. Review each change in the active file.
- **Settings:** Configure app behavior and inspect or customize shortcuts. Settings can have global and project-specific scopes; verify which scope is open before changing preferences.
- **Workspace/project:** The active project determines which files and context the agent can use. Confirm the project shown in the window before supplying instructions that modify files.

## Verified shortcuts

These shortcuts are documented for Antigravity IDE on Windows/Linux. Do not confuse them with Antigravity App shortcuts; the app has separate documentation and different product surfaces.

| Shortcut | Use | Notes |
|---|---|---|
| `Ctrl+E` | Switch between the editor and the integrated Agent Manager surface | Google documents this for Antigravity IDE on Windows/Linux. |
| `Alt+Enter` | Accept the focused agent change | IDE inline review; inspect the change before accepting. |
| `Alt+Shift+Enter` | Reject the focused agent change | IDE inline review; verify the correct change has focus. |
| `Ctrl+Alt+M` | Add a comment on the selected code and queue it for the next chat prompt | IDE editor; select the intended code first. |

For other editor or agent commands, inspect **Settings > Shortcuts** or the visible controls. Standard shortcuts from VS Code or another editor may differ if the IDE's keymap changes.

## Common operations

### Focus the IDE and confirm its project

1. Focus `App_Antigravity` and confirm the foreground window is **Antigravity IDE**.
2. Confirm the open project/workspace before using the editor or prompting its integrated agent.
3. If the intended project is absent or ambiguous, ask the user which project to use. Do not open an inferred path.

### Switch between the editor and integrated Agent Manager

Press `Ctrl+E` to switch between the IDE editor and its integrated Agent Manager surface. This is part of the IDE. It is not a way to launch the separate Antigravity App.

### Locate a project file

1. Confirm the intended project is active.
2. Use the editor's visible file/search controls. If you want a keyboard route, verify the shortcut in the IDE's current **Settings > Shortcuts** first.
3. Select the intended result only after checking its path/name. If several results are ambiguous, refine the search rather than opening a guess.

### Start an agent task

1. Confirm the correct project and conversation are active.
2. Focus the agent prompt using the visible input in the IDE's integrated Agent Manager.
3. Enter the user's task without adding requirements. For long text, use clipboard and paste.
4. Submit only when requested. Review permission prompts, plans, diffs, and results; do not accept changes or run commands based on an unclear prompt.

### Find a command or shortcut

Use the IDE's visible command/search controls or **Settings > Shortcuts** to discover commands. Do not assume Antigravity App's `Ctrl+K` / `Ctrl+P` command palette mappings apply to the IDE.

### Review agent changes

Inspect the changed files and diff in the review surface. Confirm the target project and affected files before accepting edits. If the change is unexpected or destructive, stop and ask the user before accepting it.

## Safety and recovery

- Confirm the active project and conversation before entering prompts or accepting edits.
- A prompt can initiate agent work across project files, terminal, and browser. Treat terminal execution, external publishing, deletion, and overwrites as consequential and require clear user intent.
- Do not switch conversations or close tabs when the user's requested context may be lost or changed.
- If focus, project identity, shortcut behavior, or a permission dialog is unclear, stop. Use the visible UI or command palette to re-establish context rather than sending repeated keystrokes.
- Keyboard shortcuts and capabilities vary between Antigravity IDE, Antigravity App, CLI, and IDE extensions. Antigravity App is a separate installed app, not another name for the IDE.

## Sources

- [Google Antigravity: Getting started](https://antigravity.google/docs/getting-started) — IDE installation and switching between the editor and integrated Agent Manager (`Ctrl+E`).
- [Google Antigravity IDE: Review changes in the editor](https://antigravity.google/docs/ide/review-changes-editor) — IDE-specific accept, reject, and code-comment shortcuts.
- [Google Antigravity: Choose your Antigravity](https://antigravity.google/docs/home) — separates Antigravity App, IDE extensions, CLI, and SDK surfaces.
- [Google Antigravity: Download](https://antigravity.google/download) — separate Antigravity App and standalone IDE downloads.
- [Google Antigravity IDE product page](https://www.antigravity.google/product/antigravity-ide) — editor, agent, and artifact surfaces.

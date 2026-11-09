---
name: antigravity_app
description: Detailed guide to Google's separate Antigravity App desktop command center, including projects, agent conversations, review panels, and verified Windows shortcuts.
---

# Google Antigravity App Usage Guide

## App and platform

This guide covers **Antigravity App (Antigravity 2.0)**, the standalone Windows desktop application for launching, orchestrating, and reviewing agent work. It is not Antigravity IDE: the App has no code editor, while Antigravity IDE is a separate desktop editor with integrated agent features. Google distributes them as separate products. Do not use this guide's shortcuts or interface descriptions for the IDE, CLI, or IDE extensions.

Notch registers `App_AntigravityApp` for the Antigravity App executable and `App_Antigravity` for the separate IDE. Use the App target for this guide; never send App-specific shortcuts to the IDE target.

## Interface map

- **Projects/sidebar:** Projects define the folders and resources available to agents and can scope settings and permissions. Choose the intended project before starting work.
- **Conversations:** Sessions contain prompts and agent work. Search can find conversations by title, project, and full text. Quick conversations outside projects use a local scratch folder and have their own settings and permissions.
- **Main conversation:** Enter goals, questions, or follow-up instructions in the message box. The agent can run synchronously or asynchronously and may use tools according to project permissions.
- **Overview panel:** Summarizes work produced in the current conversation, such as review, files, terminals, artifacts, plans, and subagents.
- **Side panel:** Displays work beside the conversation. Artifacts, files, diffs, terminal, subagent conversations, and browser pages open as tabs in this panel.
- **Review:** Shows project changes and diffs. Inspect them before accepting or committing changes.
- **Modes and remote work:** Local project work runs with local project access subject to permissions. Remote Agents use a Google-managed remote environment and are a distinct execution destination; availability depends on plan/account.
- **Settings > Shortcuts:** Displays the app's current shortcut mappings. Use it when a binding is absent or customized.

## Verified shortcuts

The following mappings are documented for Antigravity App on Windows/Linux. Product shortcuts are customizable; confirm in Settings > Shortcuts if a key does not behave as listed.

| Shortcut | Effect | Notes |
|---|---|---|
| `Ctrl+K` | Search conversations and open the command palette's conversation category | Searches conversation title, project, and full text. |
| `Ctrl+P` | Search project files | Use only after confirming the active project. |
| `Ctrl+F` | Find text in an open file or conversation | The search scope depends on the active surface. |
| `Ctrl+Shift+P` | List commands available in the current view | Type to filter, inspect the command label, then press `Enter` to run it. |
| `Ctrl+Shift+K` | Open project search/switcher | Confirm the project before starting work in it. |
| `Ctrl+Shift+B` | Show or hide the side panel | Side panel contains review and other work tabs. |
| `Ctrl+Alt+O` | Show or hide the Overview panel | Conversation-level summary panel. |
| `Ctrl+T` | Open a new side-panel tab | Does not create a conversation. |
| `Ctrl+W` | Close the current side-panel tab | Closing the last tab also closes the side panel. |
| `Ctrl+Shift+T` | Reopen the most recently closed side-panel tab | Restores its prior position and scroll point. |
| `Ctrl+Tab` / `Ctrl+Shift+Tab` | Move to next / previous side-panel tab | Tab switching applies when the side panel has tabs. |
| `Ctrl+Shift+M` | Maximize or restore the side panel | Toggles the side-by-side panel overlay. |
| `Ctrl+D` / `Ctrl+Shift+D` | Split the current view right / down | Creates a side-by-side conversation pane. Check active pane before entering a prompt. |
| `Ctrl+M` | Start or stop voice dictation in the message box | Dictates text into the prompt; this differs from two-way voice mode. |

## Common operations

### Find or resume an agent conversation

1. Press `Ctrl+K` and search for a distinctive title, project, or phrase from the conversation.
2. Confirm the matching conversation and project before opening it.
3. If several results look similar, refine the search instead of guessing.

### Open a project and start work

1. Use the visible Projects sidebar or `Ctrl+Shift+K` to locate the intended project.
2. Confirm its name and attached folders/resources. Project settings determine what the agent can access.
3. Start or resume a conversation in that project, then enter the user's instructions and submit once when requested.
4. Review the plan, permission requests, and proposed tool actions. Grant only permissions needed for the stated task.

### Start a one-off conversation outside a project

Use the visible new-conversation control outside a project. Such a conversation runs in a local scratch folder with its own settings and permissions, and inherits global permissions. It is not attached to a project workspace. Confirm this is appropriate before entering project-specific instructions.

### Search for and open a project file

1. Confirm the project whose files should be searched.
2. Press `Ctrl+P` and enter part of the filename.
3. Confirm the full path/result before opening it. If multiple files match, refine the search.

### Review agent output

Open the conversation's Review or Overview surface and inspect changed files, diffs, artifacts, and execution results. Ask for changes or reject edits when they do not match the request. Review the exact diff before accepting or committing project changes.

### Use the side panel and split conversations

Use `Ctrl+Shift+B` to toggle the side panel and `Ctrl+Alt+O` for Overview. Open side-panel tabs with `Ctrl+T`; move with `Ctrl+Tab` / `Ctrl+Shift+Tab`. `Ctrl+D` and `Ctrl+Shift+D` split conversations right/down. Before typing, check which pane or prompt has focus.

### Use voice

`Ctrl+M` starts/stops dictation into the message box. For a spoken, two-way conversation, use the visible Start Voice mode control; do not assume dictation and voice mode are the same feature. Voice availability and permissions depend on account and workspace.

## Safety and recovery

- Antigravity agents can read/write project files, run commands, search the web, use connected tools, and coordinate subagents. Project permission settings and execution mode matter; inspect prompts and scope before approving.
- A local project and a Remote Agent use different execution environments. Confirm the intended environment before starting work or sharing project data.
- A quick conversation outside a project uses a scratch folder; do not treat it as operating on the user's project.
- Do not accept, publish, commit, delete, or overwrite project changes unless explicitly requested and the exact effect is clear.
- Search, split-pane, side-panel, and tab shortcuts change focus or context. Verify the selected conversation, project, pane, and tab before entering content.
- Focus `App_AntigravityApp` before app interaction. Never use `App_Antigravity` for this guide; that target opens the IDE.
- If project identity, local/remote mode, focus, permission scope, or a shortcut is unclear, stop and ask rather than trying a similar product's controls.

## Sources

- [Google Antigravity: Introducing Google Antigravity 2.0](https://antigravity.google/blog/introducing-google-antigravity-2) — explicitly describes the standalone Antigravity App as separate from Antigravity IDE and without an IDE.
- [Google Antigravity: Choose your Antigravity](https://antigravity.google/docs/home) — product surface overview for App, CLI, IDEs, and SDK.
- [Google Antigravity: Search and command palette](https://antigravity.google/docs/search) — App-specific conversation, file, project, and command shortcuts.
- [Google Antigravity: Side panel and Overview panel](https://antigravity.google/docs/side-panel) — App side-panel, tab, overview, and split-view behavior/shortcuts.
- [Google Antigravity: Feature overview](https://antigravity.google/docs/features) — projects, permissions, App-specific features, remote agents, and voice.
- [Google Antigravity: Download](https://antigravity.google/download) — separate standalone App and IDE product listings/downloads.

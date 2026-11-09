---
name: create-automation
description: Guide for creating automation workflows, onboarding applications, and defining new desktop capabilities for the Notch desktop automation assistant.
---

# AHK Automation & Workflow Authoring Guide

Use this guide when creating a new automation workflow, defining new desktop actions, or onboarding applications to the Notch desktop automation assistant.

---

## 1. Architecture Overview

Notch uses a declarative, fail-fast, workflow-centric architecture:

1. **Workflow Definitions ([`workflows/<workflow_name>.md`](file:///c:/Flutter%20Drive/Personal%20Workspace/AutomatedWorkflow/workflows))**:
   - The single source of truth for procedures.
   - Written in layman terms with standard keyboard shortcuts (e.g. `Ctrl+S`, `Enter`, `Alt+F4`).
   - Parsed at runtime by [`workflow_manager.py`](file:///c:/Flutter%20Drive/Personal%20Workspace/AutomatedWorkflow/src/agent/workflow_manager.py) and injected into the LLM system prompt catalog.
2. **App Registry ([`src/automation/autohotkey/apps.ahk`](file:///c:/Flutter%20Drive/Personal%20Workspace/AutomatedWorkflow/src/automation/autohotkey/apps.ahk))**:
   - Central registry defining window title matchers (`App_<Name>`) and launch executable paths (`App_<Name>_Exec`).
3. **AHK Manifest ([`.agents/context/ahk_manifest.md`](file:///c:/Flutter%20Drive/Personal%20Workspace/AutomatedWorkflow/.agents/context/ahk_manifest.md))**:
   - Single source of truth for LLM-allowed action primitives (`FocusApp`, `TypeText`, `CopyToClipboard`, `Paste`, `SendShortcut`, `ClearTextField`, etc.).
   - Parsed by [`ActionController`](file:///c:/Flutter%20Drive/Personal%20Workspace/AutomatedWorkflow/src/automation/action_controller.py) to validate action names and generate system prompts.
4. **Persistent Subprocess Bridge ([`src/automation/ahk_bridge.py`](file:///c:/Flutter%20Drive/Personal%20Workspace/AutomatedWorkflow/src/automation/ahk_bridge.py))**:
   - Spawns and manages a persistent AutoHotkey v2 daemon ([`agent_runner.ahk`](file:///c:/Flutter%20Drive/Personal%20Workspace/AutomatedWorkflow/src/automation/autohotkey/agent_runner.ahk)) that executes batch actions over line-delimited JSON on `stdin`/`stdout`.

---

## 2. Creating a New Workflow

To teach Notch a new capability, create a `.md` file inside [`workflows/`](file:///c:/Flutter%20Drive/Personal%20Workspace/AutomatedWorkflow/workflows) (e.g., `workflows/search_brave.md`).

### Required Structure

Every workflow file must have YAML frontmatter (`name` and `description`) followed by numbered markdown headings with step-by-step instructions:

```markdown
---
name: search_brave
description: Opens the Brave browser, creates a new tab, and searches for user-specified text.
---

# Search the Web in Brave

## 1. Open Brave Browser
Bring Brave Browser to the foreground, launching it if it is not currently open.

## 2. Open a New Tab
Press Ctrl+T to open a new tab.

## 3. Type the Search Query
Type the query requested by the user into the address bar.

## 4. Execute the Search
Press Enter to navigate.
```

### Authoring Guidelines

1. **Clear, Layman English**: Write instructions in plain conversational steps. The LLM translates layman descriptions into atomic action primitives.
2. **Standard Shortcut Terms**: Refer to shortcuts using standard human conventions (`Ctrl+S`, `Ctrl+T`, `Alt+F4`, `Enter`, `Tab`). The LLM translates them to AHK syntax (`^s`, `^t`, `!{F4}`, `{Enter}`, `{Tab}`).
3. **Dynamic User Content**: When the workflow requires user parameters (e.g. text to write, query to search, recipient name), specify that the step uses content provided by Boss.
4. **Prefer Clipboard for Long Text**: Instruct workflows that insert dynamic or multi-line text to paste from clipboard rather than typing character-by-character.
5. **Hot-Reloadable**: Notch rescans [`workflows/`](file:///c:/Flutter%20Drive/Personal%20Workspace/AutomatedWorkflow/workflows) on every request turn. You do not need to restart the application to test a new or edited workflow.

---

## 3. Onboarding a New Application

If your workflow interacts with an application that Notch does not yet recognize:

### Step 1: Update App Registry (`src/automation/autohotkey/apps.ahk`)
Add the window identifier (`WinTitle`) and executable path. Use portable path expansions where applicable:
```ahk
Global App_Slack := "ahk_exe slack.exe"
Global App_Slack_Exec := "C:\Users\username\AppData\Local\slack\slack.exe"
```

### Step 2: Update Manifest (`.agents/context/ahk_manifest.md`)
Add the application to the `## Apps` table:
```markdown
| `App_Slack` | Slack desktop messaging client |
```

---

## 4. Adding a New Action Primitive (If Needed)

If an automation requires a primitive beyond existing controls (`FocusApp`, `TypeText`, `CopyToClipboard`, `Paste`, `SendShortcut`, `ClearTextField`, `ClickAt`, `ToggleVoiceTyping`):

### Step 1: Implement the Function in `src/automation/autohotkey/controls.ahk`
Write an AutoHotkey **v2** function:
```ahk
; Scrolls the active window down or up
ScrollWindow(direction) {
    if (direction = "up") {
        Send("{WheelUp 5}")
    } else {
        Send("{WheelDown 5}")
    }
    Sleep(300)
}
```

### Step 2: Register in `.agents/context/ahk_manifest.md`
Add the function signature to the `## Actions` section:
```markdown
- **`ScrollWindow(direction)`**: Scroll the active window 'up' or 'down'.
```
> [!IMPORTANT]
> `ActionController` uses a regex on `## Actions` (`-\s*\*\*\`?([A-Za-z][A-Za-z0-9_]*)`) to whitelist callable actions. If it is not listed in `ahk_manifest.md`, `ActionController` will reject the action call before dispatching to AHK.

---

## 5. Runtime Execution & Safety Lifecycle

When the user gives an instruction:

```
User Query (Voice or Text)
           │
           ▼
Check against Workflow Catalog
           ├────────────────────────────┐
           │ [No Match]                 │ [Match Found]
           ▼                            ▼
Politely refuse without calling   1. Call read_workflow(workflow_name)
tools; explain available tasks          │
                                        ▼
                                  2. Compile steps to single batch execute_actions
                                        │
                                        ▼
                                  3. ActionController validates whitelist against ahk_manifest.md
                                        │
                                        ▼
                                  4. AHKBridge dispatches via stdin to agent_runner.ahk
                                        │ (Fail-fast: halts if any step fails)
                                        ▼
                                  5. Notch confirms completion aloud to Boss (plain text, no markdown)
```


---
description: Guide for creating automation workflows and onboarding applications to the Notch desktop automation assistant.
---

# AHK Automation & Workflow Authoring Guide

Use this guide when creating a new automation workflow or adding app support for the Notch desktop automation assistant.

## Architecture Overview

Notch uses a simplified, workflow-centric architecture:
1. **Workflows (`workflows/<workflow_name>.md`)**: The single source of truth for procedures. Written in plain layman English with standard human keyboard shortcuts (e.g. `Ctrl+S`, `Enter`, `Alt+F4`).
2. **App Registry (`src/automation/autohotkey/apps.ahk`)**: Central registry defining window titles and executable paths for applications.
3. **AHK Manifest (`.agents/context/ahk_manifest.md`)**: Defines the available AHK action primitives (`FocusApp`, `TypeText`, `CopyToClipboard`, `Paste`, `SendShortcut`, etc.) and the list of known apps.

---

## 1. Creating a New Workflow

To teach Notch a new capability, create a `.md` file in the `workflows/` directory at the project root.

### Format Requirement
Every workflow file must have YAML frontmatter with `name` and `description`, followed by numbered markdown headings with layman instructions:

```markdown
---
name: write_letter
description: Opens Notepad, writes a letter based on user instructions, and saves it.
---

# Write Letter in Notepad

## 1. Open Notepad
Open or switch to Windows Notepad.

## 2. Write the Letter
Type or paste the letter content requested by the user into the document.

## 3. Save the File
Save the document by pressing Ctrl+S.
```

### Authoring Rules
- **Layman Language**: Write instructions in simple conversational steps. Non-technical users should be able to create or edit workflows.
- **Human Shortcuts**: Use human terms like `Ctrl+S`, `Alt+F`, `Enter`, `Win+H`. The LLM automatically converts them to AutoHotkey syntax.
- **Dynamic Content**: If the workflow needs user data (like a message to write, or a search term), instruct the step to use the content provided by the user.
- **Live Reload**: Notch dynamically scans the `workflows/` directory on every request—you do not need to restart Notch to test a new or edited workflow.

---

## 2. Onboarding a New Application (If Needed)

If a workflow targets an application that Notch doesn't know about yet:

### Step A: Update `src/automation/autohotkey/apps.ahk`
Add the app window matcher and executable path:
```ahk
Global App_<Name> := "ahk_exe <ProcessName.exe>"
Global App_<Name>_Exec := "C:\Full\Path\To\executable.exe"
```

### Step B: Update `## Apps` Table in `.agents/context/ahk_manifest.md`
Add a row to the table:
```markdown
| `App_<Name>` | Application description |
```

---

## 3. Execution Model

- When the user speaks or types a request, Notch matches it against the workflow catalog.
- If no workflow matches, Notch politely explains it has not been taught that task yet and lists available workflows. It calls zero tools.
- When a workflow matches:
  1. Notch calls `read_workflow` to load the steps.
  2. The LLM translates the steps into a single batch of `execute_actions`.
  3. Actions run sequentially in AutoHotkey with fail-fast safety (stops immediately if any action fails).
  4. Notch confirms completion conversationally to Boss.

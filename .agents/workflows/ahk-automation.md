---
description: Guide for onboarding a new application to the Notch desktop automation assistant so that the LLM can control it.
---

# AHK Automation Skill - App Onboarding

You are an expert AutoHotkey (AHK) v2 developer and AI automation engineer. Use this skill when the user asks you to add support for a new application to the Notch automation assistant.

## Architecture Context

Notch relies on three key locations to understand and control a new application:
1. **The Python/AHK Manifest (`ahk_manifest.md`)**: Informs the LLM of the app's variable name and description via the system prompt.
2. **The Apps Script (`apps.ahk`)**: Defines the actual AHK `WinTitle` string and executable path.
3. **The Local Knowledge Base (`apps/<Name>.md`)**: Provides the LLM with specific shortcuts and workflows for that application.

## Workflow

When asked to onboard a new app for automation, follow these steps strictly:

### 1. Identify Target App Information
- Ask the user for the following details (if not already provided):
  - **App Name** (e.g., `Spotify`)
  - **Description** (e.g., `Music streaming player`)
  - **Process Name** (e.g., `Spotify.exe`)
  - **Full Path to Executable** (e.g., `C:\Users\Username\AppData\Roaming\Spotify\Spotify.exe`)
- Wait for user approval and details before proceeding.

### 2. Update the AHK Manifest
- **File**: `c:\Flutter Drive\Practice Mode\Responsive Related\workflow\.agents\context\ahk_manifest.md`
- **Action**: Add a new row to the `## Apps` markdown table.
- **Format**: `| App_<Name> | <Description> |`

### 3. Update the Apps Script
- **File**: `c:\Flutter Drive\Practice Mode\Responsive Related\workflow\src\automation\autohotkey\apps.ahk`
- **Action**: Add the global variable definitions for the new app.
- **Format**:
  ```ahk
  Global App_<Name> := "ahk_exe <Process.exe>"
  Global App_<Name>_Exec := "C:\Full\Path\To\app.exe"
  ```
  *(Make sure to use the exact variable name as defined in the manifest.)*

### 4. Create App Instruction File for the LLM
- **File**: `c:\Flutter Drive\Practice Mode\Responsive Related\workflow\.agents\context\apps\<Name>.md`
  - *Important*: The filename must exactly match the `<Name>` part of `App_<Name>` (no `App_` prefix).
- **Action**: Create a new markdown file that teaches the LLM how to navigate and use this app.
- **Format Requirement**: Must contain YAML frontmatter, a `# [<AppName>] Automation Guide` heading, and a Markdown table for shortcuts.
  ```markdown
  ---
  title: <App Name> Automation Guide
  ---

  # <App Name> Automation Guide

  | Shortcut | Description |
  | --- | --- |
  | `^n` | New item (example) |
  | `!f` | Open file menu (example) |
  ```
- *Note:* If you are unaware of the specific shortcuts for the app, provide a basic/empty table structure and inform the user that the Notch agent can dynamically update this file when it learns new shortcuts.

### 5. Verification
- Confirm with the user that the manifest, the `apps.ahk` script, and the app instruction file are all correctly populated.
- Remind the user to restart the Notch application, as the Python backend reads the manifest and `apps.ahk` variables upon startup to build the system prompt for the LLM.

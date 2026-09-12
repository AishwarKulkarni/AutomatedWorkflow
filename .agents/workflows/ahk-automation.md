---
description: Automates the creation of AutoHotkey (AHK) scripts for application automation flows, managing reusable functions and app registrations.
---

# AHK Automation Skill

You are an expert AutoHotkey (AHK) v2 developer. Use this skill when the user asks you to create an automation flow for an application.

## Workflow

When invoked to create an automation script, follow these steps strictly in order:

### 1. Analyze Existing Functions

- **Review**: Analyze the `c:\Flutter Drive\Practice Mode\Responsive Related\workflow\controls.ahk` file.
- **Identify**: Look for existing reusable functions (e.g., `ClickAt`, `FocusApp`, `SendEnter`, `TypeText`) that can be used to fulfill the user's requested automation flow.

### 2. Handle New Function Requirements

- **Assess**: Determine if the requested flow requires a new reusable function that is not currently in `controls.ahk`.
- **Approval**: If a new function is needed, you **MUST** ask the user for approval first before adding it. Do not proceed until the user approves.
- **Implementation**: Once approval is granted, add the new reusable function to `c:\Flutter Drive\Practice Mode\Responsive Related\workflow\controls.ahk`.

### 3. App Registration Check

- **Review**: Check `c:\Flutter Drive\Practice Mode\Responsive Related\workflow\src\autohotkey\apps.ahk` to see if the target application is already registered.
- **Approval**: If the application is NOT listed, ask the user for approval to add it, and ask for the **full path to the executable**.
- **Implementation**: Once approved, add **both** entries to `apps.ahk`:
  - `Global App_<Name> := "ahk_exe <Process.exe>"` — used by `FocusApp`/`WinExist` for window matching.
  - `Global App_<Name>_Exec := "C:\Full\Path\To\app.exe"` — used by `RunApp` to launch the app from disk.

### 4. Create the Automation Script

- **Write**: Create the specific AHK script for the application's automation flow.
- **Location**: Save the new script in the appropriate subdirectory under `c:\Flutter Drive\Practice Mode\Responsive Related\workflow\App List\<AppName>\`.
- **Guidelines**:
  - Rely on the reusable functions from `controls.ahk`.
  - Follow the user's specific instructions for the automation flow.
  - **CRITICAL**: Do NOT add comments to the code unless they are extremely important (per the user's global rule).

### 5. Register in Main Script

- **Review**: Open `c:\Flutter Drive\Practice Mode\Responsive Related\workflow\main.ahk`.
- **Update Includes**: Include the new script in `main.ahk` under the appropriate `#HotIf TargetApp != "" and WinActive(TargetApp)` block. If this is a new app, you may need to add `#Include "App List\<AppName>\<ScriptName>.ahk"`.
- **Update GUI Dropdown**: Ensure the new application variable (e.g., `App_Name`) is added to the `appList` array inside the `SelectAppGui()` function in `main.ahk` so it can be selected from the UI dropdown menu.

## Golden Rules

- **No Unapproved Additions**: Never add to `controls.ahk` or `apps.ahk` without explicit user permission.
- **Code Cleanliness**: No unnecessary comments. Keep the code minimal and functional.

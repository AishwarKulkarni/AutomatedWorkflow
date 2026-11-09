---
name: create-automation
description: Research and create new Notch app usage guides in instructions/, including verified shortcuts, navigation patterns, and safe operating steps.
---

# Notch App Instruction Authoring Guide

Use this guide when the user asks to create a new instruction guide for a desktop application. These files explain how to use a given app: its interface, common tasks, navigation, and shortcuts. They are app reference material, not a list of tasks Notch is authorized to perform. Use `update-instructions` when the user asks to revise an existing guide.

## 1. Check the existing system first

Before writing a guide, identify the exact application and, when relevant, its version, operating system, edition, and desktop or web variant. Inspect:

- Existing files in `instructions/` for app coverage, overlap, naming, and conventions.
- `.agents/context/ahk_manifest.md` for allowed action primitives and app target names.
- `src/automation/autohotkey/apps.ahk` when the requested app might not be registered.
- `src/agent/workflow_manager.py` for the current instruction file metadata and loading contract.

Research the app's keyboard shortcuts deliberately. Verify behavior from authoritative, current sources, prioritizing official app documentation and vendor shortcut references. Note OS-specific differences and distinguish confirmed shortcuts from unverified conventions. Browse when official documentation is not available locally. Name or link sources in the guide. Do not invent shortcuts, controls, or features; omit uncertain claims from operational steps.

Do not claim that an app or action is available unless it appears in the manifest and is implemented. Prefer the existing supported actions and keyboard shortcuts. If the request needs a new app or primitive, make the necessary supporting code and manifest changes as well; describe the limit to the user if it cannot safely be implemented.

## 2. Instruction file contract

Create a new Markdown file under `instructions/`. Use a lowercase snake_case filename based on the app, such as `brave_browser.md` or `notepad.md`. The filename stem should match the guide `name`.

The parser supports simple, single-line `name` and `description` frontmatter. Keep these values on one line and avoid YAML features such as folded or multiline strings.

```markdown
---
name: brave_browser
description: Usage guide for navigating Brave, managing tabs, and using verified browser shortcuts.
---

# Brave Browser Usage Guide

## App and platform
...

## Interface map
...

## Verified shortcuts
...

## Common operations
...

## Safety and recovery
...

## Sources
...
```

The guide should be a practical reference for an agent operating the named app. Describe reusable operations, not just one user-requested task.

## 3. Write a complete app guide

Cover the app and platform/version scope, main interface areas and focus behavior, verified keyboard shortcuts by purpose, detailed reusable operations, text/input handling, safety and recovery cases, and sources with links and platform/version coverage. Explain prerequisites, which view or control must be active, how to reach a feature, and what state should result. Include useful app-specific shortcuts for navigation, editing, search, tabs/windows, save/open, and other core functions. Distinguish app shortcuts from operating-system shortcuts and explain `Ctrl`/`Command` differences. A shortcut list without usage context is insufficient.

Use plain, direct English and concrete steps. Do not assume the agent can inspect UI state unless the available actions support it. Explain where confidence is limited and omit claims that cannot be supported.

### Example of app guide structure

```markdown
---
name: brave_browser
description: Usage guide for navigating Brave and using verified browser shortcuts.
---

# Brave Browser Usage Guide

## App and platform
Brave Browser for Windows (state the researched version scope).

## Interface map
Describe the address bar, tabs, menus, and relevant focus behavior.

## Verified shortcuts
List researched shortcuts with their purpose and source.

## Common operations
Describe reusable app operations with prerequisites and expected states.

## Safety and recovery
Document focus hazards, dialogs, and conditions to stop.

## Sources
Link authoritative app documentation and shortcut references.
```

This example is a structure guide; include only details relevant to the actual workflow.

## 4. Safety and scope

- A guide is reference knowledge; it does not by itself authorize Notch to perform every operation described. Follow the current runtime approval and action-gating rules.
- Start app interaction by focusing the specified registered target. Never assume focus succeeded or send keystrokes after a focus failure.
- Prefer keyboard shortcuts to coordinate clicks. Use `ClickAt` only when the UI has no practical keyboard route, and only when the target and coordinates are stable enough to be safe.
- Keep action sequences bounded to the requested outcome. Do not add extra cleanup, navigation, or content changes that the user did not request.
- Treat sending messages, submitting forms, deleting or overwriting data, purchasing, publishing, and other consequential actions with care. The workflow must not infer recipients, destinations, or irreversible choices. If a consequential choice is ambiguous or not explicitly requested, stop and ask the user.
- The action batch is fail-fast. Once an action fails or the observed state differs from what the next step requires, do not continue issuing dependent actions.
- Never promise a verification method unavailable to the current action set. The system primarily performs keyboard actions; it may not be able to inspect arbitrary UI state.

## 5. Use supported actions accurately

Only direct the agent to use actions listed in `.agents/context/ahk_manifest.md`. The current manifest may include `FocusApp`, `TypeText`, `CopyToClipboard`, `Paste`, `ClickAt`, `SendShortcut`, `ShowMessage`, `ClearMessage`, `ClearTextField`, and `ToggleVoiceTyping`; check the file because this list can change.

Important conventions:

- `FocusApp` requires the registered `target_app` name.
- `TypeText` is for short literal text. Use clipboard plus paste for long text.
- `SendShortcut` takes AHK shortcut syntax at execution time; in workflow prose, write familiar names (`Ctrl+S`, `Alt+F4`, `Enter`).
- `ClickAt` requires coordinates and should be a last resort.
- Pass a manifest app variable such as `App_Notepad` or `App_Brave` as `target_app`; do not invent target names.

## 6. Add application or action support when necessary

### New application

If the workflow requires an unregistered app, add a reliable window matcher and launch executable in `src/automation/autohotkey/apps.ahk`, then document the target in the `## Apps` table in `.agents/context/ahk_manifest.md`. Follow existing AHK v2 patterns and avoid machine-specific paths when a portable or environment-derived path is available. If a dependable launch path or window matcher is unknown, do not guess; explain what information is missing.

### New action primitive

Add a primitive only when the task cannot be safely expressed using existing actions. Implement it in the appropriate AHK v2 control code, register its signature and clear behavior description under `## Actions` in `.agents/context/ahk_manifest.md`, and ensure its arguments match the Python validation and JSON IPC contract. Never place an unimplemented action in a workflow. Follow the repository's fail-fast and window-focus safety rules.

## 7. Keep the instruction catalog and project context accurate

Instruction files live in `instructions/` and are loaded by `workflow_manager.py` (the module name may remain until a separate refactor). Keep descriptions concise and clear about which app the guide covers. A guide provides reference knowledge; follow the runtime's current approval and action-gating rules.

When a change affects features, dependencies, tools, or architectural boundaries, update `CONTEXT.md` as required by the repository's `AGENTS.md`. A guide-only content change normally does not change architecture context.

## 8. Final review

Before finishing, confirm that:

- The guide is in `instructions/` and has valid single-line `name` and `description` frontmatter.
- Its filename and guide name agree and identify the app.
- It documents reusable app operations, interface details, shortcuts, and safety conditions.
- Shortcut claims are sourced, with platform and version differences stated.
- Every named app and action exists in the current manifest/implementation.
- The guide does not imply blanket authorization for app operations or rely on guessed facts.
- Any required app/action support and manifest documentation are included.

Summarize the guide and research sources, and mention any supporting app/action changes. Do not claim runtime verification unless it was actually performed.

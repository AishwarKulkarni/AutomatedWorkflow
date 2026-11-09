---
name: windows_notepad
description: Detailed usage reference for Windows Notepad, including tabs, plain-text editing, search, saving, and verified Windows shortcuts.
---

# Windows Notepad Usage Guide

## App and platform

This guide covers Windows Notepad on Windows 11 and the supported Windows 10 help scope. Notepad is updated independently through Windows, and features/shortcuts vary by app version and rollout. Recent Windows 11 versions add tabs and may add Markdown formatting or other features; do not assume those controls exist on every device. The registered `App_Notepad` target uses `Notepad.exe`.

## Interface map

- **Document area:** Plain-text editor for the active document. In recent Windows 11 releases, Markdown files may expose formatting and preview controls; treat those as version-dependent.
- **Tabs:** Recent Windows 11 versions support multiple open documents in one window. The add-tab button displays `Ctrl+N` in current Microsoft release notes. Settings can control whether files open in tabs or separate windows in some versions.
- **Title/tab indicator:** Shows the file name and, in current versions, an unsaved-changes indicator. Confirm which document is active before editing.
- **Menus and toolbar:** File actions include opening/saving/printing; Edit includes search and editing controls; View/Settings may expose zoom, word wrap, theme, and format features. Exact menu layout depends on version.
- **Open/Save dialogs:** Use these to select paths. Confirm the full destination and any overwrite prompt before proceeding.

## Verified shortcuts

These common Windows editor shortcuts are documented by Microsoft. `Ctrl+N` is also identified as Notepad's add-tab shortcut in current Windows Insider release notes. The app version, keyboard layout, and rollout can affect behavior.

| Shortcut | Effect | Notes |
|---|---|---|
| `Ctrl+N` | Create a new Notepad tab/document in current versions | Microsoft release notes show this on the Add tab control. A previous app version or setting may open a window instead. |
| `Ctrl+S` | Save the active document | A new/untitled document opens Save As; verify the destination. |
| `Ctrl+O` | Open a file | Standard Windows app shortcut; confirm the dialog and exact file before opening. |
| `Ctrl+F` | Find text | Standard Windows app shortcut. Search operates on the active document. |
| `Ctrl+A` | Select all text | Microsoft documents this common app shortcut; keyboard layout/version issues have been reported for some languages. |
| `Ctrl+C` / `Ctrl+X` / `Ctrl+V` | Copy / cut / paste selected text | Standard Windows editing shortcuts. Cutting changes document contents. |
| `Ctrl+Z` | Undo the last edit | Multi-level undo is supported in modern Notepad versions; verify the document state afterward. |
| `Ctrl+P` | Open print | Standard Windows app shortcut; review printer and print settings before printing. |
| `Ctrl+Tab` / `Ctrl+Shift+Tab` | Move to next / previous tab | Common tab navigation; availability depends on current Notepad version. |
| `Ctrl+W` | Close the active tab/window | Standard app behavior, but confirm unsaved changes are protected by a prompt before any close. |

Microsoft's Notepad release notes specifically document `Ctrl+N` for adding a tab and note a `Ctrl+A` conflict fix for some Spanish and Portuguese keyboard layouts. Treat the other common shortcuts as standard Windows app conventions and check the current menu/tooltips if a key does not behave as expected.

## Common operations

### Create a text document

1. Focus `App_Notepad` and confirm the active document/tab.
2. Use `Ctrl+N` to create a new document. If Notepad asks what to do with unsaved content, stop and ask the user; do not discard it.
3. Enter user-provided text exactly. For long or multi-line text, use `CopyToClipboard` followed by `Paste` to preserve formatting and line breaks.
4. Press `Ctrl+S`, then enter the exact user-specified path and filename in Save As.
5. If an overwrite confirmation appears, stop unless the user explicitly authorized replacing that file.

### Open and edit a file

1. Press `Ctrl+O` or use File > Open.
2. Select only the user-specified file; confirm the full path/name before opening.
3. Make only the requested edits. Save with `Ctrl+S` after confirming the active tab is the intended document.
4. If the file type or encoding prompt appears, preserve the existing format unless the user specified a change.

### Find text

Press `Ctrl+F`, enter the exact phrase to find, and review the highlighted match in the active document. Use the Find interface's next/previous controls to navigate. Do not replace text unless requested and the intended replacement scope is clear.

### Work with tabs

Use `Ctrl+N` to create a tab in current versions. Check the tab title before switching or saving. If the version exposes separate windows instead, use the visible File or Settings controls. Do not close tabs to tidy the workspace; a tab may contain unsaved text.

### Print

Use `Ctrl+P` or File > Print. Review the selected printer and preview/page settings before sending a print job. Printing is an external side effect and requires explicit user intent.

## Safety and recovery

- Confirm the active tab and file path before typing, saving, or printing.
- Never dismiss an unsaved-changes prompt by choosing discard. Ask the user what to do.
- Do not select all or replace text unless the correct document and target field are confirmed.
- Do not overwrite an existing file without explicit instruction. Stop at file-exists or encoding dialogs if the correct choice is not known.
- Notepad feature sets change with Store/app updates and Windows rollout. When the visible interface does not match this guide, use its menu/toolbar and report the difference rather than guessing.

## Sources

- [Microsoft Learn: Notepad release notes](https://learn.microsoft.com/windows-insider/release-notes/apps/notepad) — current release details, `Ctrl+N` tab label, and keyboard layout fix; Windows Insider/app rollout scope.
- [Microsoft: Tabs in Notepad begins rolling out to Windows Insiders](https://blogs.windows.com/windows-insider/2023/01/19/tabs-in-notepad-begins-rolling-out-to-windows-insiders/) — tab behavior and its version-dependent introduction.
- [Microsoft Learn: Keyboard interactions for Windows apps](https://learn.microsoft.com/en-us/windows/uwp/design/input/keyboard-interactions) — common app shortcuts such as Save, Find, Print, editing, and tab navigation.
- [Microsoft Support: Help in Notepad](https://support.microsoft.com/en-us/windows/apps/help-in-notepad) — Windows 10/11 scope and Notepad printing/page setup.

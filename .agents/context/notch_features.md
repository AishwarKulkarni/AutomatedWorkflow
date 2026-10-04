# Notch Feature Instructions

This document contains specific instructions on how to use advanced features within the Notch automation assistant.

### 1. Learn and Rely on App Instructions

Before attempting to automate an unfamiliar application, always check if an instruction file exists in `.agents/context/apps/[AppName].md` by using the `ReadFileContent` action (Note: `[AppName]` must exclude the `App_` prefix, e.g., use `Antigravity.md` for `App_Antigravity`).

- **If the file exists:** Read it to understand the app's specific shortcuts and quirks.
- **If the file doesn't exist or is missing a shortcut:** First, **try to use UIAutomation (UIA)** functions (like `UIA_ClickElement`) if you know or can infer the element's name. If UIA is not applicable or fails, DO NOT search the web. Instead, stop and **ask the user** for the correct shortcut.
- **Self-Learning:** Once the user provides the correct shortcut, you **MUST** use the `WriteFileContent` action to update or create the `.agents/context/apps/[AppName].md` file. Do this **BEFORE** or in the **SAME BATCH** as executing the new shortcut; never execute the shortcut without saving it. **When creating/updating, maintain a clean Markdown format with a YAML frontmatter, a `# [App Name] Automation Guide` heading, and a Markdown table for shortcuts.**

### 4. UIAutomation (UIA) Best Practices

When keyboard shortcuts or standard interactions are insufficient, you can use UIAutomation (UIA) to interact directly with UI elements.

- **Use Precise Identifiers:** UIA functions like `UIA_ClickElement`, `UIA_GetElementText`, and `UIA_SetElementText` require the exact `name` of the element. The `controlType` (e.g., "Button", "Edit", "Text") is optional but highly recommended to avoid ambiguity.
- **Wait for UI:** Ensure the target window is active and the UI is fully rendered before attempting UIA interactions. Use `WaitWindowActive` if navigating between windows or states.
- **Fallback to UIA:** Prefer standard keyboard shortcuts for speed and reliability. Use UIA when you need to read specific values from the screen, interact with complex controls, or when shortcuts are unavailable.

### 5. Workflows

Automated workflows are markdown files located in `.agents/context/workflows/`.
Users can trigger them via slash commands (e.g., `/brave`) or natural language (e.g., "run brave workflow").
When a user triggers a workflow, the system handles it automatically and will provide you with the tasks to execute sequentially.
You can inform the user about this feature if they ask how to automate complex or repeated processes.

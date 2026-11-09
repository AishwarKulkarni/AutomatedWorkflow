---
name: chatgpt_desktop
description: Usage reference for the ChatGPT Windows desktop app, including Chat, Work, Codex, projects, recents, and verified Windows shortcuts.
---

# ChatGPT Desktop App Usage Guide

## App and platform

This guide covers the ChatGPT desktop app on Windows, including its Chat, Work, and Codex areas. OpenAI's new desktop app combines these experiences; ChatGPT Classic is a separate older app. The app target registered in this project launches a Windows AppsFolder package associated with Codex, which may update into the new ChatGPT desktop app. Confirm the visible product and mode before entering a prompt. Do not assume a ChatGPT conversation and a Codex conversation share history.

## Interface map

- **Global app switcher/menu:** Select ChatGPT or Codex. Codex has separate history from ChatGPT.
- **Chat / Work toggle:** Within ChatGPT, Chat is for conversational help and Work for task completion and deliverables. Availability can depend on account and workspace access.
- **Recents:** Chat and Work chats appear together; the list can be sorted, filtered, or pinned. Confirm the selected conversation before sending content.
- **Projects:** Keep related chats, files, and instructions together. Starting a Chat or Work conversation from a project carries its context.
- **Codex:** A separate software development view for local folders, repositories, terminals, and developer tools. Local access and actions depend on permissions.
- **Voice:** Available in supported Work and Codex experiences. Microphone, accessibility, or screen/audio permissions may be requested.
- **Built-in browser:** In supported Work/Codex chats, an internal browser has its own state. It is distinct from Brave or the user's Chrome profile.

## Verified shortcuts

The official Windows app documentation identifies `Alt+Space` as the shortcut to open the companion window. The shortcut is configurable in app settings. The release notes describe `Ctrl+K` for chat-history search in an earlier Windows app release; because the desktop navigation has since changed, verify that mapping in the installed version before using it. Do not use web shortcuts as if they were confirmed desktop shortcuts.

| Shortcut | Effect | Notes |
|---|---|---|
| `Alt+Space` | Open the companion window | Windows; configurable. Only use when the companion window is wanted. |
| `Ctrl+K` | Chat-history search in the older documented Windows app | Historical/version-dependent; use the visible Recents search or verify the current mapping first. |
| `Ctrl+Shift+B` | Open the built-in browser in a Work or Codex chat | Current official desktop documentation; browser availability and permissions may vary. |

## Common operations

### Choose the right experience

1. Confirm which product is visible (new ChatGPT, ChatGPT Classic, or Codex app) and identify the active mode.
2. In the new app, select ChatGPT or Codex from the app menu. Within ChatGPT, select Chat or Work.
3. Use the user's explicitly named experience. If the intended mode is unclear, ask before switching or entering content.

### Find or resume a conversation

1. Use Recents and its visible filters or search controls.
2. Confirm the selected title and context before entering a new message.
3. Chat and Work recents are unified, but Codex history remains separate. Do not assume one search or history list covers all areas.

### Work in a project

Open the intended project and confirm its name. Choose Chat or Work from the project according to the user's request. For Codex, confirm the local folder/repository and permissions before asking it to make changes. Only provide files and private content the user intended to share.

### Use the built-in browser

In a Work or Codex chat, press `Ctrl+Shift+B` or use the toolbar control to open the built-in browser. It uses its own browser state, not the Brave/Chrome profile. Review the page and any permission prompt. Browser sign-in, downloads, and web actions require clear user intent.

### Use Voice

Select the Voice control in a supported Work or Codex experience and grant only the required permissions. Voice shortcuts are configured in Settings; do not guess the key combination.

## Safety and recovery

- Confirm product, mode, project, and conversation before sending a prompt. Sending is an external communication action and must match the user's request.
- A task submitted to Codex or Work may access local files or other tools when permitted. Review the scope and permission prompts.
- Do not switch chats, projects, or modes to recover from an unclear state. Stop and ask if the intended destination is uncertain.
- Companion-window, history-search, and browser shortcuts can be changed or version-dependent. Prefer visible controls when behavior is uncertain.
- Avoid confusing Codex with ChatGPT Classic or the new ChatGPT desktop app. Their capabilities and histories differ.

## Sources

- [OpenAI Help: Moving to the new ChatGPT desktop app](https://help.openai.com/en/articles/20001276-moving-to-the-new-chatgpt-desktop-app) — Chat, Work, Codex, app migration, projects, and recents.
- [OpenAI Help: ChatGPT Work and Codex](https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex) — desktop modes, local access, projects, voice, and permissions.
- [OpenAI Help: Using the built-in browser in the ChatGPT desktop app](https://help.openai.com/en/articles/20001277-using-the-built-in-browser-in-the-chatgpt-desktop-app) — Windows `Ctrl+Shift+B` and browser context.
- [OpenAI Help: Windows app release notes](https://help.openai.com/en/articles/10003026-windows-app-release-notes) — Windows companion shortcut and historical search shortcut details.

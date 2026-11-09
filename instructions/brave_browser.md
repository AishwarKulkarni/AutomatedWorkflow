---
name: brave_browser
description: Windows Brave usage and safe desktop web automation workflows using the app's supported keyboard and mouse actions.
---

# Brave Browser Usage Guide

## Scope and automation limits

This guide covers the Brave desktop browser on Windows. The current Notch automation target is `App_Brave`, matched by the `brave.exe` process and launched from the configured Brave executable path. It uses AutoHotkey v2 desktop input; it is not browser-driver automation.

Available automation actions are `FocusApp`, `SendShortcut`, `TypeText`, `CopyToClipboard`, `Paste`, and `ClickAt`. The runtime can report whether an action ran, but it does not read page text, inspect the DOM, locate elements by accessible name or selector, capture browser screenshots, or confirm that a website accepted a click or form value. `ClickAt(x, y)` uses screen coordinates and can break when the window, zoom, layout, banner, or scroll position changes. Use it only when the target is visually confirmed and coordinates are known for the current screen state.

Therefore, prefer simple browser navigation and low-risk tasks with observable checkpoints. For page-specific work, proceed one small step at a time and use the visible browser state to verify the result before continuing. If the page state cannot be observed, the layout is ambiguous, or a step depends on hidden/dynamic content, stop and ask the user to clarify or complete that step. Do not claim a web task succeeded based only on successful keystroke dispatch.

Brave's shortcuts can be customized in **Settings > System > Shortcuts**. Browser extensions, website keyboard handlers, dialogs, and focused text fields may change what a key does. The shortcuts below are the official Windows/Linux mappings; check the live mapping if one behaves differently.

## Interface map

- **Tab strip:** Each tab has independent page/navigation state. Check the selected tab before entering text or closing it.
- **Address bar (omnibox):** Takes a URL or search query. `Ctrl+L` focuses and selects it.
- **Page area:** Contains the active site. A focused form field or embedded editor may intercept browser shortcuts.
- **Main menu:** Browser settings, history, bookmarks, downloads, and other controls.
- **Shields icon:** Shows the current site's protection controls. Per-site changes remain specific to that site.
- **Site information / permissions:** The tune/site-controls icon beside the address can open site settings and permissions.
- **Profiles and private windows:** Separate browser contexts. Private browsing does not make browsing anonymous and may not use the same signed-in session.
- **Downloads and prompts:** Downloads can open or save files; permission, authentication, certificate, and external-app dialogs may interrupt a sequence.

## Supported actions and AHK shortcut notation

`SendShortcut` accepts AutoHotkey key syntax. Common mappings are `^` for Ctrl, `!` for Alt, `+` for Shift, and `#` for the Windows key; for example, `^l` is Ctrl+L, `^+n` is Ctrl+Shift+N, and `{Enter}` presses Enter. Use one shortcut at a time and verify the resulting browser state before relying on it. For longer supplied text, use `CopyToClipboard(text)` followed by `Paste()` rather than a long `TypeText` sequence.

Every browser operation starts with `FocusApp` targeted at `App_Brave`. The AHK `FocusApp` implementation attempts activation and waits for the Brave window to become active; if it fails, stop the workflow. A focus action identifies the app window, not a particular profile, tab, or page, so confirm those separately in the visible UI.

## Verified Windows shortcuts

| Shortcut | Effect | Notes |
|---|---|---|
| `Ctrl+L` / `Alt+D` / `F6` | Focus the address bar | Verify the caret is in the omnibox before typing. |
| `Ctrl+T` | Open a new tab and focus it | Use to preserve the current page. |
| `Ctrl+N` | Open a new window | A normal window. |
| `Ctrl+Shift+N` | Open a private window | Separate private context. |
| `Ctrl+W` / `Ctrl+F4` | Close the current tab | Confirm the active tab first. |
| `Ctrl+Shift+W` | Close the current window | Can close all tabs in that window. |
| `Ctrl+Shift+T` | Reopen the last closed tab | May restore recently closed tabs in sequence. |
| `Ctrl+Tab` / `Ctrl+Shift+Tab` | Next / previous tab | `Ctrl+PgDn` / `Ctrl+PgUp` also work. |
| `Ctrl+1` through `Ctrl+8` | Activate tab 1 through 8 | Count from the left. |
| `Ctrl+9` | Activate the last tab | Regardless of tab count. |
| `Alt+Left` / `Alt+Right` | Back / forward in history | Active tab. |
| `Ctrl+H` / `Ctrl+J` | Open History / Downloads | Opens the corresponding browser page. |
| `Ctrl+F`, `Ctrl+G`, `Ctrl+Shift+G` | Find text; next / previous match | Searches the loaded page, not the web. |
| `Tab` / `Shift+Tab` | Move through focusable page controls | Websites may define their own focus order. |
| `Ctrl+Shift+B` | Show / hide bookmarks bar | Browser window. |
| `Ctrl+Shift+O` | Open Bookmarks Manager | Browser window. |
| `Ctrl+Shift+M` | Open profile menu | Check the selected profile before proceeding. |
| `Shift+Esc` | Open Brave Task Manager | Browser window. |
| `Ctrl+Shift+Delete` | Open Clear Browsing Data options | Review the data types and time range; do not confirm an unrequested clear. |
| `F5` / `Ctrl+R` | Reload the page | Reload may resubmit or lose in-progress page state. |
| `Esc` | Stop page loading / close some browser UI | Effect depends on current focus and state. |
| `Ctrl+0` | Reset page zoom | Other zoom shortcuts are `Ctrl++` and `Ctrl+-`. |
| `F11` | Toggle full screen | Changes the visible layout and coordinate positions. |
| `Alt+F` / `F10` then `Enter` | Open the main menu | Menu labels can vary with locale/version. |

## Reliable web automation workflow

Use this sequence for each browser task:

1. **Match the request to an available guide.** Only automate actions covered by the instruction catalog and the AHK manifest. This guide describes browser operations; it does not authorize arbitrary website actions.
2. **Focus and identify the context.** Call `FocusApp` with `App_Brave`. Confirm visually that the expected Brave window, profile, and tab are active. If not, stop before sending keys.
3. **Navigate using the address bar.** Send `Ctrl+L`, enter the exact URL the user supplied (or the precise search phrase they requested), then send `{Enter}` once. Do not guess URLs, search terms, or destination accounts.
4. **Wait for and inspect the result.** Allow the page to load, then verify the visible domain, page title/content, and any redirect or interstitial. There is no page-ready signal in the current AHK action result. If load status or destination is unclear, stop rather than sending another `Enter` or continuing blindly.
5. **Perform one small, reversible step at a time.** Prefer browser shortcuts and keyboard navigation. Use `Tab`/`Shift+Tab` only when the focus order is visible/understood; use coordinates only for a currently visible, unambiguous target. Avoid long blind action batches on dynamic pages.
6. **Verify after each state change.** Inspect the visible page after navigation, opening a dialog, changing tabs, or submitting a step. A successful AHK action only means the input action was dispatched, not that the website completed the requested operation.
7. **Stop at consequential or unclear steps.** Authentication, CAPTCHA, permission prompts, security warnings, form submission, sending/posting, purchases, booking, account changes, data deletion, downloads, and external-app launches require explicit user intent and a clear target. Ask for clarification if the request does not specify the necessary details. Never approve a prompt or submit a consequential action based on assumptions.

### Navigate to a supplied site

Focus `App_Brave`, confirm the intended window, send `Ctrl+L`, paste/type the exact supplied URL, then send `{Enter}` once. Inspect the resulting domain and page before acting further. If a redirect, certificate warning, sign-in wall, or unexpected destination appears, stop and report it.

### Search the web

Focus the browser and use `Ctrl+L`; enter the user's exact search query and press `{Enter}` once. Inspect the results page and domain before opening any result. Do not assume the top result is trustworthy or relevant. Opening a result is a separate navigation step and must be verified.

### Work with tabs

Use `Ctrl+T` to create a tab and `Ctrl+Tab` / `Ctrl+Shift+Tab` or `Ctrl+1`–`Ctrl+9` to switch. Confirm the visible active tab before typing. Use `Ctrl+Shift+T` to restore an accidentally closed tab only when that is the intended recovery. Before `Ctrl+W` or closing a window, check for unsaved work and confirm the tab/window being closed.

### Find text on the current page

Use `Ctrl+F`, enter a short phrase, and inspect the highlighted match. Use `Ctrl+G` for the next match and `Ctrl+Shift+G` for the previous match; press `Esc` to close the find bar. This does not search other pages or guarantee that all page content has loaded.

### Handle a site that appears broken

Brave Shields can affect site behavior. Inspect the Shields panel and the page's visible error first. Do not globally weaken protections. Changing site-specific Shields settings or permissions changes the browser's privacy/security posture; do so only when explicitly requested, for the correct domain, and after reviewing what setting is being changed. Recheck the site after any approved change.

### Downloads and browser prompts

Open Downloads with `Ctrl+J` to inspect an existing download. Before activating a download link, verify the site, exact file, and user intent. Do not open/run downloaded files or accept external-app launches based only on a browser prompt. Review permission prompts (camera, microphone, location, notifications, clipboard, file/device access) and security warnings; stop for user direction instead of granting access automatically.

### Forms and page actions

Page layout, validation, and focus order vary by site. Do not fill or submit a form unless the user supplied the content and requested that operation. Before submission, verify each visible field and the destination/account. Sending messages, publishing content, placing orders, making reservations, or changing account data is a consequential action: require explicit intent and stop if any detail or final state is uncertain. After an authorized submission, inspect the visible confirmation before reporting completion.

## Safety and recovery

- Never send keystrokes unless Brave has been focused and the intended window/context is confirmed.
- A webpage, text field, popup, browser dialog, or extension can intercept a shortcut. Reconfirm focus after a context switch.
- Do not chain page-specific actions based on assumed timing. The automation layer has fixed short delays and no page-load or element-ready checks.
- If an action's effect is uncertain, inspect the UI before retrying. Repeating `Enter`, clicking again, or resubmitting can cause duplicate actions.
- Use `ClickAt` only when the target is visible and coordinates are verified for the current screen layout; do not infer coordinates from old screenshots or a different resolution/zoom.
- Avoid destructive browser actions (clearing data, removing bookmarks, closing windows) unless clearly requested and the target is confirmed.
- Private browsing does not guarantee anonymity and should not be used to bypass an account, access, or policy restriction.
- Stop if the active profile, tab, domain, user account, prompt, or result cannot be identified reliably.

## Sources

- [Brave Help Center: What keyboard shortcuts can I use in Brave?](https://support.brave.app/hc/en-us/articles/360032272171-What-keyboard-shortcuts-can-I-use-in-Brave) — Windows/Linux shortcuts and customization.
- [Brave Help Center: How do I change site permissions?](https://support.brave.app/hc/en-us/articles/360018205431-How-do-I-change-site-permissions) — global and per-site permissions.
- [Brave Help Center: How do I configure global and site-specific Shields settings?](https://support.brave.app/hc/en-us/articles/360023646212-How-do-I-configure-global-and-site-specific-Shields-settings) — Shields controls and site-specific behavior.

---
app_name: "Brave Browser"
executable: "brave.exe"
---
# Brave Browser Automation Guide

## Keyboard Shortcuts
| Task | Shortcut | Notes |
|---|---|---|
| New Tab | `^t` | Wait 200ms |
| Close Tab | `^w` | |
| New Window | `^n` | Wait 500ms |
| New Incognito Window | `^+n` | Wait 500ms |
| Focus Address Bar | `^l` or `!d` | Use this to type a URL and hit Enter |
| Reload Page | `^r` | |
| Hard Reload Page | `^+r` | |
| Go Back | `!{Left}` | Alt + Left Arrow |
| Go Forward | `!{Right}` | Alt + Right Arrow |
| Switch to Next Tab | `^{Tab}` | |
| Switch to Previous Tab | `^+{Tab}` | |
| Open Developer Tools | `^+i` or `{F12}` | Wait 1000ms |
| Zoom In | `^{NumpadAdd}` or `^+{+}` | |
| Zoom Out | `^{NumpadSub}` or `^-` | |
| Reset Zoom | `^0` | |
| Find in Page | `^f` | Wait 200ms |

## Common Workflows
- **Navigate to a URL:** Press `^l`, wait 100ms, type URL (e.g., `SendKeys, https://example.com{Enter}`), wait for page load (approx 2000ms).
- **Search on Web:** Press `^l`, wait 100ms, type query and `{Enter}`.
- **Inspect Element:** Press `^+c`, wait 500ms, click on the element.
- **Switch Tab and Refresh:** Press `^{Tab}` to move to the next tab, then press `^r` to refresh.
- **Open Settings:** Focus address bar `^l`, type `brave://settings{Enter}`.
- **Clear Browsing Data:** Press `^+{Delete}`, wait 500ms for modal to appear.

## UI Quirks / Gotchas
- The main webpage content area can have deeply nested and complex UIA trees that can be very slow to parse; relying on keyboard shortcuts is often much faster and more reliable than UIA automation.
- Brave Shields (ad and tracker blocker) might block certain page elements or scripts; this can affect automation flows interacting with specific websites.
- Native popups or dialogs (like download prompts, location permissions) can steal focus and may require UIA interaction to dismiss, as standard web shortcuts won't work on them.
- If DevTools are open, they might trap focus. Ensure focus is explicitly moved back to the main document body if needed.

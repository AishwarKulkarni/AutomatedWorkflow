#Requires AutoHotkey v2.0

; Clicks at a specific coordinate and waits briefly
ClickAt(x, y) {
    Click(x, y)
    Sleep(500)
}

; Toggles Windows Voice Typing (Win + H)
ToggleVoiceTyping() {
    Send("#h")
    Sleep(500)
}

; Sends a keyboard shortcut
SendShortcut(shortcut) {
    Send(shortcut)
    Sleep(500)
}

; Shows a tooltip message
ShowMessage(msg) {
    CoordMode("ToolTip", "Screen")
    ToolTip(msg, 0, A_ScreenHeight)
    Sleep(500)
}

; Clears the tooltip
ClearMessage() {
    ToolTip()
    Sleep(500)
}


; Copies the given data to the clipboard
CopyToClipboard(data) {
    if (data = "")
        return
    A_Clipboard := ""
    A_Clipboard := data
    ClipWait(2)
    Sleep(500)
}

; Pastes the current clipboard content
Paste() {
    Send("^v")
    Sleep(500)
}

; Brings the target application to the foreground, launching it if necessary
FocusApp() {
    global TargetApp, TargetExec
    if !WinActive(TargetApp) {
        if !WinExist(TargetApp) {
            if (TargetExec = "") {
                ShowMessage("Error: No _Exec path defined for: " TargetApp)
                SetTimer(ClearMessage, -3000)
                return false
            }
            try {
                Run(TargetExec)
            } catch {
                ShowMessage("Error: Could not launch " TargetExec)
                SetTimer(ClearMessage, -3000)
                return false
            }
            if !WinWait(TargetApp, , 10) {
                ShowMessage("Error: Application did not start in time.")
                Sleep(3000)
                ClearMessage()
                return false
            }
            WinActivate(TargetApp)
        } else {
            if (WinGetMinMax(TargetApp) = -1) {
                WinRestore(TargetApp)
            }
            WinActivate(TargetApp)
        }
        if !WinWaitActive(TargetApp, , 2) {
            ShowMessage("Error: Could not activate target application.")
            Sleep(3000)
            ClearMessage()
            return false
        }
    }
    Sleep(500)
    return true
}

ClearTextField() {
    oldClip := A_Clipboard
    A_Clipboard := ""
    Send("^a^c")

    if (ClipWait(0.5) && Trim(A_Clipboard) != "") {
        Send("{Backspace}")
        Sleep(500)
    } else {
        Send("{Right}")
    }

    A_Clipboard := oldClip
    Sleep(500)
}

ReadFileContent(filePath) {
    if !FileExist(filePath) {
        return ""
    }
    return FileRead(filePath)
}

WriteFileContent(filePath, content) {
    SplitPath(filePath, , &dir)
    if (dir != "" && !DirExist(dir)) {
        DirCreate(dir)
    }
    if FileExist(filePath) {
        FileDelete(filePath)
    }
    FileAppend(content, filePath, "UTF-8")
    return true
}

; Types literal text
TypeText(text) {
    SendText(text)
    Sleep(500)
}
#Requires AutoHotkey v2.0

; Clicks at a specific coordinate and waits briefly
ClickAt(x, y) {
    Click(x, y)
    Sleep(100)
}

; Toggles Windows Voice Typing (Win + H)
ToggleVoiceTyping() {
    Send("#h")
}

; Sends the Enter key
SendEnter() {
    Send("{Enter}")
}

; Shows a tooltip message
ShowMessage(msg) {
    CoordMode("ToolTip", "Screen")
    ToolTip(msg, 0, A_ScreenHeight)
}

; Clears the tooltip
ClearMessage() {
    ToolTip()
}

; Sends the Tab key
SendTab() {
    Send("{Tab}")
}

; Types the given text
TypeText(text) {
    SendText(text)
}

; Brings the target application to the foreground
FocusApp(targetApp) {
    if !WinActive(targetApp) {
        if WinExist(targetApp) {
            if (WinGetMinMax(targetApp) = -1) {
                WinMaximize(targetApp)
            }
            WinActivate(targetApp)
        } else {
            if !WinWait(targetApp, , 10) {
                ShowMessage("Error: Application did not start in time.")
                Sleep(3000)
                ClearMessage()
                return false
            }
            WinActivate(targetApp)
        }
        if !WinWaitActive(targetApp, , 2) {
            ShowMessage("Error: Could not activate target application.")
            Sleep(3000)
            ClearMessage()
            return false
        }
    }
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
    Sleep(200)
}

ReadFileContent(filePath) {
    if !FileExist(filePath) {
        return ""
    }
    return FileRead(filePath)
}

RunApp(targetApp) {
    content := ReadFileContent(A_ScriptDir "\apps.ahk")
    if (content = "") {
        ShowMessage("Error: apps.ahk not found or empty.")
        SetTimer(ClearMessage, -3000)
        return false
    }

    if InStr(content, targetApp) {
        exeName := StrReplace(targetApp, "ahk_exe ", "")
        try {
            Run(exeName)
            return true
        } catch {
            ShowMessage("Error: Could not launch " exeName)
            SetTimer(ClearMessage, -3000)
            return false
        }
    } else {
        ShowMessage("Error: Application not listed in apps.ahk")
        SetTimer(ClearMessage, -3000)
        return false
    }
}
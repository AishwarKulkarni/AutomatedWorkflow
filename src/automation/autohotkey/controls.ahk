#Requires AutoHotkey v2.0
#Include libraries/UIA.ahk

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

; --- UIA Functions ---

; Gets the active TargetApp window as a UIA element
_GetTargetAppUIA() {
    global TargetApp
    if (TargetApp = "")
        return UIA.ElementFromHandle(WinActive("A"))
    
    ; Focus the app first
    FocusApp()
    return UIA.ElementFromHandle(WinExist(TargetApp))
}

; Wait for the target window to be active
WaitWindowActive(winTitle := "", timeoutSec := 5) {
    global TargetApp
    target := (winTitle != "") ? winTitle : TargetApp
    if (target = "")
        target := "A" ; Active window
    
    if WinWaitActive(target, , timeoutSec)
        return true
    return false
}

; Clicks an element by name and optional control type
UIA_ClickElement(name, controlType := "", timeoutMs := 5000) {
    try {
        el := _GetTargetAppUIA()
        if !el
            return false
        
        condition := {Name: name, MatchMode: "Exact"}
        if (controlType != "")
            condition.Type := controlType
        
        foundEl := el.WaitElement(condition, timeoutMs)
        if !foundEl
            return false
            
        foundEl.Click()
        Sleep(500)
        return true
    } catch {
        return false
    }
}

; Gets the text/value of an element
UIA_GetElementText(name, controlType := "", timeoutMs := 5000) {
    try {
        el := _GetTargetAppUIA()
        if !el
            return ""
        
        condition := {Name: name, MatchMode: "Exact"}
        if (controlType != "")
            condition.Type := controlType
            
        foundEl := el.WaitElement(condition, timeoutMs)
        if !foundEl
            return ""
            
        val := foundEl.Value
        if (val = "")
            val := foundEl.Name
        return val
    } catch {
        return ""
    }
}

; Sets the text of an element (usually an Edit control)
UIA_SetElementText(name, text, controlType := "", timeoutMs := 5000) {
    try {
        el := _GetTargetAppUIA()
        if !el
            return false
        
        condition := {Name: name, MatchMode: "Exact"}
        if (controlType != "")
            condition.Type := controlType
            
        foundEl := el.WaitElement(condition, timeoutMs)
        if !foundEl
            return false
            
        foundEl.Value := text
        Sleep(500)
        return true
    } catch {
        return false
    }
}
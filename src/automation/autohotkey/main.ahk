#Requires AutoHotkey v2.0

; --- Master Script ---
; This script runs in the background and loads all your other scripts.

#Include "apps.ahk"

SetTitleMatchMode(2)

Global TargetApp := ""

SelectAppGui() {
    global TargetApp
    myGui := Gui("+AlwaysOnTop", "Select Target App")
    myGui.Add("Text", , "Select or enter the target application:")

    appList := [App_Antigravity, App_Opencode, App_Agy, App_Notepad]
    appInput := myGui.Add("ComboBox", "w250 Choose1", appList)

    BtnOK_Click(btn, info) {
        TargetApp := appInput.Text
        myGui.Destroy()
    }

    myGui.Add("Button", "w80 x85 Default", "OK").OnEvent("Click", BtnOK_Click)
    myGui.Show()
    WinWaitClose("Select Target App")
}

SelectAppGui()

#Include "hotkey_scripts\AddPrompt.ahk"

; Press Escape to instantly terminate the automation script
Esc:: ExitApp()
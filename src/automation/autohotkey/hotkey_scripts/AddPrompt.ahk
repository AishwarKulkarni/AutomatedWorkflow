#Requires AutoHotkey v2.0
#Include "..\controls.ahk"

global IsVoiceRecording := false

; Press ` to start, press ` again to stop and send.
ToggleVoiceRecording(FocusCallback?) {
    global IsVoiceRecording

    if (!IsVoiceRecording) {
        if IsSet(FocusCallback) {
            FocusCallback()
        }

        ; 2. Start dictation
        IsVoiceRecording := true
        ToggleVoiceTyping()
        ShowMessage("Voice Chat Active... Press `` to send.")
    } else {
        ; 3. Stop dictation
        IsVoiceRecording := false
        ToggleVoiceTyping()
        ClearMessage()
        Sleep(500) ; wait slightly for text to be committed

        ; 4. Press Enter to send the message in Antigravity
        SendShortcut("{Enter}")
    }
}

`:: ToggleVoiceRecording()
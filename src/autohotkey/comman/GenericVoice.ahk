#Requires AutoHotkey v2.0
#Include "..\controls.ahk"

global IsVoiceRecording := false

StartVoiceRecording(msg := "🎤 Dictation Active...") {
    global IsVoiceRecording
    if (!IsVoiceRecording) {
        IsVoiceRecording := true
        ToggleVoiceTyping()
        ShowMessage(msg)
    }
}

StopVoiceRecording() {
    global IsVoiceRecording
    if (IsVoiceRecording) {
        IsVoiceRecording := false
        ToggleVoiceTyping()
        Sleep(500)
        ClearMessage() 
    }
}

ToggleGenericVoice(msg := "🎤 Dictation Active...") {
    global IsVoiceRecording
    if (!IsVoiceRecording) {
        StartVoiceRecording(msg)
        return true
    } else {
        StopVoiceRecording()
        return false
    }
}

#Requires AutoHotkey v2.0
#Include "..\controls.ahk"
#Include "..\comman\GenericVoice.ahk"

; Press ` to start, press ` again to stop and send.
ToggleVoiceRecording(FocusCallback?) {
    global IsVoiceRecording

    if (!IsVoiceRecording) {
        if IsSet(FocusCallback) {
            FocusCallback()
        }

        ; 2. Start dictation
        StartVoiceRecording("Voice Chat Active... Press `` to send.")
    } else {
        ; 3. Stop dictation
        StopVoiceRecording()

        ; 4. Press Enter to send the message in Antigravity
        SendEnter()
    }
}
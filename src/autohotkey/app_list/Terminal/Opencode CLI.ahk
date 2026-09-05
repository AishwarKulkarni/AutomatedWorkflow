#Requires AutoHotkey v2.0
#Include "..\..\controls.ahk"
#Include "..\..\apps.ahk"
#Include "..\..\comman\GenericVoice.ahk"
#Include "..\..\comman\AddPrompt.ahk"

; Backtick: Start voice recording with focus callback
`:: ToggleVoiceRecording()

; Helper function to focus the app and prepare the chat
PrepareOpencodeChat(
    focusTargetApp := false,
    createNewChat := '',
    setSkill := "",
    skillName := "",
    additionalText := "",
    useVoice := false
) {
    global App_Opencode

    if (focusTargetApp) {
        if (!FocusApp(App_Opencode)) {
            return
        }
        Sleep(200)
    }

    if (createNewChat != "") {
        TypeText(createNewChat)
        Sleep(500)
        Send("{Enter}")
        Sleep(500)
    }

    if (setSkill != "") {
        TypeText(setSkill)
        Sleep(500)
        Send("{Enter}")
        Sleep(500)
        TypeText(skillName)
        Sleep(500)
        Send("{Enter}")
        Sleep(500)
    }

    if (additionalText != "") {
        TypeText(additionalText)
        Sleep(100)
        Send("{Space}")
    }

    if (useVoice) {
        StartVoiceRecording("Voice Chat Active... Press `` to stop and send.")
    } else {
        Sleep(200)
        Send("{Enter}")
    }
}

; Backtick + 1: Start /grilling flow
` & 1:: {
    PrepareOpencodeChat(
        true,        ; focusTargetApp
        '',          ; createNewChat
        "/skill",    ; addSkill
        "grilling",  ; skillName
        "",
        true         ; useVoice
    )
    ShowMessage("Action: /grilling started...")
}

; Backtick + 2: Start /to-spec flow
` & 2:: {
    PrepareOpencodeChat(
        true,        ; focusTargetApp
        '/new',      ; createNewChat
        "/skill",    ; addSkill
        "to-spec",   ; skillName
        "",
        true         ; useVoice
    )
    ShowMessage("Action: /to-spec started...")
}

; Backtick + 3: Start /to-tickets flow
` & 3:: {
    PrepareOpencodeChat(
        true,        ; focusTargetApp
        '/new',      ; createNewChat
        "/skill",    ; addSkill
        "to-tickets", ; skillName
        "Please base the tickets on the spec file created in the previous step.",
        false       ; useVoice
    )
    ShowMessage("Action: /to-tickets started...")
}

; Backtick + 4: Start /implement flow
` & 4:: {
    PrepareOpencodeChat(
        true,        ; focusTargetApp
        '/new',      ; createNewChat
        "/skill",    ; addSkill
        "implement", ; skillName
        "implement the tickets created in last step and make sure to implement them parallely whenever they are 'unblocked' and 'ready for agent' start working on them",
        false        ; useVoice
    )
    ShowMessage("Action: /implement started...")
}
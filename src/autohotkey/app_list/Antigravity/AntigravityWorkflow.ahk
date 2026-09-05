#Requires AutoHotkey v2.0
#Include "..\..\controls.ahk"
#Include "..\..\apps.ahk"
#Include "..\..\comman\GenericVoice.ahk"
#Include "..\..\comman\AddPrompt.ahk"

FocusAgyChat() {
    ; Click inside the Antigravity chat text field
    ClickAt(1776, 937)
    Sleep(1000)
}

; Backtick: Start voice recording with focus callback
`:: ToggleVoiceRecording(FocusAgyChat)

; Helper function to focus the app and prepare the chat
PrepareAgyIDEChat(
    focusTargetApp := true,
    createNewChat := true,
    newChatShortcut := "",
    commandStr := "",
    additionalText := "",
    useVoice := true
) {
    global App_Antigravity

    if (focusTargetApp) {
        if (!FocusApp(App_Antigravity)) {
            return
        }
        Sleep(200)
    }

    if (createNewChat) {
        Send(newChatShortcut)
        Sleep(500)
        ClearTextField()
        Sleep(500)
    }

    if (commandStr != "") {
        TypeText(commandStr)
        Sleep(1000)
        SendTab()
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
    PrepareAgyIDEChat(
        true,        ; focusTargetApp
        true,        ; createNewChat
        "^+l",       ; newChatShortcut
        "/grilling",
        "",
        true         ; useVoice
    )
    ShowMessage("Action: /grilling started...")
}

; Backtick + 2: Start /to-spec flow
` & 2:: {
    PrepareAgyIDEChat(
        true,       ; focusTargetApp
        true,       ; createNewChat
        "^l",      ; newChatShortcut
        "/to-spec",
        "",
        false        ; useVoice
    )
    ShowMessage("Action: /to-spec started...")
}

; Backtick + 3: Start /to-tickets flow
` & 3:: {
    PrepareAgyIDEChat(
        true,       ; focusTargetApp
        true,       ; createNewChat
        "^+l",      ; newChatShortcut
        "/to-tickets",
        "Please base the tickets on the spec file created in the previous step.",
        false       ; useVoice
    )
    ShowMessage("Action: /to-tickets started...")
}

; Backtick + 4: Start /implement flow
` & 4:: {
    PrepareAgyIDEChat(
        true,        ; focusTargetApp
        true,        ; createNewChat
        "^+l",       ; newChatShortcut
        "/implement",
        "implement the tickets created in last step and make sure to implement them one by one whenever they are unblocked and ready for agent start working on them",
        false         ; useVoice
    )
    ShowMessage("Action: /implement started...")
}
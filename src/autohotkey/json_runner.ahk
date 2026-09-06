#Requires AutoHotkey v2.0
#Include controls.ahk
#Include libraries/JSON.ahk

SetWorkingDir A_InitialWorkingDir

if (A_Args.Length < 1) {
    ShowMessage("Error: No JSON file provided.")
    ExitApp(1)
}

jsonFile := A_Args[1]

if !FileExist(jsonFile) {
    ShowMessage("Error: JSON file not found - " . jsonFile)
    ExitApp(1)
}

content := FileRead(jsonFile)
try {
    tasks := JSON.parse(content)
} catch as err {
    ShowMessage("Error parsing JSON: " . err.Message)
    ExitApp(1)
}

for index, task in tasks {
    action := task["action"]
    args := task.Has("args") ? task["args"] : []

    try {
        fn := %action%
        if (Type(fn) = "Func") {
            try {
                fn(args*)
            } catch as err {
                ShowMessage("Error executing " action ": " err.Message)
            }
        } else {
            ShowMessage("Action is not a function: " . action)
        }
    } catch {
        ShowMessage("Unknown action: " . action)
    }
    Sleep(500) ; Small delay between actions
}

ExitApp(0)
#Requires AutoHotkey v2.0
#Include controls.ahk
#Include apps.ahk
#Include libraries/JSON.ahk

; ─────────────────────────────────────────────────────────────────────────────
; agent_runner.ahk — Persistent stdin/stdout JSON command loop.
;
; Python sends one JSON command per line on stdin:
;   { "action": "TypeText", "args": ["Hello"], "target_app": "App_Notepad" }
;
; AHK writes one JSON result per line to stdout:
;   { "success": true, "output": "", "error": "", "duration_ms": 42 }
;
; The process stays alive for the whole session; Python restarts it on crash.
; ─────────────────────────────────────────────────────────────────────────────

SetWorkingDir(A_InitialWorkingDir)

; Persistent globals used by control functions that reference TargetApp/TargetExec
global TargetApp := ""
global TargetExec := ""

; Open stdin for reading and stdout for writing (UTF-8)
stdin := FileOpen("*", "r", "UTF-8")
stdout := FileOpen("*", "w", "UTF-8")

if (!IsObject(stdin) || !IsObject(stdout)) {
    ExitApp(1)
}

; ── Main loop ────────────────────────────────────────────────────────────────
loop {
    ; ReadLine blocks until a complete \n-terminated line arrives.
    ; Returns "" on EOF (pipe closed by Python → orderly shutdown).
    line := stdin.ReadLine()
    if (line = "") {
        break   ; EOF — exit cleanly
    }

    line := Trim(line, " `t`r`n")
    if (line = "") {
        continue
    }

    ; ── Parse command ────────────────────────────────────────────────────────
    startMs := A_TickCount
    cmd := ""
    try {
        cmd := JSON.parse(line)
    } catch as parseErr {
        _WriteResult(stdout, false, "", "JSON parse error: " parseErr.Message, A_TickCount - startMs)
        continue
    }

    ; ── Resolve target_app → global TargetApp / TargetExec ──────────────────
    TargetApp := ""
    TargetExec := ""
    if (cmd.Has("target_app") && cmd["target_app"] != "") {
        rawTarget := cmd["target_app"]
        ; Dereference the AHK variable name (e.g. "App_Notepad" → window title string)
        if IsSet(%rawTarget%) {
            TargetApp := %rawTarget%
        } else {
            TargetApp := rawTarget   ; fall back to literal string if not a known var
        }
        execVar := rawTarget "_Exec"
        if IsSet(%execVar%) {
            TargetExec := %execVar%
        }
    }

    ; ── Dispatch action ──────────────────────────────────────────────────────
    if (!cmd.Has("action") || cmd["action"] = "") {
        _WriteResult(stdout, false, "", "Missing 'action' field in command", A_TickCount - startMs)
        continue
    }

    actionName := cmd["action"]
    args := cmd.Has("args") ? cmd["args"] : []

    ; Resolve action name to a function reference — unknown names are caught here
    fn := ""
    try {
        fn := %actionName%
    } catch {
        _WriteResult(stdout, false, "", "Unknown action: " actionName, A_TickCount - startMs)
        continue
    }

    if (Type(fn) != "Func") {
        _WriteResult(stdout, false, "", "'" actionName "' is not a callable function", A_TickCount - startMs)
        continue
    }

    ; Call the action, capturing any non-empty return value as output
    output := ""
    try {
        retVal := fn(args*)
        if (retVal != "" && retVal != 0 && retVal != false) {
            output := String(retVal)
        }
        _WriteResult(stdout, true, output, "", A_TickCount - startMs)
    } catch as execErr {
        _WriteResult(stdout, false, "", "Error in " actionName ": " execErr.Message, A_TickCount - startMs)
    }
}

ExitApp(0)

; ── Helper: serialise and flush a result line to stdout ──────────────────────
_WriteResult(fileObj, success, output, error, duration_ms) {
    result := Map(
        "success", success ? JSON.true : JSON.false,
        "output", output,
        "error", error,
        "duration_ms", duration_ms
    )
    fileObj.WriteLine(JSON.stringify(result, 0))
    fileObj.Read(0)   ; flush — forces buffered data to reach Python immediately
}
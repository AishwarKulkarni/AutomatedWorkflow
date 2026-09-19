#Requires AutoHotkey v2.0

; Define all your target applications here.
; Each app needs two entries:
;   App_<Name>       := WinTitle string used by FocusApp / WinExist for window matching.
;   App_<Name>_Exec  := Full path to the executable, used by FocusApp to launch the app.

Global App_Antigravity := "ahk_exe Antigravity IDE.exe"
Global App_Antigravity_Exec := "C:\Users\DevAdmin\AppData\Local\Programs\Antigravity IDE\Antigravity IDE.exe"

Global App_Notepad := "ahk_exe Notepad.exe"
Global App_Notepad_Exec := "C:\Windows\System32\notepad.exe"

; CMD-based launchers — _Exec points to the actual launcher, not cmd.exe
Global App_Terminal := "ahk_exe WindowsTerminal.exe"
Global App_Terminal_Exec := "wt.exe"

Global App_Brave := "ahk_exe brave.exe"
Global App_Brave_Exec := "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"


Option Explicit
Dim fso, shell, scriptDir, target, iconPath, workingDir, shortcutPath

Set fso   = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

' Determine the directory where this script resides
scriptDir   = fso.GetParentFolderName(WScript.ScriptFullName)

' Set the batch file to run.  This assumes launch_epw_visualizer.bat is in the same
' directory as the VBS script.
target      = fso.BuildPath(scriptDir, "launch_epw_visualizer.bat")

' Set the icon file to use for the shortcut.  The generated icon should also be in
' the same directory and called EPWVisualizer.ico.
iconPath    = fso.BuildPath(scriptDir, "EPWVisualizer.ico")

workingDir  = scriptDir
shortcutPath = shell.SpecialFolders("Desktop") & "\EPW Visualiser.lnk"

Dim lnk
Set lnk = shell.CreateShortcut(shortcutPath)
lnk.TargetPath       = target
lnk.IconLocation     = iconPath
lnk.WorkingDirectory = workingDir
lnk.WindowStyle      = 1 ' normal window
lnk.Description      = "Launch the EPW Data Visualiser"
lnk.Save

WScript.Echo "Shortcut created: " & shortcutPath
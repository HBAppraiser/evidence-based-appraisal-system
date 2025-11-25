# Create Desktop shortcut to C:\MarketReport\Launch_Report.bat
$TargetPath = "C:\MarketReport\Launch_Report.bat"
$ShortcutPath = Join-Path ([Environment]::GetFolderPath("Desktop")) "Market Report Generator.lnk"
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = "C:\MarketReport"
$Shortcut.IconLocation = "$TargetPath,0"
$Shortcut.Save()
Write-Host "Shortcut created on Desktop."

$desktop = [Environment]::GetFolderPath([Environment+SpecialFolder]::Desktop)
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$vbsPath = Join-Path $projectDir "StartBot.vbs"
$iconPath = Join-Path $projectDir "app_icon.ico"
$shortcutPath = Join-Path $desktop "Bing Rewards Bot.lnk"

$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut($shortcutPath)
$s.TargetPath = "wscript.exe"
$s.Arguments = "`"$vbsPath`""
$s.WorkingDirectory = $projectDir
$s.IconLocation = "$iconPath, 0"
$s.Description = "Bing Rewards Bot v8.1 (Edge Native Edition)"
$s.Save()

Write-Host "[OK] Da tao thanh cong bieu tuong Bing Rewards Bot tren Desktop!" -ForegroundColor Green

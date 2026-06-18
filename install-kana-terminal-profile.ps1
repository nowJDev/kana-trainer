# Windows Terminal에 Kana Trainer 전용 프로필을 설치한다.
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$profileName = "Kana Trainer"
$profileGuid = "{d648d711-bcb8-4d92-9f13-4f6f6f890f6a}"
$settingsCandidates = @(
    "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json",
    "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe\LocalState\settings.json"
)

$settingsPath = $settingsCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $settingsPath) {
    throw "Windows Terminal settings.json을 찾을 수 없습니다. Windows Terminal 설치 후 다시 실행하세요."
}

$backupPath = "$settingsPath.kana-trainer.bak"
Copy-Item -LiteralPath $settingsPath -Destination $backupPath -Force

$settings = Get-Content -LiteralPath $settingsPath -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $settings.profiles) {
    $settings | Add-Member -MemberType NoteProperty -Name profiles -Value ([pscustomobject]@{})
}
if (-not $settings.profiles.list) {
    $settings.profiles | Add-Member -MemberType NoteProperty -Name list -Value @()
}

$commandLine = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File `"$projectRoot\start-kana-trainer.ps1`""
$startingDirectory = $projectRoot
$profile = [pscustomobject]@{
    guid = $profileGuid
    name = $profileName
    commandline = $commandLine
    startingDirectory = $startingDirectory
    font = [pscustomobject]@{
        face = "Cascadia Mono"
        size = 50
    }
}

$updated = $false
$newList = @()
foreach ($item in $settings.profiles.list) {
    if ($item.name -eq $profileName -or $item.guid -eq $profileGuid) {
        $newList += $profile
        $updated = $true
    } else {
        $newList += $item
    }
}
if (-not $updated) {
    $newList += $profile
}
$settings.profiles.list = $newList

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$json = $settings | ConvertTo-Json -Depth 100
[System.IO.File]::WriteAllText($settingsPath, $json, $utf8NoBom)

Write-Host "Kana Trainer Windows Terminal 프로필을 설치했습니다."
Write-Host "설정 파일: $settingsPath"
Write-Host "백업 파일: $backupPath"

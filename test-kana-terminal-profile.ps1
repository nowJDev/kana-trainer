# Windows Terminal에 Kana Trainer 전용 프로필이 설치되어 있는지 확인한다.
$ErrorActionPreference = "Stop"

$settingsCandidates = @(
    "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json",
    "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe\LocalState\settings.json"
)

$settingsPath = $settingsCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $settingsPath) {
    exit 1
}

$settings = Get-Content -LiteralPath $settingsPath -Raw -Encoding UTF8 | ConvertFrom-Json
$profile = $settings.profiles.list | Where-Object { $_.name -eq "Kana Trainer" } | Select-Object -First 1
if ($profile) {
    exit 0
}

exit 1

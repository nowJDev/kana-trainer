# Kana Trainer 전용 Windows Terminal 창을 연다.
param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$profileCheck = Join-Path $PSScriptRoot "test-kana-terminal-profile.ps1"
& powershell -NoProfile -ExecutionPolicy Bypass -File $profileCheck
if ($LASTEXITCODE -ne 0) {
    exit 1
}

$wtPath = Join-Path $env:LOCALAPPDATA "Microsoft\WindowsApps\wt.exe"
if (-not (Test-Path -LiteralPath $wtPath)) {
    $wtCommand = Get-Command wt.exe -ErrorAction SilentlyContinue
    if (-not $wtCommand) {
        exit 1
    }
    $wtPath = $wtCommand.Source
}

$arguments = '-w new nt -p "Kana Trainer"'
if ($DryRun) {
    Write-Output $wtPath
    Write-Output $arguments
    exit 0
}

Start-Process -FilePath $wtPath -ArgumentList $arguments -WindowStyle Normal
exit 0

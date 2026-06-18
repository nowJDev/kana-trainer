# 카나 학습 CLI를 PowerShell에서 안정적으로 실행한다.
$ErrorActionPreference = "Stop"

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
Set-Location -LiteralPath $PSScriptRoot

$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) {
    & py -3 -m kana_trainer
} else {
    & python -m kana_trainer
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Read-Host "오류가 발생했습니다. Enter를 누르면 닫습니다"
}

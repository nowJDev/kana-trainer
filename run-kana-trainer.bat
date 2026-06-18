@rem 가나 학습 CLI를 Windows에서 바로 실행한다.
@echo off
chcp 65001 > nul
cd /d "%~dp0"

set "KANA_TRAINER_DIRECT="
if /I "%~1"=="--direct" (
    set "KANA_TRAINER_DIRECT=1"
    shift
)

if not defined KANA_TRAINER_DIRECT (
    if "%~1"=="" (
        powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0open-kana-terminal.ps1" > nul 2> nul
        if not errorlevel 1 (
            exit /b
        )
    )
)

py -3 -V > nul 2> nul
if %errorlevel%==0 (
    py -3 -m kana_trainer %1 %2 %3 %4 %5 %6 %7 %8 %9
) else (
    python -m kana_trainer %1 %2 %3 %4 %5 %6 %7 %8 %9
)

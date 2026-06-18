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
    if not defined WT_SESSION (
        set "WT_EXE="
        if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe" set "WT_EXE=%LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe"
        if not defined WT_EXE (
            where wt.exe > nul 2> nul
            if %errorlevel%==0 set "WT_EXE=wt.exe"
        )
        if defined WT_EXE (
            powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0test-kana-terminal-profile.ps1" > nul 2> nul
            if not errorlevel 1 (
                "%WT_EXE%" -w new -p "Kana Trainer" -d "%~dp0" "%ComSpec%" /k call "%~f0" --direct %*
                if not errorlevel 1 exit /b
            )
        )
    )
)

py -3 -V > nul 2> nul
if %errorlevel%==0 (
    py -3 -m kana_trainer %1 %2 %3 %4 %5 %6 %7 %8 %9
) else (
    python -m kana_trainer %1 %2 %3 %4 %5 %6 %7 %8 %9
)

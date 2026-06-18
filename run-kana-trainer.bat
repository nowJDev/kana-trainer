@rem 가나 학습 GUI를 Windows에서 바로 실행한다.
@echo off
chcp.com 65001 >nul
cd /d "%~dp0"

where pythonw.exe >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw.exe -m kana_trainer --gui %*
    exit /b
)

python -m kana_trainer --gui %*

if errorlevel 1 (
    echo.
    echo 실행 중 오류가 발생했습니다.
    pause
)

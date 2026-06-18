@rem 가나 학습 CLI를 Windows에서 바로 실행한다.
@echo off
chcp.com 65001 >nul
cd /d "%~dp0"

python -m kana_trainer %*

if errorlevel 1 (
    echo.
    echo 실행 중 오류가 발생했습니다.
    pause
)

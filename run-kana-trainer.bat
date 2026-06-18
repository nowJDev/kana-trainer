@rem 가나 학습 CLI를 Windows에서 바로 실행한다.
@echo off
chcp 65001 > nul
cd /d "%~dp0"

py -3 -V > nul 2> nul
if %errorlevel%==0 (
    py -3 -m kana_trainer %*
) else (
    python -m kana_trainer %*
)

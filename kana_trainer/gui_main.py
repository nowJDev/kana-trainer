# PyInstaller GUI 실행 파일의 진입점을 제공한다.
from __future__ import annotations

from .gui import run_gui


if __name__ == "__main__":
    raise SystemExit(run_gui())

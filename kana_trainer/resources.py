# 패키징된 앱과 개발 환경에서 공용 리소스 파일 경로를 찾는다.
from __future__ import annotations

import sys
from pathlib import Path


def resource_root() -> Path:
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root is not None:
        return Path(bundle_root)
    return Path(__file__).resolve().parents[1]


def resource_path(name: str) -> Path:
    return resource_root() / name

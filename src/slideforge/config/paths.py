from __future__ import annotations

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[3]
BACKGROUND_DIR = BASE_DIR / "backgrounds"
OUTPUT_FILE = BASE_DIR / "ML_Foundations_Auto.pptx"
GENERATED_DIR = BASE_DIR / "_generated"


def ensure_runtime_dirs() -> None:
    GENERATED_DIR.mkdir(exist_ok=True)
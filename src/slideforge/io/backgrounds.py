from __future__ import annotations

from pathlib import Path
from typing import Any

from slideforge.config.paths import BACKGROUND_DIR


BACKGROUND_SETS = {
    "title": [
        "Background 8.png",
        "Background 9.png",
    ],
    "section": [
        "Background 8.png",
        "Background 9.png",
    ],
    "formula": [
        "Background 10.png",
        "Background 7.png",
        "Background 2.png",
    ],
    "concept": [
        "Background 1.png",
        "Background 4.png",
        "Background 6.png",
    ],
    "example": [
        "Background 7.png",
        "Background 1.png",
        "Background 6.png",
    ],
    "ml": [
        "Background 5.png",
        "Background 3.png",
    ],
}


def ensure_background_exists(filename: str) -> Path:
    path = BACKGROUND_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Background file not found: {path}")
    return path


def choose_background(theme: str, counters: dict[str, int]) -> str:
    options = BACKGROUND_SETS[theme]
    index = counters[theme] % len(options)
    counters[theme] += 1
    return options[index]


def validate_backgrounds(slides: list[dict[str, Any]]) -> None:
    required = set()

    for items in BACKGROUND_SETS.values():
        for filename in items:
            required.add(filename)

    for slide in slides:
        if "background" in slide:
            required.add(slide["background"])

    missing = [
        str(BACKGROUND_DIR / name)
        for name in sorted(required)
        if not (BACKGROUND_DIR / name).exists()
    ]
    if missing:
        raise FileNotFoundError(
            "These background files are missing:\n- " + "\n- ".join(missing)
        )
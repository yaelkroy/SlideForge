from __future__ import annotations

from collections import defaultdict

from slideforge.config.paths import OUTPUT_FILE, ensure_runtime_dirs
from slideforge.io.backgrounds import validate_backgrounds
from slideforge.app.build_deck import create_presentation
from slideforge.builders.builder_registry import BUILDERS
from slideforge.projects.ml_foundations import ML_FOUNDATIONS_PART1_SLIDES


SLIDES = ML_FOUNDATIONS_PART1_SLIDES


def build_deck() -> None:
    ensure_runtime_dirs()
    validate_backgrounds(SLIDES)

    prs = create_presentation()
    counters: dict[str, int] = defaultdict(int)

    for idx, spec in enumerate(SLIDES, start=1):
        kind = spec["kind"]
        if kind not in BUILDERS:
            raise ValueError(f"Unknown slide kind on slide {idx}: {kind}")
        BUILDERS[kind](prs, spec, counters)

    prs.save(OUTPUT_FILE)
    print(f"Saved presentation: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_deck()
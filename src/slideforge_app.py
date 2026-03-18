from __future__ import annotations

from collections import defaultdict
from typing import Any

from slideforge.app.presentation_factory import create_presentation
from slideforge.builders.dependency_map import build_dependency_map_slide
from slideforge.builders.section_divider import build_section_divider_slide
from slideforge.builders.title_composite import build_title_composite_slide
from slideforge.config.paths import OUTPUT_FILE, ensure_runtime_dirs
from slideforge.io.backgrounds import validate_backgrounds
from slideforge.projects.ml_foundations.slides_part1 import SLIDES


ensure_runtime_dirs()


def build_deck(slides: list[dict[str, Any]] | None = None) -> None:
    deck_slides = slides or SLIDES
    validate_backgrounds(deck_slides)

    prs = create_presentation()
    counters: dict[str, int] = defaultdict(int)

    builders = {
        "title_composite": build_title_composite_slide,
        "section_divider": build_section_divider_slide,
        "dependency_map": build_dependency_map_slide,
    }

    for idx, spec in enumerate(deck_slides, start=1):
        kind = spec["kind"]
        if kind not in builders:
            raise ValueError(f"Unknown slide kind on slide {idx}: {kind}")
        builders[kind](prs, spec, counters)

    prs.save(OUTPUT_FILE)
    print(f"Saved presentation: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_deck()
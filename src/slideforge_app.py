from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from slideforge.app.build_deck import build_deck, load_slides, main
from slideforge.config.paths import OUTPUT_FILE


# Example launcher target. The engine itself is generic; this file only provides
# a convenient default for local development.
DEFAULT_PROJECT = "ml_foundations"


def build_example_deck(
    slides: Sequence[dict[str, Any]] | None = None,
    output_file: str | Path = OUTPUT_FILE,
    theme_overrides: Mapping[str, Any] | None = None,
) -> Path:
    resolved_slides = slides if slides is not None else load_slides(DEFAULT_PROJECT)
    return build_deck(
        resolved_slides,
        output_file=output_file,
        theme_overrides=theme_overrides,
    )


if __name__ == "__main__":
    main()

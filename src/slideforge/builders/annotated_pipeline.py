from __future__ import annotations

from typing import Any

from pptx import Presentation

from slideforge.builders.pipeline import build_pipeline_family_slide


def build_annotated_pipeline_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    """Universal composition-semantic name for the annotated/example pipeline family."""
    build_pipeline_family_slide(prs, spec, counters, variant="example_pipeline")


__all__ = ["build_annotated_pipeline_slide"]

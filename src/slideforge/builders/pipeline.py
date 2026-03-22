from __future__ import annotations

from typing import Any

from pptx import Presentation

from slideforge.builders.common import new_slide
from slideforge.config.themes import get_theme
from slideforge.io.backgrounds import choose_background
from slideforge.layout.pipeline import layout_pipeline_family
from slideforge.render.header import render_header_from_spec
from slideforge.render.pipeline_blocks import (
    render_bullets_box,
    render_connectors,
    render_examples_row,
    render_stage_card,
    render_takeaway,
    resolve_pipeline_style,
)
from slideforge.render.primitives import add_footer
from slideforge.spec.pipeline_normalization import normalize_pipeline_family_spec


def build_pipeline_family_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
    *,
    variant: str,
) -> None:
    """Universal pipeline-family builder.

    Variants:
    - ``pipeline``: stages + optional running examples + boxed takeaway
    - ``example_pipeline``: stages + optional bullets + inline takeaway
    """
    slide_theme_name = spec.get("theme", "concept")
    theme_obj = get_theme(slide_theme_name=slide_theme_name)
    bg = spec.get("background") or choose_background(slide_theme_name, counters)
    slide = new_slide(prs, bg)

    layout = dict(spec.get("layout", {}) or {})
    normalized = normalize_pipeline_family_spec(spec, variant=variant)
    header_result = render_header_from_spec(slide, spec, theme=theme_obj)
    style = resolve_pipeline_style(spec, theme_obj=theme_obj)

    layout_result = layout_pipeline_family(
        header_content_top_y=header_result.content_top_y,
        layout=layout,
        variant=normalized.variant,
        stage_count=len(normalized.stages),
        example_count=len(normalized.examples),
        has_bullets=bool(normalized.bullets),
        has_takeaway=bool(normalized.takeaway),
    )

    suffix_prefix = "example_pipeline" if normalized.variant == "example_pipeline" else "pipeline"
    for idx, (stage, box) in enumerate(zip(normalized.stages, layout_result.stage_boxes)):
        render_stage_card(
            slide,
            stage,
            box,
            idx,
            pipeline_style=style,
            layout=layout,
            suffix_prefix=suffix_prefix,
        )
    render_connectors(slide, layout_result.connectors, style=style)

    if normalized.variant == "pipeline" and normalized.examples:
        render_examples_row(
            slide,
            normalized.examples,
            layout_result.example_boxes,
            label_box=layout_result.examples_label_box,
            label_text=normalized.examples_label_text,
            style=style,
            layout=layout,
            suffix_prefix="pipeline_example",
        )
    elif normalized.variant == "example_pipeline" and normalized.bullets:
        render_bullets_box(slide, normalized.bullets, layout_result.bullets_box, style=style, layout=layout)

    render_takeaway(
        slide,
        normalized.takeaway,
        layout_result.takeaway_box,
        style=style,
        layout=layout,
        boxed=normalized.variant == "pipeline",
    )
    add_footer(slide, dark=style["footer_dark"], color=style["footer_color"])


def build_pipeline_slide(prs: Presentation, spec: dict[str, Any], counters: dict[str, int]) -> None:
    build_pipeline_family_slide(prs, spec, counters, variant="pipeline")

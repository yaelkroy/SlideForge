from __future__ import annotations

from typing import Any, Mapping

from pptx import Presentation

from slideforge.builders.common import new_slide
from slideforge.builders.triple_role_bands import render_triple_role_bottom_bands
from slideforge.builders.triple_role_panels import render_triple_role_panels
from slideforge.builders.triple_role_style import resolve_triple_role_style
from slideforge.config.themes import get_theme
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box
from slideforge.render.header import render_header_from_spec
from slideforge.render.primitives import add_footer


def _join_items(items: list[str]) -> str:
    cleaned = [item.strip() for item in items if item and item.strip()]
    return "   •   ".join(cleaned)


def _box_from_dict(raw: Mapping[str, Any], fallback: Box) -> Box:
    return Box(
        raw.get("x", fallback.x),
        raw.get("y", fallback.y),
        raw.get("w", fallback.w),
        raw.get("h", fallback.h),
    )


def build_triple_role_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    slide_theme_name = spec.get("theme", "concept")
    theme_obj = get_theme(slide_theme_name=slide_theme_name)

    bg = spec.get("background") or choose_background(slide_theme_name, counters)
    slide = new_slide(prs, bg)

    layout = dict(spec.get("layout", {}) or {})
    style = resolve_triple_role_style(spec, theme_obj=theme_obj)

    panels = list(spec.get("panels", []) or [])
    bullets_text = _join_items(list(spec.get("bullets", []) or []))
    formulas_text = _join_items(list(spec.get("formulas", []) or []))
    takeaway = str(spec.get("takeaway", "")).strip()

    header_result = render_header_from_spec(
        slide,
        spec,
        theme=theme_obj,
    )

    panel_region_fallback = Box(
        float(layout.get("panel_x", 0.88)),
        float(
            layout.get(
                "panel_y",
                header_result.content_top_y
                + float(layout.get("content_to_panel_gap", 0.14)),
            )
        ),
        float(layout.get("panel_w", 11.24)),
        float(layout.get("panel_h", 3.05)),
    )
    panel_region_raw = layout.get("panel_region")
    panel_region = (
        _box_from_dict(panel_region_raw, panel_region_fallback)
        if isinstance(panel_region_raw, Mapping)
        else panel_region_fallback
    )

    render_triple_role_panels(
        slide,
        panels=panels,
        panel_region=panel_region,
        layout=layout,
        style=style,
    )

    render_triple_role_bottom_bands(
        slide,
        panel_region=panel_region,
        bullets_text=bullets_text,
        formulas_text=formulas_text,
        takeaway=takeaway,
        layout=layout,
        style=style,
    )

    add_footer(
        slide,
        dark=style["footer_dark"],
        color=style["footer_color"],
    )
from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, NAVY, SLATE, TITLE_FONT
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, layout_concept_poster
from slideforge.render.primitives import (
    add_divider_line,
    add_footer,
    add_rounded_box,
    add_textbox,
)


def _join_items(items: list[str]) -> str:
    cleaned = [item.strip() for item in items if item and item.strip()]
    return "   •   ".join(cleaned)


def _add_fitted_text(
    slide,
    *,
    box: Box,
    text: str,
    font_name: str,
    font_size: int,
    color,
    bold: bool = False,
    align=PP_ALIGN.CENTER,
) -> None:
    if not text.strip() or box.w <= 0 or box.h <= 0:
        return

    add_textbox(
        slide,
        x=box.x,
        y=box.y,
        w=box.w,
        h=box.h,
        text=text,
        font_name=font_name,
        font_size=font_size,
        color=color,
        bold=bold,
        align=align,
    )


def build_concept_poster_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    theme = spec.get("theme", "concept")
    bg = spec.get("background") or choose_background(theme, counters)
    slide = new_slide(prs, bg)

    layout = spec.get("layout", {})

    title = spec.get("title") or spec["slide_title"]
    subtitle = spec.get("subtitle", "").strip()
    mini_visual = spec.get("mini_visual", "").strip()

    explanation = (
        spec.get("text_explanation", "").strip()
        or spec.get("explanation", "").strip()
    )
    bullets = spec.get("bullets", [])
    bullets_text = _join_items(bullets)

    formulas = spec.get("formulas", [])
    formulas_text = _join_items(formulas)

    note_text = spec.get("concrete_example_anchor", "").strip()
    takeaway = spec.get("takeaway", "").strip()

    add_textbox(
        slide,
        x=0.80,
        y=layout.get("title_y", 0.42),
        w=11.70,
        h=0.52,
        text=title,
        font_name=TITLE_FONT,
        font_size=28,
        color=NAVY,
        bold=True,
    )
    add_divider_line(slide, dark=False)

    if subtitle:
        add_textbox(
            slide,
            x=1.00,
            y=layout.get("subtitle_y", 0.98),
            w=11.00,
            h=0.42,
            text=subtitle,
            font_name=BODY_FONT,
            font_size=17,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    poster_box_dict = layout.get(
        "poster_box",
        {"x": 0.96, "y": 1.34, "w": 11.10, "h": 4.98},
    )
    outer_box = Box(
        poster_box_dict["x"],
        poster_box_dict["y"],
        poster_box_dict["w"],
        poster_box_dict["h"],
    )

    add_rounded_box(
        slide,
        outer_box.x,
        outer_box.y,
        outer_box.w,
        outer_box.h,
    )

    poster_layout = layout_concept_poster(
        outer_box,
        explanation=explanation,
        bullets_text=bullets_text,
        formulas_text=formulas_text,
        note_text=note_text,
        takeaway_text=takeaway,
        top_pad=layout.get("top_pad", 0.18),
        bottom_pad=layout.get("bottom_pad", 0.14),
        gap=layout.get("content_gap", 0.08),
        visual_min_share=layout.get("visual_min_share", 0.66),
        visual_max_share=layout.get("visual_max_share", 0.80),
    )

    # Optional manual override, but the default should be autofit-driven.
    visual_override = layout.get("visual_box")
    visual_box = (
        Box(
            visual_override["x"],
            visual_override["y"],
            visual_override["w"],
            visual_override["h"],
        )
        if visual_override
        else poster_layout.visual_box
    )

    if mini_visual:
        add_mini_visual(
            slide,
            kind=mini_visual,
            x=visual_box.x,
            y=visual_box.y,
            w=visual_box.w,
            h=visual_box.h,
            suffix="_concept_poster",
            variant="dark_on_light",
        )

    fits = poster_layout.text_fits
    boxes = poster_layout.text_boxes

    if "explanation" in boxes and "explanation" in fits:
        _add_fitted_text(
            slide,
            box=boxes["explanation"],
            text=explanation,
            font_name=BODY_FONT,
            font_size=max(15, fits["explanation"].font_size),
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    if "bullets" in boxes and "bullets" in fits:
        _add_fitted_text(
            slide,
            box=boxes["bullets"],
            text=bullets_text,
            font_name=BODY_FONT,
            font_size=max(13, fits["bullets"].font_size),
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    if "formulas" in boxes and "formulas" in fits:
        _add_fitted_text(
            slide,
            box=boxes["formulas"],
            text=formulas_text,
            font_name=FORMULA_FONT,
            font_size=max(13, fits["formulas"].font_size),
            color=NAVY,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    if "note" in boxes and "note" in fits:
        _add_fitted_text(
            slide,
            box=boxes["note"],
            text=note_text,
            font_name=BODY_FONT,
            font_size=max(12, fits["note"].font_size),
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    if "takeaway" in boxes and "takeaway" in fits:
        _add_fitted_text(
            slide,
            box=boxes["takeaway"],
            text=takeaway,
            font_name=BODY_FONT,
            font_size=max(13, fits["takeaway"].font_size),
            color=SLATE,
            bold=True,
            align=PP_ALIGN.CENTER,
        )

    add_footer(slide, dark=False)
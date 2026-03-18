from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, NAVY, SLATE, TITLE_FONT
from slideforge.io.backgrounds import choose_background
from slideforge.render.primitives import (
    add_divider_line,
    add_footer,
    add_rounded_box,
    add_textbox,
)


def _join_items(items: list[str]) -> str:
    cleaned = [item.strip() for item in items if item and item.strip()]
    return "   •   ".join(cleaned)


def build_concept_poster_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    theme = spec.get("theme", "concept")
    bg = spec.get("background") or choose_background(theme, counters)
    slide = new_slide(prs, bg)

    layout = spec.get("layout", {})

    title_y = layout.get("title_y", 0.42)
    subtitle_y = layout.get("subtitle_y", 0.98)
    poster_box = layout.get(
        "poster_box",
        {"x": 0.95, "y": 1.34, "w": 11.15, "h": 4.96},
    )

    add_textbox(
        slide,
        x=0.80,
        y=title_y,
        w=11.70,
        h=0.50,
        text=spec["title"],
        font_name=TITLE_FONT,
        font_size=26,
        color=NAVY,
        bold=True,
    )
    add_divider_line(slide, dark=False)

    subtitle = spec.get("subtitle", "").strip()
    if subtitle:
        add_textbox(
            slide,
            x=1.00,
            y=subtitle_y,
            w=11.00,
            h=0.40,
            text=subtitle,
            font_name=BODY_FONT,
            font_size=17,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    add_rounded_box(
        slide,
        poster_box["x"],
        poster_box["y"],
        poster_box["w"],
        poster_box["h"],
    )

    mini_visual = spec.get("mini_visual", "").strip()

    explanation = (
        spec.get("text_explanation", "").strip()
        or spec.get("explanation", "").strip()
    )
    bullets = spec.get("bullets", [])
    formulas = spec.get("formulas", [])
    anchor = spec.get("concrete_example_anchor", "").strip()
    takeaway = spec.get("takeaway", "").strip()

    # Dynamic vertical layout:
    # reserve only the space we actually need below the visual.
    text_blocks: list[tuple[str, float]] = []
    if explanation:
        text_blocks.append(("explanation", 0.44))
    if bullets:
        text_blocks.append(("bullets", 0.24))
    if formulas:
        text_blocks.append(("formulas", 0.24))
    if anchor:
        text_blocks.append(("anchor", 0.20))
    if takeaway:
        text_blocks.append(("takeaway", 0.24))

    gap = 0.08
    reserved_h = sum(h for _, h in text_blocks) + gap * len(text_blocks)

    top_pad = 0.20
    bottom_pad = 0.16
    visual_h = poster_box["h"] - top_pad - bottom_pad - reserved_h
    visual_h = max(2.90, visual_h)

    visual_x = poster_box["x"] + 0.30
    visual_y = poster_box["y"] + top_pad
    visual_w = poster_box["w"] - 0.60

    # If the caller explicitly wants a larger diagram, allow overrides.
    visual_box = layout.get("visual_box")
    if visual_box:
        visual_x = visual_box["x"]
        visual_y = visual_box["y"]
        visual_w = visual_box["w"]
        visual_h = visual_box["h"]

    if mini_visual:
        add_mini_visual(
            slide,
            kind=mini_visual,
            x=visual_x,
            y=visual_y,
            w=visual_w,
            h=visual_h,
            suffix="_concept_poster",
            variant="dark_on_light",
        )

    current_y = visual_y + visual_h + gap

    if explanation:
        add_textbox(
            slide,
            x=poster_box["x"] + 0.28,
            y=current_y,
            w=poster_box["w"] - 0.56,
            h=0.44,
            text=explanation,
            font_name=BODY_FONT,
            font_size=16,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )
        current_y += 0.44 + gap

    if bullets:
        add_textbox(
            slide,
            x=poster_box["x"] + 0.28,
            y=current_y,
            w=poster_box["w"] - 0.56,
            h=0.24,
            text=_join_items(bullets),
            font_name=BODY_FONT,
            font_size=14,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )
        current_y += 0.24 + gap

    if formulas:
        add_textbox(
            slide,
            x=poster_box["x"] + 0.24,
            y=current_y,
            w=poster_box["w"] - 0.48,
            h=0.24,
            text=_join_items(formulas),
            font_name=FORMULA_FONT,
            font_size=13,
            color=NAVY,
            bold=False,
            align=PP_ALIGN.CENTER,
        )
        current_y += 0.24 + gap

    if anchor:
        add_textbox(
            slide,
            x=poster_box["x"] + 0.26,
            y=current_y,
            w=poster_box["w"] - 0.52,
            h=0.20,
            text=anchor,
            font_name=BODY_FONT,
            font_size=12,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )
        current_y += 0.20 + gap

    if takeaway:
        add_textbox(
            slide,
            x=poster_box["x"] + 0.24,
            y=current_y,
            w=poster_box["w"] - 0.48,
            h=0.24,
            text=takeaway,
            font_name=BODY_FONT,
            font_size=13,
            color=SLATE,
            bold=True,
            align=PP_ALIGN.CENTER,
        )

    add_footer(slide, dark=False)
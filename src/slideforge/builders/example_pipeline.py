from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import ACCENT, BODY_FONT, FORMULA_FONT, NAVY, SLATE, TITLE_FONT
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, centered_visual_in_card, fit_text
from slideforge.render.primitives import (
    add_divider_line,
    add_footer,
    add_rounded_box,
    add_soft_connector,
    add_textbox,
)


def _join_items(items: list[str]) -> str:
    cleaned = [item.strip() for item in items if item and item.strip()]
    return "   •   ".join(cleaned)


def _fit_stage_text(
    text: str,
    box: Box,
    *,
    min_font: int,
    max_font: int,
    max_lines: int,
) -> int:
    if not text.strip() or box.w <= 0 or box.h <= 0:
        return max_font
    fitted = fit_text(
        text,
        box.w,
        box.h,
        min_font_size=min_font,
        max_font_size=max_font,
        max_lines=max_lines,
    )
    return max(min_font, fitted.font_size)


def _add_stage_card(
    slide,
    stage: dict[str, Any],
    card_box: Box,
    idx: int,
) -> None:
    add_rounded_box(slide, card_box.x, card_box.y, card_box.w, card_box.h)

    title_box = Box(card_box.x + 0.10, card_box.y + 0.10, card_box.w - 0.20, 0.24)
    title_text = stage.get("title", "").strip()
    title_font = _fit_stage_text(
        title_text,
        title_box,
        min_font=12,
        max_font=15,
        max_lines=2,
    )
    add_textbox(
        slide,
        x=title_box.x,
        y=title_box.y,
        w=title_box.w,
        h=title_box.h,
        text=title_text,
        font_name=TITLE_FONT,
        font_size=title_font,
        color=NAVY,
        bold=True,
        align=PP_ALIGN.CENTER,
    )

    caption_text = stage.get("caption", "").strip()
    formula_text = stage.get("formula", "").strip()

    visual_box = centered_visual_in_card(
        card_box,
        title_h=0.24,
        caption_h=0.24 if caption_text else 0.0,
        formula_h=0.18 if formula_text else 0.0,
        top_pad=0.10,
        bottom_pad=0.12,
        gap_above_visual=0.10,
        gap_below_visual=0.10,
    )

    add_mini_visual(
        slide,
        kind=stage.get("mini_visual", ""),
        x=visual_box.x,
        y=visual_box.y,
        w=visual_box.w,
        h=visual_box.h,
        suffix=f"_example_pipeline_{idx}",
        variant="dark_on_light",
    )

    current_y = visual_box.bottom + 0.08

    if caption_text:
        caption_box = Box(card_box.x + 0.12, current_y, card_box.w - 0.24, 0.24)
        caption_font = _fit_stage_text(
            caption_text,
            caption_box,
            min_font=11,
            max_font=13,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=caption_box.x,
            y=caption_box.y,
            w=caption_box.w,
            h=caption_box.h,
            text=caption_text,
            font_name=BODY_FONT,
            font_size=caption_font,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )
        current_y += 0.24 + 0.04

    if formula_text:
        formula_box = Box(card_box.x + 0.10, current_y, card_box.w - 0.20, 0.18)
        formula_font = _fit_stage_text(
            formula_text,
            formula_box,
            min_font=11,
            max_font=13,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=formula_box.x,
            y=formula_box.y,
            w=formula_box.w,
            h=formula_box.h,
            text=formula_text,
            font_name=FORMULA_FONT,
            font_size=formula_font,
            color=NAVY,
            bold=False,
            align=PP_ALIGN.CENTER,
        )


def build_example_pipeline_slide(
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
    stages = spec.get("example_pipeline", {}).get("stages", [])
    bullets = spec.get("bullets", [])
    takeaway = spec.get("takeaway", "").strip()

    add_textbox(
        slide,
        x=0.80,
        y=layout.get("title_y", 0.42),
        w=11.70,
        h=0.52,
        text=title,
        font_name=TITLE_FONT,
        font_size=27,
        color=NAVY,
        bold=True,
    )
    add_divider_line(slide, dark=False)

    if subtitle:
        add_textbox(
            slide,
            x=0.96,
            y=layout.get("subtitle_y", 0.98),
            w=11.08,
            h=0.42,
            text=subtitle,
            font_name=BODY_FONT,
            font_size=16,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    region_dict = layout.get(
        "pipeline_region",
        {"x": 0.82, "y": 1.78, "w": 11.32, "h": 2.92},
    )
    region = Box(
        region_dict["x"],
        region_dict["y"],
        region_dict["w"],
        region_dict["h"],
    )
    gap = layout.get("pipeline_gap", 0.30)

    count = max(1, len(stages))
    card_w = (region.w - gap * (count - 1)) / count
    card_h = region.h

    for idx, stage in enumerate(stages):
        card_box = Box(
            region.x + idx * (card_w + gap),
            region.y,
            card_w,
            card_h,
        )
        _add_stage_card(slide, stage, card_box, idx)

        if idx < count - 1:
            next_x = region.x + (idx + 1) * (card_w + gap)
            add_soft_connector(
                slide,
                x1=card_box.right,
                y1=card_box.y + card_box.h / 2,
                x2=next_x,
                y2=card_box.y + card_box.h / 2,
                color=ACCENT,
                width_pt=1.6,
            )

    if bullets:
        bullets_text = _join_items(bullets)
        bullets_y = layout.get("bullets_y", region.bottom + 0.28)
        bullets_box = Box(1.00, bullets_y, 11.00, 0.24)
        bullets_font = _fit_stage_text(
            bullets_text,
            bullets_box,
            min_font=12,
            max_font=14,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=bullets_box.x,
            y=bullets_box.y,
            w=bullets_box.w,
            h=bullets_box.h,
            text=bullets_text,
            font_name=BODY_FONT,
            font_size=bullets_font,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    if takeaway:
        takeaway_y = layout.get("takeaway_y", region.bottom + 0.72)
        takeaway_box = Box(1.02, takeaway_y, 10.96, 0.42)
        takeaway_font = _fit_stage_text(
            takeaway,
            takeaway_box,
            min_font=12,
            max_font=14,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=takeaway_box.x,
            y=takeaway_box.y,
            w=takeaway_box.w,
            h=takeaway_box.h,
            text=takeaway,
            font_name=BODY_FONT,
            font_size=takeaway_font,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    add_footer(slide, dark=False)
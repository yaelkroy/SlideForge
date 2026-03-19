from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import ACCENT, BODY_FONT, FORMULA_FONT, NAVY, SLATE, TITLE_FONT
from slideforge.io.backgrounds import choose_background
from slideforge.render.primitives import (
    add_divider_line,
    add_footer,
    add_rounded_box,
    add_soft_connector,
    add_textbox,
)
from slideforge.utils.text_layout import fit_joined_items_to_box, fit_text_to_box


def _add_stage_card(
    slide,
    stage: dict[str, Any],
    x: float,
    y: float,
    w: float,
    h: float,
    idx: int,
) -> None:
    add_rounded_box(slide, x, y, w, h)

    inner_x = x + 0.12
    inner_y = y + 0.10
    inner_w = w - 0.24
    inner_h = h - 0.20

    title_fit = fit_text_to_box(
        text=stage.get("title", ""),
        width_in=inner_w,
        height_in=0.28,
        min_font_size=13,
        max_font_size=16,
        max_lines=2,
    )

    caption_text = stage.get("caption", "").strip()
    caption_fit = fit_text_to_box(
        text=caption_text,
        width_in=inner_w,
        height_in=0.34,
        min_font_size=12,
        max_font_size=14,
        max_lines=2,
    ) if caption_text else None

    formula_text = stage.get("formula", "").strip()
    formula_fit = fit_text_to_box(
        text=formula_text,
        width_in=inner_w,
        height_in=0.28,
        min_font_size=12,
        max_font_size=13,
        max_lines=2,
    ) if formula_text else None

    reserved_h = title_fit.height_in + 0.08
    if caption_fit:
        reserved_h += caption_fit.height_in + 0.06
    if formula_fit:
        reserved_h += formula_fit.height_in + 0.06

    visual_h = max(1.40, inner_h - reserved_h)
    visual_y = inner_y + title_fit.height_in + 0.06

    add_textbox(
        slide,
        x=inner_x,
        y=inner_y,
        w=inner_w,
        h=title_fit.height_in + 0.02,
        text=title_fit.text,
        font_name=TITLE_FONT,
        font_size=title_fit.font_size,
        color=NAVY,
        bold=True,
        align=PP_ALIGN.CENTER,
    )

    add_mini_visual(
        slide,
        kind=stage.get("mini_visual", ""),
        x=inner_x + 0.04,
        y=visual_y,
        w=inner_w - 0.08,
        h=visual_h,
        suffix=f"_example_pipeline_{idx}",
        variant="dark_on_light",
    )

    cursor_y = visual_y + visual_h + 0.05

    if caption_fit:
        add_textbox(
            slide,
            x=inner_x,
            y=cursor_y,
            w=inner_w,
            h=caption_fit.height_in + 0.02,
            text=caption_fit.text,
            font_name=BODY_FONT,
            font_size=caption_fit.font_size,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )
        cursor_y += caption_fit.height_in + 0.04

    if formula_fit:
        add_textbox(
            slide,
            x=inner_x,
            y=cursor_y,
            w=inner_w,
            h=formula_fit.height_in + 0.02,
            text=formula_fit.text,
            font_name=FORMULA_FONT,
            font_size=formula_fit.font_size,
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
    region = layout.get("pipeline_region", {"x": 0.82, "y": 1.78, "w": 11.32, "h": 2.92})
    gap = layout.get("pipeline_gap", 0.30)

    add_textbox(
        slide,
        x=0.80,
        y=layout.get("title_y", 0.42),
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
        sub_fit = fit_text_to_box(
            text=subtitle,
            width_in=11.0,
            height_in=0.42,
            min_font_size=15,
            max_font_size=17,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=1.00,
            y=layout.get("subtitle_y", 0.98),
            w=11.00,
            h=0.42,
            text=sub_fit.text,
            font_name=BODY_FONT,
            font_size=sub_fit.font_size,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    stages = spec.get("example_pipeline", {}).get("stages", [])
    count = max(1, min(3, len(stages)))
    stages = stages[:count]

    card_w = (region["w"] - gap * (count - 1)) / count
    for idx, stage in enumerate(stages):
        card_x = region["x"] + idx * (card_w + gap)

        _add_stage_card(
            slide=slide,
            stage=stage,
            x=card_x,
            y=region["y"],
            w=card_w,
            h=region["h"],
            idx=idx,
        )

        if idx < count - 1:
            next_x = region["x"] + (idx + 1) * (card_w + gap)
            add_soft_connector(
                slide,
                x1=card_x + card_w,
                y1=region["y"] + region["h"] / 2,
                x2=next_x,
                y2=region["y"] + region["h"] / 2,
                color=ACCENT,
                width_pt=1.6,
            )

    bullets = spec.get("bullets", [])
    if bullets:
        fit = fit_joined_items_to_box(
            items=bullets,
            width_in=11.0,
            height_in=0.28,
            min_font_size=12,
            max_font_size=14,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=1.00,
            y=layout.get("bullets_y", 5.02),
            w=11.00,
            h=0.28,
            text=fit.text,
            font_name=BODY_FONT,
            font_size=fit.font_size,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    takeaway = spec.get("takeaway", "").strip()
    if takeaway:
        fit = fit_text_to_box(
            text=takeaway,
            width_in=10.9,
            height_in=0.34,
            min_font_size=12,
            max_font_size=14,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=1.10,
            y=layout.get("takeaway_y", 5.46),
            w=10.90,
            h=0.34,
            text=fit.text,
            font_name=BODY_FONT,
            font_size=fit.font_size,
            color=SLATE,
            bold=True,
            align=PP_ALIGN.CENTER,
        )

    add_footer(slide, dark=False)
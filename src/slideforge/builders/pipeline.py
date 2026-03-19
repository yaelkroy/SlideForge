from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual, add_visual_with_caption
from slideforge.builders.common import new_slide
from slideforge.config.constants import (
    ACCENT,
    BODY_FONT,
    FORMULA_FONT,
    NAVY,
    SLATE,
    TITLE_FONT,
)
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, centered_visual_in_card, fit_text
from slideforge.render.primitives import (
    add_divider_line,
    add_footer,
    add_rounded_box,
    add_soft_connector,
    add_textbox,
)


def _fit_text_size(
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


def _pipeline_card(
    slide,
    step: dict[str, Any],
    card_box: Box,
    idx: int,
) -> None:
    add_rounded_box(slide, card_box.x, card_box.y, card_box.w, card_box.h)

    title_text = step.get("title", "").strip()
    body_text = step.get("body", "").strip()
    footer_text = step.get("footer", "").strip()

    title_box = Box(card_box.x + 0.10, card_box.y + 0.10, card_box.w - 0.20, 0.24)
    title_font = _fit_text_size(
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

    visual_box = centered_visual_in_card(
        card_box,
        title_h=0.24,
        caption_h=0.22 if body_text else 0.0,
        formula_h=0.18 if footer_text else 0.0,
        top_pad=0.10,
        bottom_pad=0.12,
        gap_above_visual=0.10,
        gap_below_visual=0.10,
    )

    add_mini_visual(
        slide,
        kind=step.get("mini_visual", ""),
        x=visual_box.x,
        y=visual_box.y,
        w=visual_box.w,
        h=visual_box.h,
        suffix=f"_pipeline_{idx}",
        variant="dark_on_light",
    )

    current_y = visual_box.bottom + 0.08

    if body_text:
        body_box = Box(card_box.x + 0.12, current_y, card_box.w - 0.24, 0.22)
        body_font = _fit_text_size(
            body_text,
            body_box,
            min_font=11,
            max_font=13,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=body_box.x,
            y=body_box.y,
            w=body_box.w,
            h=body_box.h,
            text=body_text,
            font_name=BODY_FONT,
            font_size=body_font,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )
        current_y += 0.22 + 0.04

    if footer_text:
        footer_box = Box(card_box.x + 0.10, current_y, card_box.w - 0.20, 0.18)
        footer_font = _fit_text_size(
            footer_text,
            footer_box,
            min_font=11,
            max_font=13,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=footer_box.x,
            y=footer_box.y,
            w=footer_box.w,
            h=footer_box.h,
            text=footer_text,
            font_name=FORMULA_FONT,
            font_size=footer_font,
            color=NAVY,
            bold=False,
            align=PP_ALIGN.CENTER,
        )


def build_pipeline_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    theme = spec.get("theme", "concept")
    bg = spec.get("background") or choose_background(theme, counters)
    slide = new_slide(prs, bg)

    layout = spec.get("layout", {})
    steps = spec.get("pipeline", {}).get("steps", [])

    title = spec.get("title") or spec["slide_title"]
    subtitle = spec.get("subtitle", "").strip()
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
        subtitle_box = Box(1.00, layout.get("subtitle_y", 0.98), 11.00, 0.42)
        subtitle_font = _fit_text_size(
            subtitle,
            subtitle_box,
            min_font=15,
            max_font=17,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=subtitle_box.x,
            y=subtitle_box.y,
            w=subtitle_box.w,
            h=subtitle_box.h,
            text=subtitle,
            font_name=BODY_FONT,
            font_size=subtitle_font,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    region_dict = layout.get(
        "pipeline_region",
        {"x": 0.86, "y": 1.84, "w": 11.28, "h": 2.48},
    )
    region = Box(
        region_dict["x"],
        region_dict["y"],
        region_dict["w"],
        region_dict["h"],
    )
    gap = layout.get("pipeline_gap", 0.22)

    count = max(1, len(steps))
    card_w = (region.w - gap * (count - 1)) / count
    card_h = region.h

    for idx, step in enumerate(steps):
        card_box = Box(
            region.x + idx * (card_w + gap),
            region.y,
            card_w,
            card_h,
        )
        _pipeline_card(slide, step, card_box, idx)

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

    examples = spec.get("examples", [])
    if examples:
        examples_label_box = Box(1.10, layout.get("examples_y", region.bottom + 0.22), 10.90, 0.20)
        examples_label_font = _fit_text_size(
            "Running examples",
            examples_label_box,
            min_font=12,
            max_font=13,
            max_lines=1,
        )
        add_textbox(
            slide,
            x=examples_label_box.x,
            y=examples_label_box.y,
            w=examples_label_box.w,
            h=examples_label_box.h,
            text="Running examples",
            font_name=BODY_FONT,
            font_size=examples_label_font,
            color=SLATE,
            bold=True,
            align=PP_ALIGN.CENTER,
        )

        ex_y = examples_label_box.bottom + 0.04
        ex_w = 4.85
        ex_gap = 0.38
        ex_x0 = 1.18

        for idx, ex in enumerate(examples[:2]):
            if isinstance(ex, dict):
                ex_kind = ex.get("mini_visual", "")
                ex_text = ex.get("text", "")
            else:
                ex_kind = ""
                ex_text = str(ex)

            ex_x = ex_x0 + idx * (ex_w + ex_gap)
            add_visual_with_caption(
                slide,
                kind=ex_kind,
                x=ex_x,
                y=ex_y,
                w=ex_w,
                h=0.98,
                caption=ex_text,
                suffix=f"_pipeline_example_{idx}",
                variant="dark_on_light",
                caption_font_size=12,
            )

    if takeaway:
        takeaway_box_dict = layout.get(
            "takeaway_box",
            {"x": 1.00, "y": 5.40, "w": 10.90, "h": 0.70},
        )
        takeaway_box = Box(
            takeaway_box_dict["x"],
            takeaway_box_dict["y"],
            takeaway_box_dict["w"],
            takeaway_box_dict["h"],
        )
        add_rounded_box(
            slide,
            takeaway_box.x,
            takeaway_box.y,
            takeaway_box.w,
            takeaway_box.h,
        )
        takeaway_text_box = Box(
            takeaway_box.x + 0.16,
            takeaway_box.y + 0.10,
            takeaway_box.w - 0.32,
            takeaway_box.h - 0.16,
        )
        takeaway_font = _fit_text_size(
            takeaway,
            takeaway_text_box,
            min_font=12,
            max_font=14,
            max_lines=3,
        )
        add_textbox(
            slide,
            x=takeaway_text_box.x,
            y=takeaway_text_box.y,
            w=takeaway_text_box.w,
            h=takeaway_text_box.h,
            text=takeaway,
            font_name=BODY_FONT,
            font_size=takeaway_font,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    add_footer(slide, dark=False)
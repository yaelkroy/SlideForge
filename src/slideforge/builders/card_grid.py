from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, NAVY, SLATE, TITLE_FONT
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, centered_visual_in_card, fit_text
from slideforge.render.primitives import add_divider_line, add_footer, add_rounded_box, add_textbox


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


def _add_grid_card(
    slide,
    card: dict[str, Any],
    card_box: Box,
    idx: int,
) -> None:
    add_rounded_box(slide, card_box.x, card_box.y, card_box.w, card_box.h)

    title_text = card.get("title", "").strip()
    formula_text = card.get("formula", "").strip()
    caption_text = card.get("caption", "").strip()

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
        caption_h=0.20 if caption_text else 0.0,
        formula_h=0.18 if formula_text else 0.0,
        top_pad=0.10,
        bottom_pad=0.12,
        gap_above_visual=0.10,
        gap_below_visual=0.10,
    )

    add_mini_visual(
        slide,
        kind=card.get("mini_visual", ""),
        x=visual_box.x,
        y=visual_box.y,
        w=visual_box.w,
        h=visual_box.h,
        suffix=f"_card_grid_{idx}",
        variant="dark_on_light",
    )

    current_y = visual_box.bottom + 0.08

    if formula_text:
        formula_box = Box(card_box.x + 0.10, current_y, card_box.w - 0.20, 0.18)
        formula_font = _fit_text_size(
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
        current_y += 0.18 + 0.05

    if caption_text:
        caption_box = Box(card_box.x + 0.10, current_y, card_box.w - 0.20, 0.20)
        caption_font = _fit_text_size(
            caption_text,
            caption_box,
            min_font=10,
            max_font=12,
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


def build_card_grid_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    theme = spec.get("theme", "concept")
    bg = spec.get("background") or choose_background(theme, counters)
    slide = new_slide(prs, bg)

    layout = spec.get("layout", {})
    grid = spec.get("grid", {})
    rows = grid.get("rows", 1)
    cols = grid.get("cols", 3)
    cards = grid.get("cards", [])

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
        add_textbox(
            slide,
            x=0.96,
            y=layout.get("subtitle_y", 0.98),
            w=11.08,
            h=0.40,
            text=subtitle,
            font_name=BODY_FONT,
            font_size=16,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    region_dict = layout.get(
        "grid_region",
        {"x": 0.90, "y": 1.72, "w": 11.20, "h": 3.95},
    )
    region = Box(
        region_dict["x"],
        region_dict["y"],
        region_dict["w"],
        region_dict["h"],
    )
    gap_x = layout.get("gap_x", 0.28)
    gap_y = layout.get("gap_y", 0.28)

    card_w = (region.w - gap_x * (cols - 1)) / cols
    card_h = (region.h - gap_y * (rows - 1)) / rows

    for idx, card in enumerate(cards[: rows * cols]):
        r = idx // cols
        c = idx % cols
        card_box = Box(
            region.x + c * (card_w + gap_x),
            region.y + r * (card_h + gap_y),
            card_w,
            card_h,
        )
        _add_grid_card(slide, card, card_box, idx)

    if takeaway:
        takeaway_y = layout.get("takeaway_y", region.bottom + 0.30)
        takeaway_box = Box(1.02, takeaway_y, 10.96, 0.24)
        takeaway_font = _fit_text_size(
            takeaway,
            takeaway_box,
            min_font=11,
            max_font=13,
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
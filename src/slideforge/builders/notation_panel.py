from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, NAVY, SLATE, TITLE_FONT
from slideforge.io.backgrounds import choose_background
from slideforge.render.primitives import add_divider_line, add_footer, add_rounded_box, add_textbox
from slideforge.utils.text_layout import fit_text_to_box


def _add_grid_card(
    slide,
    card: dict[str, Any],
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
        text=card.get("title", ""),
        width_in=inner_w,
        height_in=0.26,
        min_font_size=13,
        max_font_size=15,
        max_lines=2,
    )

    formula_fit = fit_text_to_box(
        text=card.get("formula", ""),
        width_in=inner_w,
        height_in=0.28,
        min_font_size=12,
        max_font_size=13,
        max_lines=2,
    )

    caption_fit = fit_text_to_box(
        text=card.get("caption", ""),
        width_in=inner_w,
        height_in=0.22,
        min_font_size=11,
        max_font_size=12,
        max_lines=2,
    )

    reserved_h = title_fit.height_in + formula_fit.height_in + caption_fit.height_in + 0.20
    visual_h = max(1.20, inner_h - reserved_h)
    visual_y = inner_y + title_fit.height_in + 0.04

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
        kind=card.get("mini_visual", ""),
        x=inner_x + 0.04,
        y=visual_y,
        w=inner_w - 0.08,
        h=visual_h,
        suffix=f"_card_grid_{idx}",
        variant="dark_on_light",
    )

    formula_y = visual_y + visual_h + 0.04
    add_textbox(
        slide,
        x=inner_x,
        y=formula_y,
        w=inner_w,
        h=formula_fit.height_in + 0.02,
        text=formula_fit.text,
        font_name=FORMULA_FONT,
        font_size=formula_fit.font_size,
        color=NAVY,
        bold=False,
        align=PP_ALIGN.CENTER,
    )

    caption_y = formula_y + formula_fit.height_in + 0.03
    add_textbox(
        slide,
        x=inner_x,
        y=caption_y,
        w=inner_w,
        h=caption_fit.height_in + 0.02,
        text=caption_fit.text,
        font_name=BODY_FONT,
        font_size=caption_fit.font_size,
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
    region = layout.get("grid_region", {"x": 0.90, "y": 1.72, "w": 11.20, "h": 3.95})
    gap_x = layout.get("gap_x", 0.28)
    gap_y = layout.get("gap_y", 0.24)

    add_textbox(
        slide,
        x=0.80,
        y=layout.get("title_y", 0.42),
        w=11.70,
        h=0.50,
        text=spec["title"],
        font_name=TITLE_FONT,
        font_size=25,
        color=NAVY,
        bold=True,
    )
    add_divider_line(slide, dark=False)

    subtitle = spec.get("subtitle", "").strip()
    if subtitle:
        sub_fit = fit_text_to_box(
            text=subtitle,
            width_in=11.0,
            height_in=0.34,
            min_font_size=14,
            max_font_size=16,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=1.00,
            y=layout.get("subtitle_y", 0.98),
            w=11.00,
            h=0.34,
            text=sub_fit.text,
            font_name=BODY_FONT,
            font_size=sub_fit.font_size,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    card_w = (region["w"] - gap_x * (cols - 1)) / cols
    card_h = (region["h"] - gap_y * (rows - 1)) / rows

    for idx, card in enumerate(cards[: rows * cols]):
        r = idx // cols
        c = idx % cols
        card_x = region["x"] + c * (card_w + gap_x)
        card_y = region["y"] + r * (card_h + gap_y)
        _add_grid_card(slide, card, card_x, card_y, card_w, card_h, idx)

    takeaway = spec.get("takeaway", "").strip()
    if takeaway:
        fit = fit_text_to_box(
            text=takeaway,
            width_in=10.95,
            height_in=0.24,
            min_font_size=11,
            max_font_size=13,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=1.05,
            y=layout.get("takeaway_y", 5.98),
            w=10.95,
            h=0.24,
            text=fit.text,
            font_name=BODY_FONT,
            font_size=fit.font_size,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    add_footer(slide, dark=False)
from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, NAVY, SLATE, TITLE_FONT
from slideforge.io.backgrounds import choose_background
from slideforge.render.primitives import add_divider_line, add_footer, add_rounded_box, add_textbox


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

    add_textbox(
        slide,
        x=x + 0.10,
        y=y + 0.10,
        w=w - 0.20,
        h=0.22,
        text=card.get("title", ""),
        font_name=TITLE_FONT,
        font_size=13,
        color=NAVY,
        bold=True,
        align=PP_ALIGN.CENTER,
    )

    add_mini_visual(
        slide,
        kind=card.get("mini_visual", ""),
        x=x + 0.18,
        y=y + 0.38,
        w=w - 0.36,
        h=0.82,
        suffix=f"_card_grid_{idx}",
        variant="dark_on_light",
    )

    add_textbox(
        slide,
        x=x + 0.10,
        y=y + 1.28,
        w=w - 0.20,
        h=0.22,
        text=card.get("formula", ""),
        font_name=FORMULA_FONT,
        font_size=10,
        color=NAVY,
        bold=False,
        align=PP_ALIGN.CENTER,
    )

    add_textbox(
        slide,
        x=x + 0.10,
        y=y + h - 0.28,
        w=w - 0.20,
        h=0.18,
        text=card.get("caption", ""),
        font_name=BODY_FONT,
        font_size=9,
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
    rows = grid.get("rows", 2)
    cols = grid.get("cols", 3)
    cards = grid.get("cards", [])
    region = layout.get("grid_region", {"x": 0.85, "y": 1.55, "w": 11.35, "h": 4.45})
    gap_x = layout.get("gap_x", 0.30)
    gap_y = layout.get("gap_y", 0.34)

    add_textbox(
        slide,
        x=0.80,
        y=layout.get("title_y", 0.42),
        w=11.70,
        h=0.50,
        text=spec["title"],
        font_name=TITLE_FONT,
        font_size=24,
        color=NAVY,
        bold=True,
    )
    add_divider_line(slide, dark=False)

    subtitle = spec.get("subtitle", "").strip()
    if subtitle:
        add_textbox(
            slide,
            x=1.00,
            y=layout.get("subtitle_y", 0.98),
            w=11.00,
            h=0.34,
            text=subtitle,
            font_name=BODY_FONT,
            font_size=14,
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
        add_textbox(
            slide,
            x=1.05,
            y=layout.get("takeaway_y", 6.14),
            w=10.95,
            h=0.20,
            text=takeaway,
            font_name=BODY_FONT,
            font_size=10,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    add_footer(slide, dark=False)
from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, NAVY, SLATE, TITLE_FONT
from slideforge.io.backgrounds import choose_background
from slideforge.render.primitives import add_divider_line, add_footer, add_rounded_box, add_textbox


def _add_prereq_panel(
    slide,
    panel: dict[str, Any],
    x: float,
    y: float,
    w: float,
    h: float,
    idx: int,
) -> None:
    add_rounded_box(slide, x, y, w, h)

    add_textbox(
        slide,
        x=x + 0.12,
        y=y + 0.10,
        w=w - 0.24,
        h=0.24,
        text=panel.get("title", ""),
        font_name=TITLE_FONT,
        font_size=14,
        color=NAVY,
        bold=True,
        align=PP_ALIGN.CENTER,
    )

    add_mini_visual(
        slide,
        kind=panel.get("mini_visual", ""),
        x=x + 0.20,
        y=y + 0.42,
        w=w - 0.40,
        h=0.98,
        suffix=f"_prereq_{idx}",
        variant="dark_on_light",
    )

    add_textbox(
        slide,
        x=x + 0.18,
        y=y + 1.45,
        w=w - 0.36,
        h=0.24,
        text=panel.get("caption", ""),
        font_name=BODY_FONT,
        font_size=11,
        color=SLATE,
        bold=False,
        align=PP_ALIGN.CENTER,
    )

    add_textbox(
        slide,
        x=x + 0.18,
        y=y + 1.72,
        w=w - 0.36,
        h=0.18,
        text=panel.get("formula", ""),
        font_name=FORMULA_FONT,
        font_size=10,
        color=NAVY,
        bold=False,
        align=PP_ALIGN.CENTER,
    )

    anchor = panel.get("anchor", "").strip()
    if anchor:
        add_textbox(
            slide,
            x=x + 0.16,
            y=y + h - 0.22,
            w=w - 0.32,
            h=0.16,
            text=anchor,
            font_name=BODY_FONT,
            font_size=8,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )


def build_prereq_grid_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    theme = spec.get("theme", "concept")
    bg = spec.get("background") or choose_background(theme, counters)
    slide = new_slide(prs, bg)

    layout = spec.get("layout", {})
    region = layout.get("grid_region", {"x": 0.95, "y": 1.45, "w": 11.10, "h": 4.45})
    cols = layout.get("cols", 2)
    rows = layout.get("rows", 2)
    gap_x = layout.get("gap_x", 0.42)
    gap_y = layout.get("gap_y", 0.42)

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
            y=layout.get("subtitle_y", 1.02),
            w=11.00,
            h=0.36,
            text=subtitle,
            font_name=BODY_FONT,
            font_size=15,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    panels = spec.get("panels", [])
    card_w = (region["w"] - gap_x * (cols - 1)) / cols
    card_h = (region["h"] - gap_y * (rows - 1)) / rows

    for idx, panel in enumerate(panels):
        r = idx // cols
        c = idx % cols
        card_x = region["x"] + c * (card_w + gap_x)
        card_y = region["y"] + r * (card_h + gap_y)
        _add_prereq_panel(slide, panel, card_x, card_y, card_w, card_h, idx)

    takeaway = spec.get("takeaway", "").strip()
    if takeaway:
        box = layout.get("takeaway_box", {"x": 1.00, "y": 6.00, "w": 10.90, "h": 0.34})
        add_textbox(
            slide,
            x=box["x"],
            y=box["y"],
            w=box["w"],
            h=box["h"],
            text=takeaway,
            font_name=BODY_FONT,
            font_size=11,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    add_footer(slide, dark=False)
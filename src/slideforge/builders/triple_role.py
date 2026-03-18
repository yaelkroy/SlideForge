from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, NAVY, SLATE, TITLE_FONT
from slideforge.io.backgrounds import choose_background
from slideforge.render.primitives import add_divider_line, add_footer, add_rounded_box, add_textbox


def _add_role_panel(
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
        x=x + 0.10,
        y=y + 0.10,
        w=w - 0.20,
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
        x=x + 0.16,
        y=y + 0.42,
        w=w - 0.32,
        h=1.20,
        suffix=f"_triple_role_{idx}",
        variant="dark_on_light",
    )

    add_textbox(
        slide,
        x=x + 0.12,
        y=y + 1.72,
        w=w - 0.24,
        h=0.30,
        text=panel.get("caption", ""),
        font_name=BODY_FONT,
        font_size=11,
        color=SLATE,
        bold=False,
        align=PP_ALIGN.CENTER,
    )

    add_textbox(
        slide,
        x=x + 0.10,
        y=y + h - 0.28,
        w=w - 0.20,
        h=0.18,
        text=panel.get("formula", ""),
        font_name=FORMULA_FONT,
        font_size=10,
        color=NAVY,
        bold=False,
        align=PP_ALIGN.CENTER,
    )


def build_triple_role_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    theme = spec.get("theme", "concept")
    bg = spec.get("background") or choose_background(theme, counters)
    slide = new_slide(prs, bg)

    layout = spec.get("layout", {})
    panel_region = layout.get("panel_region", {"x": 0.85, "y": 1.75, "w": 11.35, "h": 2.95})
    gap = layout.get("panel_gap", 0.28)
    panels = spec.get("panels", [])
    count = max(1, len(panels))
    panel_w = (panel_region["w"] - gap * (count - 1)) / count

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
            x=1.10,
            y=layout.get("subtitle_y", 1.00),
            w=10.90,
            h=0.36,
            text=subtitle,
            font_name=BODY_FONT,
            font_size=14,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    for idx, panel in enumerate(panels):
        x = panel_region["x"] + idx * (panel_w + gap)
        _add_role_panel(slide, panel, x, panel_region["y"], panel_w, panel_region["h"], idx)

    bullets = spec.get("bullets", [])
    if bullets:
        add_textbox(
            slide,
            x=1.00,
            y=layout.get("bullets_y", 5.10),
            w=11.00,
            h=0.22,
            text="   •   ".join(bullets),
            font_name=BODY_FONT,
            font_size=11,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    formulas = spec.get("formulas", [])
    if formulas:
        add_textbox(
            slide,
            x=1.00,
            y=layout.get("formula_y", 5.52),
            w=11.00,
            h=0.20,
            text="   •   ".join(formulas),
            font_name=FORMULA_FONT,
            font_size=10,
            color=NAVY,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    add_footer(slide, dark=False)
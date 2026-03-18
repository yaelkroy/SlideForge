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

    add_textbox(
        slide,
        x=x + 0.10,
        y=y + 0.10,
        w=w - 0.20,
        h=0.24,
        text=stage.get("title", ""),
        font_name=TITLE_FONT,
        font_size=13,
        color=NAVY,
        bold=True,
        align=PP_ALIGN.CENTER,
    )

    add_mini_visual(
        slide,
        kind=stage.get("mini_visual", ""),
        x=x + 0.14,
        y=y + 0.38,
        w=w - 0.28,
        h=1.15,
        suffix=f"_example_pipeline_{idx}",
        variant="dark_on_light",
    )

    caption = stage.get("caption", "").strip()
    if caption:
        add_textbox(
            slide,
            x=x + 0.12,
            y=y + 1.60,
            w=w - 0.24,
            h=0.28,
            text=caption,
            font_name=BODY_FONT,
            font_size=11,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    formula = stage.get("formula", "").strip()
    if formula:
        add_textbox(
            slide,
            x=x + 0.10,
            y=y + h - 0.28,
            w=w - 0.20,
            h=0.18,
            text=formula,
            font_name=FORMULA_FONT,
            font_size=10,
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
    region = layout.get("pipeline_region", {"x": 0.68, "y": 1.80, "w": 11.70, "h": 2.70})
    gap = layout.get("pipeline_gap", 0.18)

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
            x=0.95,
            y=layout.get("subtitle_y", 0.98),
            w=11.10,
            h=0.40,
            text=subtitle,
            font_name=BODY_FONT,
            font_size=15,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    stages = spec.get("example_pipeline", {}).get("stages", [])
    count = max(1, len(stages))
    card_w = (region["w"] - gap * (count - 1)) / count

    for idx, stage in enumerate(stages):
        card_x = region["x"] + idx * (card_w + gap)
        _add_stage_card(slide, stage, card_x, region["y"], card_w, region["h"], idx)

        if idx < count - 1:
            next_x = region["x"] + (idx + 1) * (card_w + gap)
            add_soft_connector(
                slide,
                x1=card_x + card_w,
                y1=region["y"] + region["h"] / 2,
                x2=next_x,
                y2=region["y"] + region["h"] / 2,
                color=ACCENT,
                width_pt=1.5,
            )

    bullets = spec.get("bullets", [])
    if bullets:
        add_textbox(
            slide,
            x=1.00,
            y=layout.get("bullets_y", 4.84),
            w=11.00,
            h=0.22,
            text="   •   ".join(bullets),
            font_name=BODY_FONT,
            font_size=11,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    takeaway = spec.get("takeaway", "").strip()
    if takeaway:
        add_textbox(
            slide,
            x=1.10,
            y=layout.get("takeaway_y", 5.35),
            w=10.90,
            h=0.42,
            text=takeaway,
            font_name=BODY_FONT,
            font_size=12,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    add_footer(slide, dark=False)
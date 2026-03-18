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
from slideforge.render.primitives import (
    add_divider_line,
    add_footer,
    add_rounded_box,
    add_soft_connector,
    add_textbox,
)


def _pipeline_card(
    slide,
    step: dict[str, Any],
    x: float,
    y: float,
    w: float,
    h: float,
    idx: int,
) -> None:
    add_rounded_box(slide, x, y, w, h)

    add_textbox(
        slide,
        x=x + 0.08,
        y=y + 0.10,
        w=w - 0.16,
        h=0.24,
        text=step.get("title", ""),
        font_name=TITLE_FONT,
        font_size=14,
        color=NAVY,
        bold=True,
        align=PP_ALIGN.CENTER,
    )

    add_mini_visual(
        slide,
        kind=step.get("mini_visual", ""),
        x=x + 0.14,
        y=y + 0.34,
        w=w - 0.28,
        h=1.00,
        suffix=f"_pipeline_{idx}",
        variant="dark_on_light",
    )

    body = step.get("body", "").strip()
    if body:
        add_textbox(
            slide,
            x=x + 0.12,
            y=y + 1.40,
            w=w - 0.24,
            h=0.28,
            text=body,
            font_name=BODY_FONT,
            font_size=11,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    footer = step.get("footer", "").strip()
    if footer:
        add_textbox(
            slide,
            x=x + 0.12,
            y=y + h - 0.28,
            w=w - 0.24,
            h=0.18,
            text=footer,
            font_name=FORMULA_FONT,
            font_size=11,
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
            x=1.05,
            y=layout.get("subtitle_y", 0.98),
            w=10.95,
            h=0.48,
            text=subtitle,
            font_name=BODY_FONT,
            font_size=16,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    region = layout.get(
        "pipeline_region",
        {"x": 0.90, "y": 1.84, "w": 11.20, "h": 2.16},
    )
    gap = layout.get("pipeline_gap", 0.15)

    count = max(1, len(steps))
    card_w = (region["w"] - gap * (count - 1)) / count

    for idx, step in enumerate(steps):
        card_x = region["x"] + idx * (card_w + gap)

        _pipeline_card(
            slide=slide,
            step=step,
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
                width_pt=1.5,
            )

    examples = spec.get("examples", [])
    if examples:
        add_textbox(
            slide,
            x=1.10,
            y=layout.get("examples_y", 4.16),
            w=10.90,
            h=0.20,
            text="Running examples",
            font_name=BODY_FONT,
            font_size=12,
            color=SLATE,
            bold=True,
            align=PP_ALIGN.CENTER,
        )

        ex_y = layout.get("examples_y", 4.16) + 0.22
        ex_w = 4.70
        ex_gap = 0.40
        ex_x0 = 1.25

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
                h=0.88,
                caption=ex_text,
                suffix=f"_pipeline_example_{idx}",
                variant="dark_on_light",
                caption_font_size=11,
            )

    takeaway = spec.get("takeaway", "").strip()
    takeaway_box = layout.get(
        "takeaway_box",
        {"x": 1.00, "y": 5.32, "w": 10.90, "h": 0.72},
    )
    if takeaway:
        add_rounded_box(
            slide,
            takeaway_box["x"],
            takeaway_box["y"],
            takeaway_box["w"],
            takeaway_box["h"],
        )
        add_textbox(
            slide,
            x=takeaway_box["x"] + 0.18,
            y=takeaway_box["y"] + 0.10,
            w=takeaway_box["w"] - 0.36,
            h=takeaway_box["h"] - 0.14,
            text=takeaway,
            font_name=BODY_FONT,
            font_size=13,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    add_footer(slide, dark=False)
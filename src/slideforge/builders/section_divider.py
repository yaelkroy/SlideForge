from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, GHOST_TEXT, OFFWHITE, TITLE_FONT, WHITE
from slideforge.io.backgrounds import choose_background
from slideforge.render.primitives import add_footer, add_ghost_label, add_soft_connector, add_textbox


def build_section_divider_slide(prs: Presentation, spec: dict[str, Any], counters: dict[str, int]) -> None:
    bg = spec.get("background") or choose_background("section", counters)
    slide = new_slide(prs, bg)

    layout = spec.get("layout", {})
    title_region = layout.get("title_region", {"x": 1.0, "y": 2.0, "w": 11.0, "h": 0.9})
    subtitle_region = layout.get("subtitle_region", {"x": 1.45, "y": 2.88, "w": 10.1, "h": 0.40})

    add_textbox(
        slide,
        x=title_region["x"],
        y=title_region["y"],
        w=title_region["w"],
        h=title_region["h"],
        text=spec["title"],
        font_name=TITLE_FONT,
        font_size=26,
        color=WHITE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )

    subtitle = spec.get("subtitle", "").strip()
    if subtitle:
        add_textbox(
            slide,
            x=subtitle_region["x"],
            y=subtitle_region["y"],
            w=subtitle_region["w"],
            h=subtitle_region["h"],
            text=subtitle,
            font_name=BODY_FONT,
            font_size=15,
            color=OFFWHITE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    elements = spec.get("section_visual", {}).get("elements", [])
    previous = None

    for idx, element in enumerate(elements):
        add_mini_visual(
            slide,
            kind=element["kind"],
            x=element["x"],
            y=element["y"],
            w=element["w"],
            h=element["h"],
            suffix=f"_section_{idx}",
            variant="light_on_dark",
        )

        if element.get("label"):
            add_ghost_label(
                slide,
                x=element["x"] + 0.20,
                y=element["y"] + element["h"] + 0.05,
                w=max(1.3, element["w"] - 0.40),
                text=element["label"],
                font_size=10,
            )

        if previous and spec.get("section_visual", {}).get("soft_connector_line", True):
            add_soft_connector(
                slide,
                x1=previous["x"] + previous["w"] + 0.12,
                y1=previous["y"] + previous["h"] / 2,
                x2=element["x"] - 0.10,
                y2=element["y"] + element["h"] / 2,
                color=GHOST_TEXT,
                width_pt=1.0,
            )

        previous = element

    add_footer(slide, dark=True)
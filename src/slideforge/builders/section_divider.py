from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.config.constants import (
    TITLE_FONT,
    BODY_FONT,
    WHITE,
    OFFWHITE,
    GHOST_TEXT,
)
from slideforge.io.backgrounds import choose_background
from slideforge.render.primitives import (
    add_footer,
    add_textbox,
    add_soft_connector,
    add_ghost_label,
)
from slideforge.app.slide_utils import new_slide
from slideforge.assets.mini_visuals import add_mini_visual


def build_section_divider_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    bg = spec.get("background") or choose_background("section", counters)
    slide = new_slide(prs, bg)

    layout = spec.get("layout", {})
    title_region = layout.get(
        "title_region",
        {"x": 1.0, "y": 2.0, "w": 11.0, "h": 0.9},
    )
    subtitle_region = layout.get(
        "subtitle_region",
        {"x": 1.45, "y": 2.9, "w": 10.1, "h": 0.4},
    )

    # Title
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

    # Subtitle
    subtitle = spec.get("subtitle", "")
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

    if len(elements) >= 3:
        left, middle, right = elements[:3]

        add_mini_visual(
            slide,
            kind=left["kind"],
            x=left["x"],
            y=left["y"],
            w=left["w"],
            h=left["h"],
            suffix="_section_left",
        )
        add_mini_visual(
            slide,
            kind=middle["kind"],
            x=middle["x"],
            y=middle["y"],
            w=middle["w"],
            h=middle["h"],
            suffix="_section_mid",
        )
        add_mini_visual(
            slide,
            kind=right["kind"],
            x=right["x"],
            y=right["y"],
            w=right["w"],
            h=right["h"],
            suffix="_section_right",
        )

        # small decorative labels under visuals
        add_ghost_label(
            slide,
            x=left["x"] + 0.35,
            y=left["y"] + left["h"] + 0.06,
            w=1.4,
            text=left.get("label", "vector"),
            font_size=10,
        )
        add_ghost_label(
            slide,
            x=middle["x"] + 0.30,
            y=middle["y"] + middle["h"] + 0.06,
            w=1.4,
            text=middle.get("label", "hyperplane"),
            font_size=10,
        )
        add_ghost_label(
            slide,
            x=right["x"] + 0.28,
            y=right["y"] + right["h"] + 0.06,
            w=1.5,
            text=right.get("label", "classifier"),
            font_size=10,
        )

        if spec.get("section_visual", {}).get("soft_connector_line", True):
            add_soft_connector(
                slide,
                x1=left["x"] + left["w"] + 0.20,
                y1=left["y"] + left["h"] / 2,
                x2=right["x"] - 0.10,
                y2=right["y"] + right["h"] / 2,
                color=GHOST_TEXT,
                width_pt=1.0,
            )

    add_footer(slide, dark=True)
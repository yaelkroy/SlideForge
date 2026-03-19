from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, OFFWHITE, TITLE_FONT
from slideforge.io.backgrounds import choose_background
from slideforge.render.primitives import add_footer, add_textbox
from slideforge.utils.text_layout import fit_text_to_box


def build_section_divider_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    theme = spec.get("theme", "section")
    bg = spec.get("background") or choose_background(theme, counters)
    slide = new_slide(prs, bg)

    layout = spec.get("layout", {})
    title_region = layout.get("title_region", {"x": 1.0, "y": 2.0, "w": 11.0, "h": 0.9})
    subtitle_region = layout.get("subtitle_region", {"x": 1.2, "y": 2.9, "w": 10.6, "h": 0.40})

    title_fit = fit_text_to_box(
        text=spec.get("title", ""),
        width_in=title_region["w"],
        height_in=title_region["h"],
        min_font_size=28,
        max_font_size=34,
        max_lines=2,
    )
    add_textbox(
        slide,
        x=title_region["x"],
        y=title_region["y"],
        w=title_region["w"],
        h=title_region["h"],
        text=title_fit.text,
        font_name=TITLE_FONT,
        font_size=title_fit.font_size,
        color=OFFWHITE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )

    subtitle = spec.get("subtitle", "").strip()
    if subtitle:
        sub_fit = fit_text_to_box(
            text=subtitle,
            width_in=subtitle_region["w"],
            height_in=subtitle_region["h"],
            min_font_size=15,
            max_font_size=18,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=subtitle_region["x"],
            y=subtitle_region["y"],
            w=subtitle_region["w"],
            h=subtitle_region["h"],
            text=sub_fit.text,
            font_name=BODY_FONT,
            font_size=sub_fit.font_size,
            color=OFFWHITE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    section_visual = spec.get("section_visual", {})
    elements = section_visual.get("elements", [])

    for idx, element in enumerate(elements):
        add_mini_visual(
            slide,
            kind=element.get("kind", ""),
            x=element["x"],
            y=element["y"],
            w=element["w"],
            h=element["h"],
            suffix=f"_section_divider_{idx}",
            variant="light_on_dark",
        )

        label = element.get("label", "").strip()
        if label:
            label_y = element["y"] + element["h"] + 0.06
            add_textbox(
                slide,
                x=element["x"],
                y=label_y,
                w=element["w"],
                h=0.18,
                text=label,
                font_name=BODY_FONT,
                font_size=12,
                color=OFFWHITE,
                bold=False,
                align=PP_ALIGN.CENTER,
            )

    add_footer(slide, dark=True)
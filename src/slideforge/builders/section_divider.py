from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, NAVY, OFFWHITE, TITLE_FONT
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, fit_text
from slideforge.render.primitives import add_footer, add_textbox


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


def build_section_divider_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    theme = spec.get("theme", "section")
    bg = spec.get("background") or choose_background(theme, counters)
    slide = new_slide(prs, bg)

    title = spec.get("title") or spec["slide_title"]
    subtitle = spec.get("subtitle", "").strip()
    layout = spec.get("layout", {})
    section_visual = spec.get("section_visual", {})

    title_region_dict = layout.get(
        "title_region",
        {"x": 1.00, "y": 1.95, "w": 11.00, "h": 0.92},
    )
    subtitle_region_dict = layout.get(
        "subtitle_region",
        {"x": 1.20, "y": 2.90, "w": 10.60, "h": 0.42},
    )
    band_dict = layout.get(
        "band_region",
        {"x": 0.90, "y": 3.52, "w": 11.55, "h": 1.52},
    )

    title_box = Box(
        title_region_dict["x"],
        title_region_dict["y"],
        title_region_dict["w"],
        title_region_dict["h"],
    )
    subtitle_box = Box(
        subtitle_region_dict["x"],
        subtitle_region_dict["y"],
        subtitle_region_dict["w"],
        subtitle_region_dict["h"],
    )
    band_box = Box(
        band_dict["x"],
        band_dict["y"],
        band_dict["w"],
        band_dict["h"],
    )

    title_font = _fit_text_size(
        title,
        title_box,
        min_font=28,
        max_font=34,
        max_lines=2,
    )
    add_textbox(
        slide,
        x=title_box.x,
        y=title_box.y,
        w=title_box.w,
        h=title_box.h,
        text=title,
        font_name=TITLE_FONT,
        font_size=title_font,
        color=OFFWHITE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )

    if subtitle:
        subtitle_font = _fit_text_size(
            subtitle,
            subtitle_box,
            min_font=15,
            max_font=18,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=subtitle_box.x,
            y=subtitle_box.y,
            w=subtitle_box.w,
            h=subtitle_box.h,
            text=subtitle,
            font_name=BODY_FONT,
            font_size=subtitle_font,
            color=OFFWHITE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    elements = section_visual.get("elements", [])
    count = len(elements)

    if count > 0:
        side_pad = layout.get("band_side_pad", 0.35)
        inter_gap = layout.get("band_gap", 0.30)
        usable_w = band_box.w - 2 * side_pad - inter_gap * max(0, count - 1)
        elem_w = usable_w / count if count else usable_w
        elem_h = layout.get("element_h", min(1.24, band_box.h - 0.22))
        elem_y = band_box.y + (band_box.h - elem_h) / 2

        label_h = layout.get("label_h", 0.22)
        label_gap = layout.get("label_gap", 0.06)
        visual_h = max(0.60, elem_h - label_h - label_gap)

        for idx, elem in enumerate(elements):
            x = band_box.x + side_pad + idx * (elem_w + inter_gap)
            visual_y = elem_y
            label = elem.get("label", "").strip()

            if label:
                visual_y = elem_y
                add_mini_visual(
                    slide,
                    kind=elem.get("kind", ""),
                    x=x,
                    y=visual_y,
                    w=elem_w,
                    h=visual_h,
                    suffix=f"_section_divider_{idx}",
                    variant="light_on_dark",
                )

                label_box = Box(x, visual_y + visual_h + label_gap, elem_w, label_h)
                label_font = _fit_text_size(
                    label,
                    label_box,
                    min_font=12,
                    max_font=15,
                    max_lines=1,
                )
                add_textbox(
                    slide,
                    x=label_box.x,
                    y=label_box.y,
                    w=label_box.w,
                    h=label_box.h,
                    text=label,
                    font_name=BODY_FONT,
                    font_size=label_font,
                    color=OFFWHITE,
                    bold=False,
                    align=PP_ALIGN.CENTER,
                )
            else:
                add_mini_visual(
                    slide,
                    kind=elem.get("kind", ""),
                    x=x,
                    y=elem_y + (elem_h - visual_h) / 2,
                    w=elem_w,
                    h=visual_h,
                    suffix=f"_section_divider_{idx}",
                    variant="light_on_dark",
                )

    faint_words = spec.get("concrete_example_anchor", "").strip()
    if faint_words:
        words_box = Box(
            1.10,
            layout.get("faint_words_y", 5.82),
            11.00,
            0.22,
        )
        words_font = _fit_text_size(
            faint_words,
            words_box,
            min_font=11,
            max_font=14,
            max_lines=1,
        )
        add_textbox(
            slide,
            x=words_box.x,
            y=words_box.y,
            w=words_box.w,
            h=words_box.h,
            text=faint_words,
            font_name=BODY_FONT,
            font_size=words_font,
            color=OFFWHITE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    add_footer(slide, dark=True)
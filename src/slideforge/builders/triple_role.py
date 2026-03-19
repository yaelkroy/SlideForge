from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, NAVY, SLATE, TITLE_FONT
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, fit_text
from slideforge.render.primitives import add_divider_line, add_footer, add_rounded_box, add_textbox


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


def _join_items(items: list[str]) -> str:
    return "   •   ".join(item.strip() for item in items if item and item.strip())


def _add_role_panel(
    slide,
    panel: dict[str, Any],
    panel_box: Box,
    idx: int,
) -> None:
    add_rounded_box(slide, panel_box.x, panel_box.y, panel_box.w, panel_box.h)

    title_text = panel.get("title", "").strip()
    caption_text = panel.get("caption", "").strip()
    formula_text = panel.get("formula", "").strip()

    title_box = Box(panel_box.x + 0.10, panel_box.y + 0.10, panel_box.w - 0.20, 0.24)
    title_font = _fit_text_size(
        title_text,
        title_box,
        min_font=12,
        max_font=15,
        max_lines=2,
    )
    add_textbox(
        slide,
        x=title_box.x,
        y=title_box.y,
        w=title_box.w,
        h=title_box.h,
        text=title_text,
        font_name=TITLE_FONT,
        font_size=title_font,
        color=NAVY,
        bold=True,
        align=PP_ALIGN.CENTER,
    )

    # Keep the visual centered and large inside the panel.
    top_pad = 0.10
    title_h = 0.24
    above_gap = 0.10
    caption_h = 0.22 if caption_text else 0.0
    formula_h = 0.18 if formula_text else 0.0
    below_gap = 0.08
    bottom_pad = 0.12

    visual_h = panel_box.h - (
        top_pad + title_h + above_gap + caption_h + formula_h + below_gap + bottom_pad
    )
    visual_h = max(0.85, visual_h)

    visual_box = Box(
        panel_box.x + 0.14,
        panel_box.y + top_pad + title_h + above_gap,
        panel_box.w - 0.28,
        visual_h,
    )

    add_mini_visual(
        slide,
        kind=panel.get("mini_visual", ""),
        x=visual_box.x,
        y=visual_box.y,
        w=visual_box.w,
        h=visual_box.h,
        suffix=f"_triple_role_{idx}",
        variant="dark_on_light",
    )

    current_y = visual_box.bottom + 0.08

    if caption_text:
        caption_box = Box(panel_box.x + 0.12, current_y, panel_box.w - 0.24, 0.22)
        caption_font = _fit_text_size(
            caption_text,
            caption_box,
            min_font=11,
            max_font=13,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=caption_box.x,
            y=caption_box.y,
            w=caption_box.w,
            h=caption_box.h,
            text=caption_text,
            font_name=BODY_FONT,
            font_size=caption_font,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )
        current_y += 0.22 + 0.04

    if formula_text:
        formula_box = Box(panel_box.x + 0.10, current_y, panel_box.w - 0.20, 0.18)
        formula_font = _fit_text_size(
            formula_text,
            formula_box,
            min_font=11,
            max_font=13,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=formula_box.x,
            y=formula_box.y,
            w=formula_box.w,
            h=formula_box.h,
            text=formula_text,
            font_name=FORMULA_FONT,
            font_size=formula_font,
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
    title = spec.get("title") or spec["slide_title"]
    subtitle = spec.get("subtitle", "").strip()
    panels = spec.get("panels", [])
    bullets = spec.get("bullets", [])
    formulas = spec.get("formulas", [])
    takeaway = spec.get("takeaway", "").strip()

    add_textbox(
        slide,
        x=0.80,
        y=layout.get("title_y", 0.42),
        w=11.70,
        h=0.52,
        text=title,
        font_name=TITLE_FONT,
        font_size=27,
        color=NAVY,
        bold=True,
    )
    add_divider_line(slide, dark=False)

    if subtitle:
        subtitle_box = Box(1.00, layout.get("subtitle_y", 0.98), 11.00, 0.40)
        subtitle_font = _fit_text_size(
            subtitle,
            subtitle_box,
            min_font=15,
            max_font=17,
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
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    region_dict = layout.get(
        "panel_region",
        {"x": 0.88, "y": 1.78, "w": 11.24, "h": 3.05},
    )
    region = Box(
        region_dict["x"],
        region_dict["y"],
        region_dict["w"],
        region_dict["h"],
    )
    gap = layout.get("panel_gap", 0.24)

    count = max(1, len(panels))
    panel_w = (region.w - gap * (count - 1)) / count

    for idx, panel in enumerate(panels):
        panel_box = Box(
            region.x + idx * (panel_w + gap),
            region.y,
            panel_w,
            region.h,
        )
        _add_role_panel(slide, panel, panel_box, idx)

    if bullets:
        bullets_text = _join_items(bullets)
        bullets_box = Box(1.02, layout.get("bullets_y", 5.16), 10.96, 0.24)
        bullets_font = _fit_text_size(
            bullets_text,
            bullets_box,
            min_font=12,
            max_font=14,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=bullets_box.x,
            y=bullets_box.y,
            w=bullets_box.w,
            h=bullets_box.h,
            text=bullets_text,
            font_name=BODY_FONT,
            font_size=bullets_font,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    if formulas:
        formulas_text = _join_items(formulas)
        formulas_box = Box(1.02, layout.get("formula_y", 5.56), 10.96, 0.20)
        formulas_font = _fit_text_size(
            formulas_text,
            formulas_box,
            min_font=12,
            max_font=14,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=formulas_box.x,
            y=formulas_box.y,
            w=formulas_box.w,
            h=formulas_box.h,
            text=formulas_text,
            font_name=FORMULA_FONT,
            font_size=formulas_font,
            color=NAVY,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    if takeaway:
        takeaway_box = Box(1.02, layout.get("takeaway_y", 5.98), 10.96, 0.24)
        takeaway_font = _fit_text_size(
            takeaway,
            takeaway_box,
            min_font=12,
            max_font=14,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=takeaway_box.x,
            y=takeaway_box.y,
            w=takeaway_box.w,
            h=takeaway_box.h,
            text=takeaway,
            font_name=BODY_FONT,
            font_size=takeaway_font,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    add_footer(slide, dark=False)
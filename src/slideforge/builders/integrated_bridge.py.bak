from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import ACCENT, BODY_FONT, FORMULA_FONT, NAVY, SLATE, TITLE_FONT
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, fit_text
from slideforge.render.primitives import (
    add_divider_line,
    add_footer,
    add_rounded_box,
    add_soft_connector,
    add_textbox,
)


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


def _add_role_box(
    slide,
    *,
    role: dict[str, Any],
    box: Box,
    suffix: str,
) -> None:
    add_rounded_box(slide, box.x, box.y, box.w, box.h)

    title_text = role.get("title", "").strip()
    caption_text = role.get("caption", "").strip()

    title_box = Box(box.x + 0.10, box.y + 0.10, box.w - 0.20, 0.24)
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

    top_pad = 0.10
    title_h = 0.24
    above_gap = 0.10
    caption_h = 0.26 if caption_text else 0.0
    below_gap = 0.10
    bottom_pad = 0.12

    visual_h = box.h - (top_pad + title_h + above_gap + caption_h + below_gap + bottom_pad)
    visual_h = max(0.90, visual_h)

    visual_box = Box(
        box.x + 0.14,
        box.y + top_pad + title_h + above_gap,
        box.w - 0.28,
        visual_h,
    )

    add_mini_visual(
        slide,
        kind=role.get("mini_visual", ""),
        x=visual_box.x,
        y=visual_box.y,
        w=visual_box.w,
        h=visual_box.h,
        suffix=suffix,
        variant="dark_on_light",
    )

    if caption_text:
        caption_box = Box(box.x + 0.12, visual_box.bottom + 0.08, box.w - 0.24, 0.26)
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


def build_integrated_bridge_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    theme = spec.get("theme", "concept")
    bg = spec.get("background") or choose_background(theme, counters)
    slide = new_slide(prs, bg)

    layout = spec.get("layout", {})
    visual = spec.get("integrated_visual", {})

    title = spec.get("title") or spec["slide_title"]
    subtitle = spec.get("subtitle", "").strip()
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

    base_object = visual.get("base_object", "").strip()
    if base_object:
        base_box = Box(3.80, layout.get("base_object_y", 1.38), 5.70, 0.22)
        base_font = _fit_text_size(
            base_object,
            base_box,
            min_font=13,
            max_font=15,
            max_lines=1,
        )
        add_textbox(
            slide,
            x=base_box.x,
            y=base_box.y,
            w=base_box.w,
            h=base_box.h,
            text=base_object,
            font_name=FORMULA_FONT,
            font_size=base_font,
            color=NAVY,
            bold=True,
            align=PP_ALIGN.CENTER,
        )

    visual_y = layout.get("visual_y", 1.80)
    panel_h = layout.get("panel_h", 2.78)
    gap = layout.get("panel_gap", 0.34)
    side_pad = layout.get("side_pad", 0.88)
    total_w = 13.333 - 2 * side_pad
    panel_w = (total_w - 2 * gap) / 3

    left_box = Box(side_pad, visual_y, panel_w, panel_h)
    center_box = Box(side_pad + panel_w + gap, visual_y, panel_w, panel_h)
    right_box = Box(side_pad + 2 * (panel_w + gap), visual_y, panel_w, panel_h)

    left_role = visual.get("left_role", {})
    center_role = visual.get("center_role", {})
    right_role = visual.get("right_role", {})

    _add_role_box(slide, role=left_role, box=left_box, suffix="_bridge_left")
    _add_role_box(slide, role=center_role, box=center_box, suffix="_bridge_center")
    _add_role_box(slide, role=right_role, box=right_box, suffix="_bridge_right")

    add_soft_connector(
        slide,
        x1=left_box.right,
        y1=left_box.y + left_box.h / 2,
        x2=center_box.x,
        y2=center_box.y + center_box.h / 2,
        color=ACCENT,
        width_pt=1.7,
    )
    add_soft_connector(
        slide,
        x1=center_box.right,
        y1=center_box.y + center_box.h / 2,
        x2=right_box.x,
        y2=right_box.y + right_box.h / 2,
        color=ACCENT,
        width_pt=1.7,
    )

    bridge_labels = visual.get("bridge_labels", [])
    if bridge_labels:
        label_y_top = visual_y + 0.06
        label_y_bottom = visual_y + panel_h + 0.04

        positions = [
            Box(left_box.right + 0.02, label_y_top, gap - 0.04, 0.18),
            Box(center_box.right + 0.02, label_y_top, gap - 0.04, 0.18),
            Box(4.50, label_y_bottom, 4.30, 0.18),
        ]

        for idx, label in enumerate(bridge_labels[:3]):
            label_box = positions[idx]
            label_font = _fit_text_size(
                label,
                label_box,
                min_font=10,
                max_font=12,
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
                color=SLATE,
                bold=False,
                align=PP_ALIGN.CENTER,
            )

    if formulas:
        formulas_text = _join_items(formulas)
        formulas_box = Box(1.02, layout.get("formula_y", 4.86), 10.96, 0.22)
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
        takeaway_box = Box(1.02, layout.get("takeaway_y", 5.32), 10.96, 0.34)
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
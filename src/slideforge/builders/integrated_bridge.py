from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import ACCENT, BODY_FONT, FORMULA_FONT, NAVY, SLATE, TITLE_FONT
from slideforge.io.backgrounds import choose_background
from slideforge.render.primitives import add_divider_line, add_footer, add_rounded_box, add_soft_connector, add_textbox
from slideforge.utils.text_layout import fit_joined_items_to_box, fit_text_to_box


def _add_role_box(
    slide,
    role: dict[str, Any],
    x: float,
    y: float,
    w: float,
    h: float,
    suffix: str,
) -> None:
    add_rounded_box(slide, x, y, w, h)

    inner_x = x + 0.12
    inner_y = y + 0.10
    inner_w = w - 0.24
    inner_h = h - 0.20

    title_fit = fit_text_to_box(
        text=role.get("title", ""),
        width_in=inner_w,
        height_in=0.24,
        min_font_size=13,
        max_font_size=15,
        max_lines=2,
    )
    caption_fit = fit_text_to_box(
        text=role.get("caption", ""),
        width_in=inner_w,
        height_in=0.28,
        min_font_size=11,
        max_font_size=13,
        max_lines=2,
    )

    visual_h = max(1.20, inner_h - title_fit.height_in - caption_fit.height_in - 0.12)
    visual_y = inner_y + title_fit.height_in + 0.04

    add_textbox(
        slide,
        x=inner_x,
        y=inner_y,
        w=inner_w,
        h=title_fit.height_in + 0.02,
        text=title_fit.text,
        font_name=TITLE_FONT,
        font_size=title_fit.font_size,
        color=NAVY,
        bold=True,
        align=PP_ALIGN.CENTER,
    )

    add_mini_visual(
        slide,
        kind=role.get("mini_visual", ""),
        x=inner_x + 0.04,
        y=visual_y,
        w=inner_w - 0.08,
        h=visual_h,
        suffix=suffix,
        variant="dark_on_light",
    )

    add_textbox(
        slide,
        x=inner_x,
        y=visual_y + visual_h + 0.04,
        w=inner_w,
        h=caption_fit.height_in + 0.02,
        text=caption_fit.text,
        font_name=BODY_FONT,
        font_size=caption_fit.font_size,
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
    left = visual.get("left_role", {})
    center = visual.get("center_role", {})
    right = visual.get("right_role", {})
    bridge_labels = visual.get("bridge_labels", [])

    add_textbox(
        slide,
        x=0.80,
        y=layout.get("title_y", 0.42),
        w=11.70,
        h=0.50,
        text=spec["title"],
        font_name=TITLE_FONT,
        font_size=25,
        color=NAVY,
        bold=True,
    )
    add_divider_line(slide, dark=False)

    subtitle = spec.get("subtitle", "").strip()
    if subtitle:
        fit = fit_text_to_box(
            text=subtitle,
            width_in=11.0,
            height_in=0.34,
            min_font_size=14,
            max_font_size=16,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=1.00,
            y=layout.get("subtitle_y", 0.98),
            w=11.00,
            h=0.34,
            text=fit.text,
            font_name=BODY_FONT,
            font_size=fit.font_size,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    base_object = visual.get("base_object", "").strip()
    if base_object:
        fit = fit_text_to_box(
            text=base_object,
            width_in=4.80,
            height_in=0.22,
            min_font_size=13,
            max_font_size=15,
            max_lines=1,
        )
        add_textbox(
            slide,
            x=4.20,
            y=1.40,
            w=4.80,
            h=0.22,
            text=fit.text,
            font_name=FORMULA_FONT,
            font_size=fit.font_size,
            color=NAVY,
            bold=True,
            align=PP_ALIGN.CENTER,
        )

    y = layout.get("visual_y", 1.80)
    w = 3.12
    h = 2.26
    left_x = 0.95
    center_x = 4.94
    right_x = 8.93

    _add_role_box(slide, left, left_x, y, w, h, "_bridge_left")
    _add_role_box(slide, center, center_x, y, w, h, "_bridge_center")
    _add_role_box(slide, right, right_x, y, w, h, "_bridge_right")

    add_soft_connector(
        slide,
        x1=left_x + w,
        y1=y + h / 2,
        x2=center_x,
        y2=y + h / 2,
        color=ACCENT,
        width_pt=1.6,
    )
    add_soft_connector(
        slide,
        x1=center_x + w,
        y1=y + h / 2,
        x2=right_x,
        y2=y + h / 2,
        color=ACCENT,
        width_pt=1.6,
    )

    if bridge_labels:
        positions = [
            (3.58, y + 0.06, 1.80),
            (7.56, y + 0.06, 1.80),
            (4.75, y + h + 0.02, 3.00),
        ]
        for idx, label in enumerate(bridge_labels[:3]):
            lx, ly, lw = positions[idx]
            fit = fit_text_to_box(
                text=label,
                width_in=lw,
                height_in=0.18,
                min_font_size=10,
                max_font_size=11,
                max_lines=1,
            )
            add_textbox(
                slide,
                x=lx,
                y=ly,
                w=lw,
                h=0.18,
                text=fit.text,
                font_name=BODY_FONT,
                font_size=fit.font_size,
                color=SLATE,
                bold=False,
                align=PP_ALIGN.CENTER,
            )

    formulas = spec.get("formulas", [])
    if formulas:
        fit = fit_joined_items_to_box(
            items=formulas,
            width_in=10.9,
            height_in=0.22,
            min_font_size=12,
            max_font_size=13,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=1.10,
            y=layout.get("formula_y", 4.72),
            w=10.90,
            h=0.22,
            text=fit.text,
            font_name=FORMULA_FONT,
            font_size=fit.font_size,
            color=NAVY,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    takeaway = spec.get("takeaway", "").strip()
    if takeaway:
        fit = fit_text_to_box(
            text=takeaway,
            width_in=10.9,
            height_in=0.34,
            min_font_size=12,
            max_font_size=14,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=1.10,
            y=layout.get("takeaway_y", 5.34),
            w=10.90,
            h=0.34,
            text=fit.text,
            font_name=BODY_FONT,
            font_size=fit.font_size,
            color=SLATE,
            bold=True,
            align=PP_ALIGN.CENTER,
        )

    add_footer(slide, dark=False)
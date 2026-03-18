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

    add_textbox(
        slide,
        x=x + 0.10,
        y=y + 0.10,
        w=w - 0.20,
        h=0.22,
        text=role.get("title", ""),
        font_name=TITLE_FONT,
        font_size=14,
        color=NAVY,
        bold=True,
        align=PP_ALIGN.CENTER,
    )

    add_mini_visual(
        slide,
        kind=role.get("mini_visual", ""),
        x=x + 0.16,
        y=y + 0.40,
        w=w - 0.32,
        h=1.00,
        suffix=suffix,
        variant="dark_on_light",
    )

    add_textbox(
        slide,
        x=x + 0.10,
        y=y + 1.50,
        w=w - 0.20,
        h=0.28,
        text=role.get("caption", ""),
        font_name=BODY_FONT,
        font_size=10,
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
            y=layout.get("subtitle_y", 0.98),
            w=10.90,
            h=0.34,
            text=subtitle,
            font_name=BODY_FONT,
            font_size=14,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    base_object = visual.get("base_object", "").strip()
    if base_object:
        add_textbox(
            slide,
            x=4.30,
            y=1.38,
            w=4.70,
            h=0.22,
            text=base_object,
            font_name=FORMULA_FONT,
            font_size=13,
            color=NAVY,
            bold=True,
            align=PP_ALIGN.CENTER,
        )

    y = layout.get("visual_y", 1.78)
    w = 3.15
    h = 2.05
    left_x = 0.90
    center_x = 5.08
    right_x = 9.26

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
        width_pt=1.5,
    )
    add_soft_connector(
        slide,
        x1=center_x + w,
        y1=y + h / 2,
        x2=right_x,
        y2=y + h / 2,
        color=ACCENT,
        width_pt=1.5,
    )

    if bridge_labels:
        positions = [
            (3.92, y + 0.18),
            (7.98, y + 0.18),
            (5.30, y + h + 0.10),
        ]
        for idx, label in enumerate(bridge_labels[:3]):
            lx, ly = positions[idx]
            add_textbox(
                slide,
                x=lx,
                y=ly,
                w=1.90 if idx < 2 else 2.80,
                h=0.18,
                text=label,
                font_name=BODY_FONT,
                font_size=9,
                color=SLATE,
                bold=False,
                align=PP_ALIGN.CENTER,
            )

    formulas = spec.get("formulas", [])
    if formulas:
        add_textbox(
            slide,
            x=1.10,
            y=layout.get("formula_y", 4.55),
            w=10.90,
            h=0.20,
            text="   •   ".join(formulas),
            font_name=FORMULA_FONT,
            font_size=10,
            color=NAVY,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    takeaway = spec.get("takeaway", "").strip()
    if takeaway:
        add_textbox(
            slide,
            x=1.10,
            y=layout.get("takeaway_y", 5.22),
            w=10.90,
            h=0.36,
            text=takeaway,
            font_name=BODY_FONT,
            font_size=12,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    add_footer(slide, dark=False)
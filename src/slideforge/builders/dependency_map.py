from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

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
    cleaned = [item.strip() for item in items if item and item.strip()]
    return "   •   ".join(cleaned)


def _add_node(
    slide,
    *,
    box: Box,
    text: str,
    font_name: str,
    min_font: int,
    max_font: int,
    color,
    bold: bool,
    align=PP_ALIGN.CENTER,
) -> None:
    add_rounded_box(slide, box.x, box.y, box.w, box.h)

    text_box = Box(box.x + 0.10, box.y + 0.08, box.w - 0.20, box.h - 0.16)
    font_size = _fit_text_size(
        text,
        text_box,
        min_font=min_font,
        max_font=max_font,
        max_lines=3,
    )
    add_textbox(
        slide,
        x=text_box.x,
        y=text_box.y,
        w=text_box.w,
        h=text_box.h,
        text=text,
        font_name=font_name,
        font_size=font_size,
        color=color,
        bold=bold,
        align=align,
    )


def _center_of(box: Box) -> tuple[float, float]:
    return (box.x + box.w / 2, box.y + box.h / 2)


def build_dependency_map_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    theme = spec.get("theme", "concept")
    bg = spec.get("background") or choose_background(theme, counters)
    slide = new_slide(prs, bg)

    title = spec.get("title") or spec["slide_title"]
    subtitle = spec.get("subtitle", "").strip()
    formulas = spec.get("formulas", [])
    takeaway = spec.get("takeaway", "").strip()
    explanation = spec.get("explanation_box", {}) or {}
    diagram = spec.get("diagram", {}) or {}
    layout = spec.get("layout", {}) or {}

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
        subtitle_box = Box(0.96, layout.get("subtitle_y", 0.98), 11.08, 0.40)
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

    center_node = diagram.get("center_node", {})
    input_nodes = diagram.get("input_nodes", [])

    center_box = Box(
        center_node.get("x", 4.10),
        center_node.get("y", 2.55),
        center_node.get("w", 2.05),
        center_node.get("h", 1.02),
    )

    input_boxes: list[Box] = []
    for node in input_nodes:
        input_boxes.append(
            Box(
                node.get("x", 1.20),
                node.get("y", 1.40),
                node.get("w", 2.20),
                node.get("h", 0.92),
            )
        )

    # Draw connectors first so nodes sit on top.
    cx, cy = _center_of(center_box)
    connector_width = layout.get("connector_width_pt", 1.5)

    for box in input_boxes:
        x1, y1 = _center_of(box)
        add_soft_connector(
            slide,
            x1=x1,
            y1=y1,
            x2=cx,
            y2=cy,
            color=ACCENT,
            width_pt=connector_width,
        )

    # Input nodes
    for node, box in zip(input_nodes, input_boxes):
        _add_node(
            slide,
            box=box,
            text=node.get("label", ""),
            font_name=BODY_FONT,
            min_font=12,
            max_font=node.get("font_size", 14),
            color=NAVY,
            bold=True,
            align=PP_ALIGN.CENTER,
        )

    # Central node
    _add_node(
        slide,
        box=center_box,
        text=center_node.get("label", "Machine\nLearning"),
        font_name=TITLE_FONT,
        min_font=16,
        max_font=center_node.get("font_size", 19),
        color=NAVY,
        bold=True,
        align=PP_ALIGN.CENTER,
    )

    # Explanation box on the right
    explanation_text = explanation.get("text", "").strip()
    explanation_title = explanation.get("title", "").strip()
    if explanation_text:
        exp_dict = layout.get("explanation_box", {"x": 8.55, "y": 2.05, "w": 3.35, "h": 1.18})
        exp_box = Box(exp_dict["x"], exp_dict["y"], exp_dict["w"], exp_dict["h"])
        add_rounded_box(slide, exp_box.x, exp_box.y, exp_box.w, exp_box.h)

        if explanation_title:
            title_box = Box(exp_box.x + 0.12, exp_box.y + 0.10, exp_box.w - 0.24, 0.22)
            title_font = _fit_text_size(
                explanation_title,
                title_box,
                min_font=12,
                max_font=14,
                max_lines=2,
            )
            add_textbox(
                slide,
                x=title_box.x,
                y=title_box.y,
                w=title_box.w,
                h=title_box.h,
                text=explanation_title,
                font_name=BODY_FONT,
                font_size=title_font,
                color=NAVY,
                bold=True,
                align=PP_ALIGN.CENTER,
            )
            body_y = title_box.bottom + 0.05
            body_h = exp_box.bottom - body_y - 0.10
        else:
            body_y = exp_box.y + 0.10
            body_h = exp_box.h - 0.20

        body_box = Box(exp_box.x + 0.14, body_y, exp_box.w - 0.28, body_h)
        body_font = _fit_text_size(
            explanation_text,
            body_box,
            min_font=12,
            max_font=14,
            max_lines=5,
        )
        add_textbox(
            slide,
            x=body_box.x,
            y=body_box.y,
            w=body_box.w,
            h=body_box.h,
            text=explanation_text,
            font_name=BODY_FONT,
            font_size=body_font,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    # Optional right-panel bullets if a spec still uses them.
    right_panel_bullets = spec.get("right_panel_bullets", []) or []
    right_panel_title = spec.get("right_panel_title", "").strip()
    if right_panel_bullets:
        rp_dict = layout.get("bullets_box", {"x": 8.55, "y": 3.55, "w": 3.35, "h": 1.55})
        rp_box = Box(rp_dict["x"], rp_dict["y"], rp_dict["w"], rp_dict["h"])
        add_rounded_box(slide, rp_box.x, rp_box.y, rp_box.w, rp_box.h)

        current_y = rp_box.y + 0.10
        if right_panel_title:
            header_box = Box(rp_box.x + 0.12, current_y, rp_box.w - 0.24, 0.22)
            header_font = _fit_text_size(
                right_panel_title,
                header_box,
                min_font=12,
                max_font=14,
                max_lines=2,
            )
            add_textbox(
                slide,
                x=header_box.x,
                y=header_box.y,
                w=header_box.w,
                h=header_box.h,
                text=right_panel_title,
                font_name=BODY_FONT,
                font_size=header_font,
                color=NAVY,
                bold=True,
                align=PP_ALIGN.CENTER,
            )
            current_y += 0.26

        bullet_text = "\n".join(f"• {item}" for item in right_panel_bullets if item.strip())
        bullet_box = Box(rp_box.x + 0.14, current_y, rp_box.w - 0.28, rp_box.bottom - current_y - 0.10)
        bullet_font = _fit_text_size(
            bullet_text,
            bullet_box,
            min_font=11,
            max_font=13,
            max_lines=8,
        )
        add_textbox(
            slide,
            x=bullet_box.x,
            y=bullet_box.y,
            w=bullet_box.w,
            h=bullet_box.h,
            text=bullet_text,
            font_name=BODY_FONT,
            font_size=bullet_font,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.LEFT,
        )

    # Formula ribbon
    if formulas:
        formula_text = _join_items(formulas)
        formula_box = Box(1.00, layout.get("formula_y", 5.46), 11.00, 0.22)
        formula_font = _fit_text_size(
            formula_text,
            formula_box,
            min_font=12,
            max_font=14,
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

    if takeaway:
        takeaway_dict = layout.get("takeaway_box", {"x": 1.35, "y": 5.82, "w": 10.50, "h": 0.44})
        takeaway_box = Box(
            takeaway_dict["x"],
            takeaway_dict["y"],
            takeaway_dict["w"],
            takeaway_dict["h"],
        )
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
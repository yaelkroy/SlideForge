from __future__ import annotations

from typing import Any, Mapping

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, OFFWHITE, TITLE_FONT
from slideforge.config.themes import SlideTheme, get_theme, resolve_color
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, fit_text
from slideforge.render.header import render_header_from_spec
from slideforge.render.primitives import (
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


def _box_from_dict(raw: Mapping[str, Any], fallback: Box) -> Box:
    return Box(
        raw.get("x", fallback.x),
        raw.get("y", fallback.y),
        raw.get("w", fallback.w),
        raw.get("h", fallback.h),
    )


def _center_of(box: Box) -> tuple[float, float]:
    return (box.x + box.w / 2, box.y + box.h / 2)


def _resolve_dependency_style(
    spec: Mapping[str, Any],
    *,
    theme_obj: SlideTheme,
) -> dict[str, Any]:
    dependency_style = dict(spec.get("dependency_style", {}) or {})

    node_fill_default = theme_obj.box_fill_color
    if node_fill_default is None:
        node_fill_default = theme_obj.panel_fill_color
    if node_fill_default is None:
        node_fill_default = OFFWHITE

    center_fill_default = theme_obj.panel_fill_color
    if center_fill_default is None:
        center_fill_default = node_fill_default

    side_fill_default = theme_obj.box_fill_color
    if side_fill_default is None:
        side_fill_default = node_fill_default

    return {
        "node_fill_color": resolve_color(dependency_style.get("node_fill_color"), side_fill_default),
        "node_line_color": resolve_color(dependency_style.get("node_line_color"), theme_obj.box_line_color),
        "node_text_color": resolve_color(dependency_style.get("node_text_color"), theme_obj.body_color),
        "center_fill_color": resolve_color(dependency_style.get("center_fill_color"), center_fill_default),
        "center_line_color": resolve_color(dependency_style.get("center_line_color"), theme_obj.panel_line_color),
        "center_text_color": resolve_color(dependency_style.get("center_text_color"), theme_obj.title_color),
        "explanation_fill_color": resolve_color(dependency_style.get("explanation_fill_color"), side_fill_default),
        "explanation_line_color": resolve_color(dependency_style.get("explanation_line_color"), theme_obj.box_line_color),
        "explanation_title_color": resolve_color(dependency_style.get("explanation_title_color"), theme_obj.box_title_color),
        "explanation_body_color": resolve_color(dependency_style.get("explanation_body_color"), theme_obj.subtitle_color),
        "right_panel_fill_color": resolve_color(dependency_style.get("right_panel_fill_color"), side_fill_default),
        "right_panel_line_color": resolve_color(dependency_style.get("right_panel_line_color"), theme_obj.box_line_color),
        "right_panel_title_color": resolve_color(dependency_style.get("right_panel_title_color"), theme_obj.box_title_color),
        "right_panel_body_color": resolve_color(dependency_style.get("right_panel_body_color"), theme_obj.subtitle_color),
        "connector_color": resolve_color(dependency_style.get("connector_color"), theme_obj.connector_color),
        "connector_width_pt": float(dependency_style.get("connector_width_pt", theme_obj.connector_width_pt)),
        "formula_color": resolve_color(dependency_style.get("formula_color"), theme_obj.body_color),
        "takeaway_color": resolve_color(dependency_style.get("takeaway_color"), theme_obj.subtitle_color),
        "footer_color": resolve_color(dependency_style.get("footer_color"), theme_obj.footer_color),
        "footer_dark": bool(dependency_style.get("footer_dark", theme_obj.footer_dark)),
        "node_line_width_pt": float(dependency_style.get("node_line_width_pt", 1.25)),
        "center_line_width_pt": float(dependency_style.get("center_line_width_pt", 1.35)),
        "side_panel_line_width_pt": float(dependency_style.get("side_panel_line_width_pt", 1.25)),
    }


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
    fill_color,
    line_color,
    line_width_pt: float,
    align=PP_ALIGN.CENTER,
) -> None:
    add_rounded_box(
        slide,
        box.x,
        box.y,
        box.w,
        box.h,
        line_color=line_color,
        fill_color=fill_color,
        line_width_pt=line_width_pt,
    )

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


def _default_diagram_center_box(diagram: Mapping[str, Any]) -> Box:
    center_node = dict(diagram.get("center_node", {}) or {})
    return Box(
        float(center_node.get("x", 4.10)),
        float(center_node.get("y", 2.55)),
        float(center_node.get("w", 2.05)),
        float(center_node.get("h", 1.02)),
    )


def _default_input_boxes(diagram: Mapping[str, Any]) -> list[Box]:
    input_nodes = list(diagram.get("input_nodes", []) or [])
    boxes: list[Box] = []
    for node in input_nodes:
        boxes.append(
            Box(
                float(node.get("x", 1.20)),
                float(node.get("y", 1.40)),
                float(node.get("w", 2.20)),
                float(node.get("h", 0.92)),
            )
        )
    return boxes


def build_dependency_map_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    slide_theme_name = spec.get("theme", "concept")
    theme_obj = get_theme(slide_theme_name=slide_theme_name)

    bg = spec.get("background") or choose_background(slide_theme_name, counters)
    slide = new_slide(prs, bg)

    formulas = list(spec.get("formulas", []) or [])
    takeaway = str(spec.get("takeaway", "")).strip()
    explanation = dict(spec.get("explanation_box", {}) or {})
    diagram = dict(spec.get("diagram", {}) or {})
    layout = dict(spec.get("layout", {}) or {})

    header_result = render_header_from_spec(
        slide,
        spec,
        theme=theme_obj,
    )

    dep_style = _resolve_dependency_style(spec, theme_obj=theme_obj)

    center_node = dict(diagram.get("center_node", {}) or {})
    input_nodes = list(diagram.get("input_nodes", []) or [])

    center_box = _default_diagram_center_box(diagram)
    input_boxes = _default_input_boxes(diagram)

    # Draw connectors first so nodes appear on top.
    cx, cy = _center_of(center_box)
    connector_width = float(layout.get("connector_width_pt", dep_style["connector_width_pt"]))

    for box in input_boxes:
        x1, y1 = _center_of(box)
        add_soft_connector(
            slide,
            x1=x1,
            y1=y1,
            x2=cx,
            y2=cy,
            color=dep_style["connector_color"],
            width_pt=connector_width,
        )

    # Input nodes.
    for node, box in zip(input_nodes, input_boxes):
        _add_node(
            slide,
            box=box,
            text=str(node.get("label", "")),
            font_name=BODY_FONT,
            min_font=int(node.get("min_font_size", 12)),
            max_font=int(node.get("font_size", 14)),
            color=dep_style["node_text_color"],
            bold=True,
            fill_color=resolve_color(node.get("fill_color"), dep_style["node_fill_color"]),
            line_color=resolve_color(node.get("line_color"), dep_style["node_line_color"]),
            line_width_pt=float(node.get("line_width_pt", dep_style["node_line_width_pt"])),
            align=PP_ALIGN.CENTER,
        )

    # Central node.
    _add_node(
        slide,
        box=center_box,
        text=str(center_node.get("label", "Machine\nLearning")),
        font_name=TITLE_FONT,
        min_font=int(center_node.get("min_font_size", 16)),
        max_font=int(center_node.get("font_size", 19)),
        color=resolve_color(center_node.get("text_color"), dep_style["center_text_color"]),
        bold=True,
        fill_color=resolve_color(center_node.get("fill_color"), dep_style["center_fill_color"]),
        line_color=resolve_color(center_node.get("line_color"), dep_style["center_line_color"]),
        line_width_pt=float(center_node.get("line_width_pt", dep_style["center_line_width_pt"])),
        align=PP_ALIGN.CENTER,
    )

    # Explanation box on the right.
    explanation_text = str(explanation.get("text", "")).strip()
    explanation_title = str(explanation.get("title", "")).strip()
    if explanation_text:
        fallback_exp_box = Box(8.55, 2.05, 3.35, 1.18)
        exp_dict = layout.get("explanation_box")
        exp_box = _box_from_dict(exp_dict, fallback_exp_box) if isinstance(exp_dict, Mapping) else fallback_exp_box

        add_rounded_box(
            slide,
            exp_box.x,
            exp_box.y,
            exp_box.w,
            exp_box.h,
            line_color=dep_style["explanation_line_color"],
            fill_color=dep_style["explanation_fill_color"],
            line_width_pt=dep_style["side_panel_line_width_pt"],
        )

        if explanation_title:
            title_box = Box(exp_box.x + 0.12, exp_box.y + 0.10, exp_box.w - 0.24, 0.22)
            title_font = _fit_text_size(
                explanation_title,
                title_box,
                min_font=int(layout.get("explanation_title_min_font", 12)),
                max_font=int(layout.get("explanation_title_max_font", 14)),
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
                color=dep_style["explanation_title_color"],
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
            min_font=int(layout.get("explanation_body_min_font", 12)),
            max_font=int(layout.get("explanation_body_max_font", 14)),
            max_lines=int(layout.get("explanation_body_max_lines", 5)),
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
            color=dep_style["explanation_body_color"],
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    # Optional right-panel bullets if a spec still uses them.
    right_panel_bullets = list(spec.get("right_panel_bullets", []) or [])
    right_panel_title = str(spec.get("right_panel_title", "")).strip()
    if right_panel_bullets:
        fallback_rp_box = Box(8.55, 3.55, 3.35, 1.55)
        rp_dict = layout.get("bullets_box")
        rp_box = _box_from_dict(rp_dict, fallback_rp_box) if isinstance(rp_dict, Mapping) else fallback_rp_box

        add_rounded_box(
            slide,
            rp_box.x,
            rp_box.y,
            rp_box.w,
            rp_box.h,
            line_color=dep_style["right_panel_line_color"],
            fill_color=dep_style["right_panel_fill_color"],
            line_width_pt=dep_style["side_panel_line_width_pt"],
        )

        current_y = rp_box.y + 0.10
        if right_panel_title:
            header_box = Box(rp_box.x + 0.12, current_y, rp_box.w - 0.24, 0.22)
            header_font = _fit_text_size(
                right_panel_title,
                header_box,
                min_font=int(layout.get("right_panel_title_min_font", 12)),
                max_font=int(layout.get("right_panel_title_max_font", 14)),
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
                color=dep_style["right_panel_title_color"],
                bold=True,
                align=PP_ALIGN.CENTER,
            )
            current_y += 0.26

        bullet_text = "\n".join(f"• {item}" for item in right_panel_bullets if str(item).strip())
        bullet_box = Box(rp_box.x + 0.14, current_y, rp_box.w - 0.28, rp_box.bottom - current_y - 0.10)
        bullet_font = _fit_text_size(
            bullet_text,
            bullet_box,
            min_font=int(layout.get("right_panel_body_min_font", 11)),
            max_font=int(layout.get("right_panel_body_max_font", 13)),
            max_lines=int(layout.get("right_panel_body_max_lines", 8)),
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
            color=dep_style["right_panel_body_color"],
            bold=False,
            align=PP_ALIGN.LEFT,
        )

    # Formula ribbon.
    if formulas:
        formula_text = _join_items(formulas)
        formula_box = Box(
            float(layout.get("formula_x", 1.00)),
            float(layout.get("formula_y", 5.46)),
            float(layout.get("formula_w", 11.00)),
            float(layout.get("formula_h", 0.22)),
        )
        formula_font = _fit_text_size(
            formula_text,
            formula_box,
            min_font=int(layout.get("formula_min_font", 12)),
            max_font=int(layout.get("formula_max_font", 14)),
            max_lines=int(layout.get("formula_max_lines", 2)),
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
            color=dep_style["formula_color"],
            bold=False,
            align=layout.get("formula_align", PP_ALIGN.CENTER),
        )

    if takeaway:
        fallback_takeaway = Box(1.35, 5.82, 10.50, 0.44)
        takeaway_dict = layout.get("takeaway_box")
        takeaway_box = _box_from_dict(takeaway_dict, fallback_takeaway) if isinstance(takeaway_dict, Mapping) else fallback_takeaway

        takeaway_font = _fit_text_size(
            takeaway,
            takeaway_box,
            min_font=int(layout.get("takeaway_min_font", 12)),
            max_font=int(layout.get("takeaway_max_font", 14)),
            max_lines=int(layout.get("takeaway_max_lines", 2)),
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
            color=dep_style["takeaway_color"],
            bold=bool(layout.get("takeaway_bold", False)),
            align=layout.get("takeaway_align", PP_ALIGN.CENTER),
        )

    add_footer(
        slide,
        dark=dep_style["footer_dark"],
        color=dep_style["footer_color"],
    )
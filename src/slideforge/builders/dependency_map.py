from __future__ import annotations

from typing import Any, Mapping

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, OFFWHITE, TITLE_FONT
from slideforge.config.themes import SlideTheme, get_theme, resolve_color
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, fit_text, layout_dependency_map
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
    return (box.center_x, box.center_y)


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
        "node_fill_color": resolve_color(
            dependency_style.get("node_fill_color"),
            side_fill_default,
        ),
        "node_line_color": resolve_color(
            dependency_style.get("node_line_color"),
            theme_obj.box_line_color,
        ),
        "node_text_color": resolve_color(
            dependency_style.get("node_text_color"),
            theme_obj.body_color,
        ),
        "center_fill_color": resolve_color(
            dependency_style.get("center_fill_color"),
            center_fill_default,
        ),
        "center_line_color": resolve_color(
            dependency_style.get("center_line_color"),
            theme_obj.panel_line_color,
        ),
        "center_text_color": resolve_color(
            dependency_style.get("center_text_color"),
            theme_obj.title_color,
        ),
        "explanation_fill_color": resolve_color(
            dependency_style.get("explanation_fill_color"),
            side_fill_default,
        ),
        "explanation_line_color": resolve_color(
            dependency_style.get("explanation_line_color"),
            theme_obj.box_line_color,
        ),
        "explanation_title_color": resolve_color(
            dependency_style.get("explanation_title_color"),
            theme_obj.box_title_color,
        ),
        "explanation_body_color": resolve_color(
            dependency_style.get("explanation_body_color"),
            theme_obj.subtitle_color,
        ),
        "right_panel_fill_color": resolve_color(
            dependency_style.get("right_panel_fill_color"),
            side_fill_default,
        ),
        "right_panel_line_color": resolve_color(
            dependency_style.get("right_panel_line_color"),
            theme_obj.box_line_color,
        ),
        "right_panel_title_color": resolve_color(
            dependency_style.get("right_panel_title_color"),
            theme_obj.box_title_color,
        ),
        "right_panel_body_color": resolve_color(
            dependency_style.get("right_panel_body_color"),
            theme_obj.subtitle_color,
        ),
        "connector_color": resolve_color(
            dependency_style.get("connector_color"),
            theme_obj.connector_color,
        ),
        "connector_width_pt": float(
            dependency_style.get("connector_width_pt", theme_obj.connector_width_pt)
        ),
        "formula_color": resolve_color(
            dependency_style.get("formula_color"),
            theme_obj.body_color,
        ),
        "takeaway_color": resolve_color(
            dependency_style.get("takeaway_color"),
            theme_obj.subtitle_color,
        ),
        "footer_color": resolve_color(
            dependency_style.get("footer_color"),
            theme_obj.footer_color,
        ),
        "footer_dark": bool(
            dependency_style.get("footer_dark", theme_obj.footer_dark)
        ),
        "node_line_width_pt": float(
            dependency_style.get("node_line_width_pt", 1.25)
        ),
        "center_line_width_pt": float(
            dependency_style.get("center_line_width_pt", 1.35)
        ),
        "side_panel_line_width_pt": float(
            dependency_style.get("side_panel_line_width_pt", 1.25)
        ),
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


def _resolve_content_box(
    header_content_box: Box,
    layout: Mapping[str, Any],
) -> Box:
    x = float(layout.get("content_x", header_content_box.x))
    y = float(layout.get("content_y", header_content_box.y))
    w = float(layout.get("content_w", header_content_box.w))
    h = float(layout.get("content_h", header_content_box.bottom - y))
    return Box(x, y, w, h)


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

    right_panel_bullets = list(spec.get("right_panel_bullets", []) or [])
    right_panel_title = str(spec.get("right_panel_title", "")).strip()
    has_explanation = bool(str(explanation.get("text", "")).strip())
    has_right_panel = bool(right_panel_bullets)

    content_box = _resolve_content_box(header_result.content_top_box, layout)

    dep_layout = layout_dependency_map(
        content_box,
        has_explanation=has_explanation,
        has_right_panel=has_right_panel,
        has_formulas=bool(formulas),
        has_takeaway=bool(takeaway),
        top_pad=float(layout.get("dep_top_pad", 0.06)),
        bottom_pad=float(layout.get("dep_bottom_pad", 0.08)),
        side_gap=float(layout.get("dep_side_gap", 0.38)),
        right_column_w=float(layout.get("dep_right_column_w", 3.15)),
        explanation_h=float(layout.get("dep_explanation_h", 1.28)),
        right_panel_h=float(layout.get("dep_right_panel_h", 1.40)),
        right_column_inner_gap=float(layout.get("dep_right_column_inner_gap", 0.18)),
        center_w=float(layout.get("dep_center_w", 2.10)),
        center_h=float(layout.get("dep_center_h", 1.06)),
        node_w=float(layout.get("dep_node_w", 2.20)),
        node_h=float(layout.get("dep_node_h", 0.95)),
        node_side_pad=float(layout.get("dep_node_side_pad", 0.22)),
        node_top_pad=float(layout.get("dep_node_top_pad", 0.18)),
        node_bottom_pad=float(layout.get("dep_node_bottom_pad", 0.18)),
        formula_h=float(layout.get("dep_formula_h", 0.22)),
        formula_gap_top=float(layout.get("dep_formula_gap_top", 0.18)),
        takeaway_h=float(layout.get("dep_takeaway_h", 0.40)),
        takeaway_gap_top=float(layout.get("dep_takeaway_gap_top", 0.12)),
        footer_clearance=float(layout.get("dep_footer_clearance", 0.44)),
        formula_side_pad=float(layout.get("dep_formula_side_pad", 0.12)),
        takeaway_side_pad=float(layout.get("dep_takeaway_side_pad", 0.35)),
    )

    # Legacy manual boxes are opt-in only.
    use_manual_boxes = bool(layout.get("use_manual_dependency_boxes", False))

    center_box = dep_layout.center_box
    input_boxes = dep_layout.input_boxes
    explanation_box = dep_layout.explanation_box
    right_panel_box = dep_layout.right_panel_box
    formula_box = dep_layout.formula_box
    takeaway_box = dep_layout.takeaway_box

    if use_manual_boxes:
        if explanation_box is not None and isinstance(layout.get("explanation_box"), Mapping):
            explanation_box = _box_from_dict(layout["explanation_box"], explanation_box)
        if right_panel_box is not None and isinstance(layout.get("bullets_box"), Mapping):
            right_panel_box = _box_from_dict(layout["bullets_box"], right_panel_box)
        if formula_box is not None and all(
            key in layout for key in ("formula_x", "formula_y", "formula_w", "formula_h")
        ):
            formula_box = Box(
                float(layout["formula_x"]),
                float(layout["formula_y"]),
                float(layout["formula_w"]),
                float(layout["formula_h"]),
            )
        if takeaway_box is not None and isinstance(layout.get("takeaway_box"), Mapping):
            takeaway_box = _box_from_dict(layout["takeaway_box"], takeaway_box)

    # Draw connectors first so nodes appear on top.
    cx, cy = _center_of(center_box)
    connector_width = float(layout.get("connector_width_pt", dep_style["connector_width_pt"]))

    for box in input_boxes[: len(input_nodes)]:
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
            fill_color=resolve_color(
                node.get("fill_color"),
                dep_style["node_fill_color"],
            ),
            line_color=resolve_color(
                node.get("line_color"),
                dep_style["node_line_color"],
            ),
            line_width_pt=float(
                node.get("line_width_pt", dep_style["node_line_width_pt"])
            ),
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
        color=resolve_color(
            center_node.get("text_color"),
            dep_style["center_text_color"],
        ),
        bold=True,
        fill_color=resolve_color(
            center_node.get("fill_color"),
            dep_style["center_fill_color"],
        ),
        line_color=resolve_color(
            center_node.get("line_color"),
            dep_style["center_line_color"],
        ),
        line_width_pt=float(
            center_node.get("line_width_pt", dep_style["center_line_width_pt"])
        ),
        align=PP_ALIGN.CENTER,
    )

    # Explanation box on the right.
    explanation_text = str(explanation.get("text", "")).strip()
    explanation_title = str(explanation.get("title", "")).strip()
    if explanation_text and explanation_box is not None:
        add_rounded_box(
            slide,
            explanation_box.x,
            explanation_box.y,
            explanation_box.w,
            explanation_box.h,
            line_color=dep_style["explanation_line_color"],
            fill_color=dep_style["explanation_fill_color"],
            line_width_pt=dep_style["side_panel_line_width_pt"],
        )

        top_inner_pad = float(layout.get("explanation_inner_top_pad", 0.10))
        side_inner_pad = float(layout.get("explanation_inner_side_pad", 0.14))
        bottom_inner_pad = float(layout.get("explanation_inner_bottom_pad", 0.16))
        title_to_body_gap = float(layout.get("explanation_title_to_body_gap", 0.07))
        title_h = float(layout.get("explanation_title_h", 0.22))

        if explanation_title:
            title_box = Box(
                explanation_box.x + 0.12,
                explanation_box.y + top_inner_pad,
                explanation_box.w - 0.24,
                title_h,
            )
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
            body_y = title_box.bottom + title_to_body_gap
        else:
            body_y = explanation_box.y + top_inner_pad

        body_h = explanation_box.bottom - body_y - bottom_inner_pad
        body_box = Box(
            explanation_box.x + side_inner_pad,
            body_y,
            explanation_box.w - 2 * side_inner_pad,
            max(0.0, body_h),
        )
        body_font = _fit_text_size(
            explanation_text,
            body_box,
            min_font=int(layout.get("explanation_body_min_font", 12)),
            max_font=int(layout.get("explanation_body_max_font", 13)),
            max_lines=int(layout.get("explanation_body_max_lines", 4)),
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

    # Optional right-panel bullets.
    if right_panel_bullets and right_panel_box is not None:
        add_rounded_box(
            slide,
            right_panel_box.x,
            right_panel_box.y,
            right_panel_box.w,
            right_panel_box.h,
            line_color=dep_style["right_panel_line_color"],
            fill_color=dep_style["right_panel_fill_color"],
            line_width_pt=dep_style["side_panel_line_width_pt"],
        )

        current_y = right_panel_box.y + 0.10
        if right_panel_title:
            header_box = Box(
                right_panel_box.x + 0.12,
                current_y,
                right_panel_box.w - 0.24,
                0.22,
            )
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

        bullet_text = "\n".join(
            f"• {item}" for item in right_panel_bullets if str(item).strip()
        )
        bullet_box = Box(
            right_panel_box.x + 0.14,
            current_y,
            right_panel_box.w - 0.28,
            max(0.0, right_panel_box.bottom - current_y - 0.10),
        )
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
    if formulas and formula_box is not None:
        formula_text = _join_items(formulas)
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

    if takeaway and takeaway_box is not None:
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
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, OFFWHITE, TITLE_FONT
from slideforge.config.themes import SlideTheme, get_theme, resolve_color
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, fit_text, layout_dependency_map
from slideforge.render.header import render_header_from_spec
from slideforge.render.primitives import add_footer, add_rounded_box, add_soft_connector, add_textbox


@dataclass(frozen=True)
class _PanelContent:
    title: str
    body: str


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _clean_items(items: list[Any] | tuple[Any, ...] | None) -> list[str]:
    return [_clean(item) for item in (items or []) if _clean(item)]


def _join_items(items: list[Any] | tuple[Any, ...] | None, *, separator: str = "   •   ") -> str:
    return separator.join(_clean_items(items))


def _box_from_dict(raw: Mapping[str, Any], fallback: Box) -> Box:
    return Box(raw.get("x", fallback.x), raw.get("y", fallback.y), raw.get("w", fallback.w), raw.get("h", fallback.h))


def _center_of(box: Box) -> tuple[float, float]:
    return box.center_x, box.center_y


def _fit_text_size(text: str, box: Box, *, min_font: int, max_font: int, max_lines: int) -> int:
    text = _clean(text)
    if not text or box.w <= 0 or box.h <= 0:
        return max_font
    fitted = fit_text(text, box.w, box.h, min_font_size=min_font, max_font_size=max_font, max_lines=max_lines)
    return max(min_font, fitted.font_size)


def _resolve_fill(primary, fallback_a, fallback_b):
    if primary is not None:
        return primary
    if fallback_a is not None:
        return fallback_a
    return fallback_b


def _resolve_dependency_style(spec: Mapping[str, Any], *, theme_obj: SlideTheme) -> dict[str, Any]:
    style = dict(spec.get("dependency_style", {}) or {})
    node_fill_default = _resolve_fill(theme_obj.box_fill_color, theme_obj.panel_fill_color, OFFWHITE)
    center_fill_default = _resolve_fill(theme_obj.panel_fill_color, node_fill_default, OFFWHITE)
    side_fill_default = _resolve_fill(theme_obj.box_fill_color, node_fill_default, OFFWHITE)
    return {
        "node_fill_color": resolve_color(style.get("node_fill_color"), side_fill_default),
        "node_line_color": resolve_color(style.get("node_line_color"), theme_obj.box_line_color),
        "node_text_color": resolve_color(style.get("node_text_color"), theme_obj.body_color),
        "center_fill_color": resolve_color(style.get("center_fill_color"), center_fill_default),
        "center_line_color": resolve_color(style.get("center_line_color"), theme_obj.panel_line_color),
        "center_text_color": resolve_color(style.get("center_text_color"), theme_obj.title_color),
        "explanation_fill_color": resolve_color(style.get("explanation_fill_color"), side_fill_default),
        "explanation_line_color": resolve_color(style.get("explanation_line_color"), theme_obj.box_line_color),
        "explanation_title_color": resolve_color(style.get("explanation_title_color"), theme_obj.box_title_color),
        "explanation_body_color": resolve_color(style.get("explanation_body_color"), theme_obj.subtitle_color),
        "right_panel_fill_color": resolve_color(style.get("right_panel_fill_color"), side_fill_default),
        "right_panel_line_color": resolve_color(style.get("right_panel_line_color"), theme_obj.box_line_color),
        "right_panel_title_color": resolve_color(style.get("right_panel_title_color"), theme_obj.box_title_color),
        "right_panel_body_color": resolve_color(style.get("right_panel_body_color"), theme_obj.subtitle_color),
        "connector_color": resolve_color(style.get("connector_color"), theme_obj.connector_color),
        "connector_width_pt": float(style.get("connector_width_pt", theme_obj.connector_width_pt)),
        "formula_color": resolve_color(style.get("formula_color"), theme_obj.body_color),
        "takeaway_color": resolve_color(style.get("takeaway_color"), theme_obj.subtitle_color),
        "footer_color": resolve_color(style.get("footer_color"), theme_obj.footer_color),
        "footer_dark": bool(style.get("footer_dark", theme_obj.footer_dark)),
        "node_line_width_pt": float(style.get("node_line_width_pt", 1.25)),
        "center_line_width_pt": float(style.get("center_line_width_pt", 1.35)),
        "side_panel_line_width_pt": float(style.get("side_panel_line_width_pt", 1.25)),
    }


def _resolve_content_box(header_content_box: Box, layout: Mapping[str, Any]) -> Box:
    x = float(layout.get("content_x", header_content_box.x))
    y = float(layout.get("content_y", header_content_box.y))
    w = float(layout.get("content_w", header_content_box.w))
    h = float(layout.get("content_h", header_content_box.bottom - y))
    return Box(x, y, w, h)


def _apply_manual_box_overrides(
    *,
    layout: Mapping[str, Any],
    explanation_box: Box | None,
    right_panel_box: Box | None,
    formula_box: Box | None,
    takeaway_box: Box | None,
) -> tuple[Box | None, Box | None, Box | None, Box | None]:
    if not bool(layout.get("use_manual_dependency_boxes", False)):
        return explanation_box, right_panel_box, formula_box, takeaway_box
    if explanation_box is not None and isinstance(layout.get("explanation_box"), Mapping):
        explanation_box = _box_from_dict(layout["explanation_box"], explanation_box)
    if right_panel_box is not None and isinstance(layout.get("bullets_box"), Mapping):
        right_panel_box = _box_from_dict(layout["bullets_box"], right_panel_box)
    if formula_box is not None and all(key in layout for key in ("formula_x", "formula_y", "formula_w", "formula_h")):
        formula_box = Box(float(layout["formula_x"]), float(layout["formula_y"]), float(layout["formula_w"]), float(layout["formula_h"]))
    if takeaway_box is not None and isinstance(layout.get("takeaway_box"), Mapping):
        takeaway_box = _box_from_dict(layout["takeaway_box"], takeaway_box)
    return explanation_box, right_panel_box, formula_box, takeaway_box


def _draw_text_block(
    slide,
    *,
    box: Box,
    text: str,
    font_name: str,
    color,
    min_font: int,
    max_font: int,
    max_lines: int,
    bold: bool = False,
    align=PP_ALIGN.CENTER,
) -> None:
    text = _clean(text)
    if not text or box.w <= 0 or box.h <= 0:
        return
    font_size = _fit_text_size(text, box, min_font=min_font, max_font=max_font, max_lines=max_lines)
    add_textbox(slide, x=box.x, y=box.y, w=box.w, h=box.h, text=text, font_name=font_name, font_size=font_size, color=color, bold=bold, align=align)


def _draw_node(
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
    add_rounded_box(slide, box.x, box.y, box.w, box.h, line_color=line_color, fill_color=fill_color, line_width_pt=line_width_pt)
    inner = Box(box.x + 0.10, box.y + 0.08, box.w - 0.20, box.h - 0.16)
    _draw_text_block(slide, box=inner, text=text, font_name=font_name, color=color, min_font=min_font, max_font=max_font, max_lines=3, bold=bold, align=align)


def _draw_labeled_panel(
    slide,
    *,
    box: Box,
    content: _PanelContent,
    fill_color,
    line_color,
    line_width_pt: float,
    title_color,
    body_color,
    title_font_name: str = BODY_FONT,
    body_font_name: str = BODY_FONT,
    body_align=PP_ALIGN.CENTER,
    title_min_font: int,
    title_max_font: int,
    body_min_font: int,
    body_max_font: int,
    body_max_lines: int,
    title_box_h: float = 0.22,
    panel_inner_x: float = 0.12,
    panel_inner_top: float = 0.10,
    panel_inner_bottom: float = 0.10,
    title_to_body_gap: float = 0.07,
) -> None:
    if box is None or box.w <= 0 or box.h <= 0 or not (content.title or content.body):
        return
    add_rounded_box(slide, box.x, box.y, box.w, box.h, line_color=line_color, fill_color=fill_color, line_width_pt=line_width_pt)
    current_y = box.y + panel_inner_top
    inner_w = max(0.0, box.w - 2 * panel_inner_x)
    if content.title:
        title_box = Box(box.x + panel_inner_x, current_y, inner_w, title_box_h)
        _draw_text_block(slide, box=title_box, text=content.title, font_name=title_font_name, color=title_color, min_font=title_min_font, max_font=title_max_font, max_lines=2, bold=True, align=PP_ALIGN.CENTER)
        current_y = title_box.bottom + title_to_body_gap
    body_h = max(0.0, box.bottom - current_y - panel_inner_bottom)
    body_box = Box(box.x + panel_inner_x, current_y, inner_w, body_h)
    _draw_text_block(slide, box=body_box, text=content.body, font_name=body_font_name, color=body_color, min_font=body_min_font, max_font=body_max_font, max_lines=body_max_lines, align=body_align)


def _draw_connectors(slide, *, center_box: Box, input_boxes: list[Box], count: int, color, width_pt: float) -> None:
    cx, cy = _center_of(center_box)
    for box in input_boxes[:count]:
        x1, y1 = _center_of(box)
        add_soft_connector(slide, x1=x1, y1=y1, x2=cx, y2=cy, color=color, width_pt=width_pt)


def _render_side_panels(
    slide,
    *,
    explanation_box: Box | None,
    explanation: _PanelContent,
    right_panel_box: Box | None,
    right_panel_title: str,
    right_panel_bullets: list[str],
    formula_box: Box | None,
    formulas: list[str],
    takeaway_box: Box | None,
    takeaway: str,
    dep_style: Mapping[str, Any],
    layout: Mapping[str, Any],
) -> None:
    if explanation.body and explanation_box is not None:
        _draw_labeled_panel(
            slide,
            box=explanation_box,
            content=explanation,
            fill_color=dep_style["explanation_fill_color"],
            line_color=dep_style["explanation_line_color"],
            line_width_pt=dep_style["side_panel_line_width_pt"],
            title_color=dep_style["explanation_title_color"],
            body_color=dep_style["explanation_body_color"],
            body_align=PP_ALIGN.CENTER,
            title_min_font=int(layout.get("explanation_title_min_font", 12)),
            title_max_font=int(layout.get("explanation_title_max_font", 14)),
            body_min_font=int(layout.get("explanation_body_min_font", 12)),
            body_max_font=int(layout.get("explanation_body_max_font", 13)),
            body_max_lines=int(layout.get("explanation_body_max_lines", 4)),
            title_box_h=float(layout.get("explanation_title_h", 0.22)),
            panel_inner_x=float(layout.get("explanation_inner_side_pad", 0.14)),
            panel_inner_top=float(layout.get("explanation_inner_top_pad", 0.10)),
            panel_inner_bottom=float(layout.get("explanation_inner_bottom_pad", 0.16)),
            title_to_body_gap=float(layout.get("explanation_title_to_body_gap", 0.07)),
        )
    if right_panel_bullets and right_panel_box is not None:
        bullet_text = "\n".join(f"• {item}" for item in _clean_items(right_panel_bullets))
        _draw_labeled_panel(
            slide,
            box=right_panel_box,
            content=_PanelContent(title=right_panel_title, body=bullet_text),
            fill_color=dep_style["right_panel_fill_color"],
            line_color=dep_style["right_panel_line_color"],
            line_width_pt=dep_style["side_panel_line_width_pt"],
            title_color=dep_style["right_panel_title_color"],
            body_color=dep_style["right_panel_body_color"],
            body_align=PP_ALIGN.LEFT,
            title_min_font=int(layout.get("right_panel_title_min_font", 12)),
            title_max_font=int(layout.get("right_panel_title_max_font", 14)),
            body_min_font=int(layout.get("right_panel_body_min_font", 11)),
            body_max_font=int(layout.get("right_panel_body_max_font", 13)),
            body_max_lines=int(layout.get("right_panel_body_max_lines", 8)),
            title_box_h=0.22,
            panel_inner_x=0.14,
            panel_inner_top=0.10,
            panel_inner_bottom=0.10,
            title_to_body_gap=0.04 if right_panel_title else 0.0,
        )
    if formulas and formula_box is not None:
        _draw_text_block(slide, box=formula_box, text=_join_items(formulas), font_name=FORMULA_FONT, color=dep_style["formula_color"], min_font=int(layout.get("formula_min_font", 12)), max_font=int(layout.get("formula_max_font", 14)), max_lines=int(layout.get("formula_max_lines", 2)), align=layout.get("formula_align", PP_ALIGN.CENTER))
    if takeaway and takeaway_box is not None:
        _draw_text_block(slide, box=takeaway_box, text=takeaway, font_name=BODY_FONT, color=dep_style["takeaway_color"], min_font=int(layout.get("takeaway_min_font", 12)), max_font=int(layout.get("takeaway_max_font", 14)), max_lines=int(layout.get("takeaway_max_lines", 2)), bold=bool(layout.get("takeaway_bold", False)), align=layout.get("takeaway_align", PP_ALIGN.CENTER))


def build_dependency_map_slide(prs: Presentation, spec: dict[str, Any], counters: dict[str, int]) -> None:
    slide_theme_name = spec.get("theme", "concept")
    theme_obj = get_theme(slide_theme_name=slide_theme_name)
    bg = spec.get("background") or choose_background(slide_theme_name, counters)
    slide = new_slide(prs, bg)

    layout = dict(spec.get("layout", {}) or {})
    formulas = list(spec.get("formulas", []) or [])
    takeaway = _clean(spec.get("takeaway"))
    explanation = dict(spec.get("explanation_box", {}) or {})
    diagram = dict(spec.get("diagram", {}) or {})
    right_panel_bullets = list(spec.get("right_panel_bullets", []) or [])
    right_panel_title = _clean(spec.get("right_panel_title"))

    header_result = render_header_from_spec(slide, spec, theme=theme_obj)
    dep_style = _resolve_dependency_style(spec, theme_obj=theme_obj)

    content_box = _resolve_content_box(header_result.content_top_box, layout)
    dep_layout = layout_dependency_map(
        content_box,
        has_explanation=bool(_clean(explanation.get("text"))),
        has_right_panel=bool(_clean_items(right_panel_bullets)),
        has_formulas=bool(_clean_items(formulas)),
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

    center_box = dep_layout.center_box
    input_boxes = dep_layout.input_boxes
    explanation_box, right_panel_box, formula_box, takeaway_box = _apply_manual_box_overrides(
        layout=layout,
        explanation_box=dep_layout.explanation_box,
        right_panel_box=dep_layout.right_panel_box,
        formula_box=dep_layout.formula_box,
        takeaway_box=dep_layout.takeaway_box,
    )

    center_node = dict(diagram.get("center_node", {}) or {})
    input_nodes = list(diagram.get("input_nodes", []) or [])

    _draw_connectors(slide, center_box=center_box, input_boxes=input_boxes, count=len(input_nodes), color=dep_style["connector_color"], width_pt=float(layout.get("connector_width_pt", dep_style["connector_width_pt"])))
    for node, box in zip(input_nodes, input_boxes):
        _draw_node(
            slide,
            box=box,
            text=_clean(node.get("label")),
            font_name=BODY_FONT,
            min_font=int(node.get("min_font_size", 12)),
            max_font=int(node.get("font_size", 14)),
            color=resolve_color(node.get("text_color"), dep_style["node_text_color"]),
            bold=True,
            fill_color=resolve_color(node.get("fill_color"), dep_style["node_fill_color"]),
            line_color=resolve_color(node.get("line_color"), dep_style["node_line_color"]),
            line_width_pt=float(node.get("line_width_pt", dep_style["node_line_width_pt"])),
            align=PP_ALIGN.CENTER,
        )

    _draw_node(
        slide,
        box=center_box,
        text=_clean(center_node.get("label")) or "Machine\nLearning",
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

    _render_side_panels(
        slide,
        explanation_box=explanation_box,
        explanation=_PanelContent(title=_clean(explanation.get("title")), body=_clean(explanation.get("text"))),
        right_panel_box=right_panel_box,
        right_panel_title=right_panel_title,
        right_panel_bullets=right_panel_bullets,
        formula_box=formula_box,
        formulas=formulas,
        takeaway_box=takeaway_box,
        takeaway=takeaway,
        dep_style=dep_style,
        layout=layout,
    )
    add_footer(slide, dark=dep_style["footer_dark"], color=dep_style["footer_color"])

from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

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
from slideforge.utils.text_layout import fit_joined_items_to_box, fit_text_to_box


def _node_center(node: dict[str, float]) -> tuple[float, float]:
    return node["x"] + node["w"] / 2.0, node["y"] + node["h"] / 2.0


def _add_node(
    slide,
    *,
    x: float,
    y: float,
    w: float,
    h: float,
    label: str,
    font_size: int,
    primary: bool = False,
) -> None:
    add_rounded_box(slide, x, y, w, h)
    fit = fit_text_to_box(
        text=label,
        width_in=w - 0.28,
        height_in=h - 0.18,
        min_font_size=max(12, font_size - 2),
        max_font_size=font_size,
        max_lines=2,
    )
    add_textbox(
        slide,
        x=x + 0.14,
        y=y + (h - fit.height_in) / 2.0,
        w=w - 0.28,
        h=fit.height_in + 0.02,
        text=fit.text,
        font_name=TITLE_FONT if primary else BODY_FONT,
        font_size=fit.font_size,
        color=NAVY,
        bold=True if primary else False,
        align=PP_ALIGN.CENTER,
    )


def build_dependency_map_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    theme = spec.get("theme", "concept")
    bg = spec.get("background") or choose_background(theme, counters)
    slide = new_slide(prs, bg)

    layout = spec.get("layout", {})

    add_textbox(
        slide,
        x=0.80,
        y=layout.get("title_y", 0.42),
        w=11.70,
        h=0.50,
        text=spec["title"],
        font_name=TITLE_FONT,
        font_size=26,
        color=NAVY,
        bold=True,
    )
    add_divider_line(slide, dark=False)

    subtitle = spec.get("subtitle", "").strip()
    if subtitle:
        sub_fit = fit_text_to_box(
            text=subtitle,
            width_in=10.9,
            height_in=0.40,
            min_font_size=15,
            max_font_size=18,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=1.00,
            y=0.98,
            w=11.00,
            h=0.40,
            text=sub_fit.text,
            font_name=BODY_FONT,
            font_size=sub_fit.font_size,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    diagram = spec.get("diagram", {})
    center_node = diagram.get("center_node", {})
    input_nodes = diagram.get("input_nodes", [])

    for node in input_nodes:
        _add_node(
            slide,
            x=node["x"],
            y=node["y"],
            w=node["w"],
            h=node["h"],
            label=node.get("label", ""),
            font_size=node.get("font_size", 14),
            primary=False,
        )

    _add_node(
        slide,
        x=center_node["x"],
        y=center_node["y"],
        w=center_node["w"],
        h=center_node["h"],
        label=center_node.get("label", ""),
        font_size=center_node.get("font_size", 20),
        primary=True,
    )

    cx, cy = _node_center(center_node)
    for node in input_nodes:
        nx, ny = _node_center(node)
        add_soft_connector(
            slide,
            x1=nx + (node["w"] / 2.0 if nx < cx else -node["w"] / 2.0),
            y1=ny,
            x2=cx + (-center_node["w"] / 2.0 if nx < cx else center_node["w"] / 2.0),
            y2=cy,
            color=ACCENT,
            width_pt=1.5,
        )

    explanation_box = layout.get("explanation_box", {"x": 8.55, "y": 2.05, "w": 3.35, "h": 1.18})
    explanation = spec.get("explanation_box", {})
    if explanation:
        add_rounded_box(
            slide,
            explanation_box["x"],
            explanation_box["y"],
            explanation_box["w"],
            explanation_box["h"],
        )

        title_fit = fit_text_to_box(
            text=explanation.get("title", ""),
            width_in=explanation_box["w"] - 0.30,
            height_in=0.22,
            min_font_size=12,
            max_font_size=14,
            max_lines=1,
        )
        add_textbox(
            slide,
            x=explanation_box["x"] + 0.15,
            y=explanation_box["y"] + 0.10,
            w=explanation_box["w"] - 0.30,
            h=0.22,
            text=title_fit.text,
            font_name=BODY_FONT,
            font_size=title_fit.font_size,
            color=SLATE,
            bold=True,
            align=PP_ALIGN.CENTER,
        )

        body_fit = fit_text_to_box(
            text=explanation.get("text", ""),
            width_in=explanation_box["w"] - 0.36,
            height_in=explanation_box["h"] - 0.42,
            min_font_size=12,
            max_font_size=14,
            max_lines=4,
        )
        add_textbox(
            slide,
            x=explanation_box["x"] + 0.18,
            y=explanation_box["y"] + 0.34,
            w=explanation_box["w"] - 0.36,
            h=explanation_box["h"] - 0.42,
            text=body_fit.text,
            font_name=BODY_FONT,
            font_size=body_fit.font_size,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    formulas = spec.get("formulas", [])
    if formulas:
        fit = fit_joined_items_to_box(
            items=formulas,
            width_in=10.9,
            height_in=0.24,
            min_font_size=13,
            max_font_size=15,
            max_lines=1,
        )
        add_textbox(
            slide,
            x=1.10,
            y=5.42,
            w=10.90,
            h=0.24,
            text=fit.text,
            font_name=FORMULA_FONT,
            font_size=fit.font_size,
            color=NAVY,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    takeaway = spec.get("takeaway", "").strip()
    if takeaway:
        take_box = layout.get("takeaway_box", {"x": 1.35, "y": 5.82, "w": 10.50, "h": 0.44})
        take_fit = fit_text_to_box(
            text=takeaway,
            width_in=take_box["w"],
            height_in=take_box["h"],
            min_font_size=12,
            max_font_size=14,
            max_lines=2,
        )
        add_textbox(
            slide,
            x=take_box["x"],
            y=take_box["y"],
            w=take_box["w"],
            h=take_box["h"],
            text=take_fit.text,
            font_name=BODY_FONT,
            font_size=take_fit.font_size,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    add_footer(slide, dark=False)
from __future__ import annotations

from typing import Any, Mapping, Sequence

from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.config.constants import BODY_FONT, FORMULA_FONT
from slideforge.layout.autofit import Box, fit_text
from slideforge.render.primitives import add_rounded_box, add_soft_connector, add_textbox
from slideforge.style.title_style import TitleCompositeStyle


def _fit_text_size(
    text: str,
    box: Box,
    *,
    min_font: int,
    max_font: int,
    max_lines: int,
) -> int:
    if not str(text or "").strip() or box.w <= 0 or box.h <= 0:
        return max_font
    fitted = fit_text(
        str(text).strip(),
        box.w,
        box.h,
        min_font_size=min_font,
        max_font_size=max_font,
        max_lines=max_lines,
    )
    return max(min_font, fitted.font_size)


def render_centered_text_block(
    slide,
    *,
    box: Box,
    text: str,
    font_name: str,
    min_font: int,
    max_font: int,
    max_lines: int,
    color,
    bold: bool = False,
    align=PP_ALIGN.CENTER,
) -> None:
    text = str(text or "").strip()
    if not text:
        return
    font_size = _fit_text_size(text, box, min_font=min_font, max_font=max_font, max_lines=max_lines)
    add_textbox(
        slide,
        x=box.x,
        y=box.y,
        w=box.w,
        h=box.h,
        text=text,
        font_name=font_name,
        font_size=font_size,
        color=color,
        bold=bold,
        align=align,
    )


def _panel_box_from_spec(panel: Mapping[str, Any], fallback: Box) -> Box:
    return Box(
        float(panel.get("x", fallback.x)),
        float(panel.get("y", fallback.y)),
        float(panel.get("w", fallback.w)),
        float(panel.get("h", fallback.h)),
    )


def render_title_visual_panel(
    slide,
    *,
    panel_box: Box,
    panel: Mapping[str, Any],
    idx: int,
    style: TitleCompositeStyle,
) -> None:
    label = str(panel.get("label", "")).strip()
    embedded_label = str(panel.get("embedded_label", "")).strip()
    mini_visual = str(panel.get("mini_visual", "")).strip()
    panel_style = dict(panel.get("style", {}) or {})

    fill_color = style.theme.derive(panel_fill_color=panel_style.get("fill_color", style.panel_fill_color)).panel_fill_color
    line_color = style.theme.derive(panel_line_color=panel_style.get("line_color", style.panel_line_color)).panel_line_color
    label_color = style.theme.derive(panel_label_color=panel_style.get("label_color", style.panel_label_color)).panel_label_color
    note_color = style.theme.derive(panel_note_color=panel_style.get("embedded_label_color", style.panel_note_color)).panel_note_color
    visual_variant = str(panel_style.get("visual_variant", style.panel_visual_variant))
    line_width_pt = float(panel_style.get("line_width_pt", 1.25))

    add_rounded_box(
        slide,
        panel_box.x,
        panel_box.y,
        panel_box.w,
        panel_box.h,
        line_color=line_color,
        fill_color=fill_color,
        line_width_pt=line_width_pt,
    )

    top_pad = float(panel.get("top_pad", 0.10))
    label_h = float(panel.get("label_h", 0.18 if label else 0.0))
    bottom_note_h = float(panel.get("bottom_note_h", 0.18 if embedded_label else 0.0))
    inter_gap = float(panel.get("inter_gap", 0.06))
    visual_pad_x = float(panel.get("visual_pad_x", 0.12))

    visual_y = panel_box.y + top_pad + (label_h + inter_gap if label else 0.0)
    visual_h_default = panel_box.h - top_pad - bottom_note_h - 0.12 - (label_h + inter_gap if label else 0.0)
    visual_h = max(0.70, min(float(panel.get("visual_h", visual_h_default)), panel_box.h - 0.30))
    visual_x = panel_box.x + visual_pad_x
    visual_w = panel_box.w - 2 * visual_pad_x

    if label:
        render_centered_text_block(
            slide,
            box=Box(panel_box.x + 0.08, panel_box.y + 0.06, panel_box.w - 0.16, max(0.16, label_h)),
            text=label,
            font_name=BODY_FONT,
            min_font=11,
            max_font=13,
            max_lines=1,
            color=label_color,
            bold=True,
        )

    if mini_visual:
        add_mini_visual(
            slide,
            kind=mini_visual,
            x=visual_x,
            y=visual_y,
            w=visual_w,
            h=visual_h,
            suffix=f"_title_composite_{idx}",
            variant=visual_variant,
        )

    if embedded_label:
        render_centered_text_block(
            slide,
            box=Box(panel_box.x + 0.08, panel_box.bottom - 0.24, panel_box.w - 0.16, 0.18),
            text=embedded_label,
            font_name=FORMULA_FONT,
            min_font=10,
            max_font=12,
            max_lines=1,
            color=note_color,
        )


def render_title_visual_composite(
    slide,
    *,
    panels: Sequence[Mapping[str, Any]],
    fallback_boxes: Sequence[Box],
    connectors: Sequence[Mapping[str, Any]],
    style: TitleCompositeStyle,
) -> list[Box]:
    actual_boxes: list[Box] = []
    for idx, (panel, fallback) in enumerate(zip(panels, fallback_boxes)):
        panel_box = _panel_box_from_spec(panel, fallback)
        actual_boxes.append(panel_box)
        render_title_visual_panel(slide, panel_box=panel_box, panel=panel, idx=idx, style=style)

    for conn in connectors or []:
        from_idx = conn.get("from")
        to_idx = conn.get("to")
        if not (
            isinstance(from_idx, int)
            and isinstance(to_idx, int)
            and 0 <= from_idx < len(actual_boxes)
            and 0 <= to_idx < len(actual_boxes)
        ):
            continue
        a = actual_boxes[from_idx]
        b = actual_boxes[to_idx]
        connector_color = style.theme.derive(connector_color=conn.get("color", style.connector_color)).connector_color
        connector_width = float(conn.get("width_pt", style.connector_width_pt))
        add_soft_connector(
            slide,
            x1=a.right,
            y1=a.y + a.h / 2,
            x2=b.x,
            y2=b.y + b.h / 2,
            color=connector_color,
            width_pt=connector_width,
        )
    return actual_boxes

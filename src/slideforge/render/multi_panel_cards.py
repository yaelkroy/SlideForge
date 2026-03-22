from __future__ import annotations

from typing import Any, Mapping, Sequence

from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, TITLE_FONT
from slideforge.layout.autofit import Box, fit_text
from slideforge.layout.multi_panel_summary import (
    MultiPanelSummaryLayout,
    allocate_multi_panel_content_heights,
    layout_multi_panel_bands,
)
from slideforge.render.primitives import add_rounded_box, add_textbox


def _fit_font_size(text: str, box: Box, *, min_font: int, max_font: int, max_lines: int | None = None, prefer_single_line: bool = False) -> int:
    if not text.strip() or box.w <= 0 or box.h <= 0:
        return max_font
    fitted = fit_text(text, box.w, box.h, min_font_size=min_font, max_font_size=max_font, max_lines=max_lines, prefer_single_line=prefer_single_line)
    return max(min_font, fitted.font_size)


def _add_fitted_text(slide, *, box: Box, text: str, font_name: str, color, min_font: int, max_font: int, max_lines: int | None = None, bold: bool = False, align=PP_ALIGN.CENTER, prefer_single_line: bool = False) -> None:
    if not text.strip() or box.w <= 0 or box.h <= 0:
        return
    add_textbox(slide, x=box.x, y=box.y, w=box.w, h=box.h, text=text, font_name=font_name, font_size=_fit_font_size(text, box, min_font=min_font, max_font=max_font, max_lines=max_lines, prefer_single_line=prefer_single_line), color=color, bold=bold, align=align)


def render_multi_panel_panels(slide, *, panels: Sequence[Mapping[str, Any]], layout_result: MultiPanelSummaryLayout, layout: Mapping[str, Any], style: Mapping[str, Any], suffix: str = "_multi_panel_summary") -> None:
    panel_inner_pad_x = float(layout.get("panel_inner_pad_x", 0.12))
    panel_inner_pad_top = float(layout.get("panel_inner_pad_top", 0.10))
    panel_inner_pad_bottom = float(layout.get("panel_inner_pad_bottom", 0.08))
    for panel, panel_box in zip(panels, layout_result.panel_boxes):
        add_rounded_box(slide, panel_box.x, panel_box.y, panel_box.w, panel_box.h, line_color=panel.get("line_color", style["panel_line_color"]), fill_color=panel.get("fill_color", style["panel_fill_color"]), line_width_pt=float(panel.get("line_width_pt", style["panel_line_width_pt"])))
        inner_x = panel_box.x + panel_inner_pad_x
        inner_w = max(0.0, panel_box.w - 2 * panel_inner_pad_x)
        inner_y = panel_box.y + panel_inner_pad_top
        inner_h = max(0.0, panel_box.h - panel_inner_pad_top - panel_inner_pad_bottom)
        panel_title = str(panel.get("title", "")).strip()
        caption_text = str(panel.get("caption", "")).strip()
        formula_text = str(panel.get("formula", "")).strip()
        heights = allocate_multi_panel_content_heights(inner_w=inner_w, content_h=inner_h, title_text=panel_title, caption_text=caption_text, formula_text=formula_text, layout=layout)
        title_box = Box(inner_x, inner_y, inner_w, heights.title_h)
        _add_fitted_text(slide, box=title_box, text=panel_title, font_name=TITLE_FONT, color=style["panel_title_color"], min_font=int(layout.get("panel_title_min_font", 12)), max_font=int(panel.get("title_font_size", layout.get("panel_title_max_font", 16))), max_lines=2, bold=True, align=PP_ALIGN.CENTER)
        visual_box = Box(inner_x, title_box.bottom + heights.title_gap, inner_w, heights.visual_h)
        mini_visual = str(panel.get("mini_visual", "")).strip()
        if mini_visual and visual_box.w > 0 and visual_box.h > 0:
            add_mini_visual(slide, kind=mini_visual, x=visual_box.x, y=visual_box.y, w=visual_box.w, h=visual_box.h, suffix=suffix, variant=str(panel.get("visual_variant", style["visual_variant"])))
        caption_box = Box(inner_x, visual_box.bottom + heights.caption_gap, inner_w, heights.caption_h)
        _add_fitted_text(slide, box=caption_box, text=caption_text, font_name=BODY_FONT, color=style["panel_caption_color"], min_font=int(layout.get("panel_caption_min_font", 11)), max_font=int(panel.get("caption_font_size", layout.get("panel_caption_max_font", 13))), max_lines=2, align=PP_ALIGN.CENTER)
        formula_y = caption_box.bottom + heights.formula_gap
        formula_box = Box(inner_x, formula_y, inner_w, max(0.0, panel_box.bottom - panel_inner_pad_bottom - formula_y))
        _add_fitted_text(slide, box=formula_box, text=formula_text, font_name=FORMULA_FONT, color=style["panel_formula_color"], min_font=int(layout.get("panel_formula_min_font", 11)), max_font=int(panel.get("formula_font_size", layout.get("panel_formula_max_font", 13))), max_lines=int(layout.get("panel_formula_max_lines", 2)), align=PP_ALIGN.CENTER)


def render_multi_panel_bands(slide, *, layout_result: MultiPanelSummaryLayout, variants, layout: Mapping[str, Any], style: Mapping[str, Any]) -> None:
    placements = layout_multi_panel_bands(layout_result=layout_result, variants=variants, layout=layout)
    if placements and bool(layout.get("use_bottom_summary_card", False)):
        side_pad = float(layout.get("bottom_summary_card_side_pad", 0.16))
        top_pad = float(layout.get("bottom_summary_card_top_pad", 0.10))
        bottom_pad = float(layout.get("bottom_summary_card_bottom_pad", 0.10))
        stack_left = min(p.box.x for p in placements)
        stack_right = max(p.box.x + p.box.w for p in placements)
        stack_top = min(p.box.y for p in placements)
        stack_bottom = max(p.box.bottom for p in placements)
        add_rounded_box(slide, x=stack_left - side_pad, y=stack_top - top_pad, w=(stack_right - stack_left) + 2 * side_pad, h=(stack_bottom - stack_top) + top_pad + bottom_pad, line_color=style["panel_line_color"], fill_color=style["panel_fill_color"], line_width_pt=float(layout.get("bottom_summary_card_line_width_pt", style["panel_line_width_pt"])))
    for placement in placements:
        add_textbox(slide, x=placement.box.x, y=placement.box.y, w=placement.box.w, h=placement.box.h, text=placement.spec.text, font_name=placement.spec.font_name, font_size=placement.font_size, color=placement.spec.color, bold=placement.spec.bold, align=placement.spec.align)

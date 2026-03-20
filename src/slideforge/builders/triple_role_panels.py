from __future__ import annotations

from typing import Any, Mapping, Sequence

from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, TITLE_FONT
from slideforge.layout.autofit import Box, distribute_columns, fit_text
from slideforge.render.primitives import add_rounded_box, add_textbox


def _fit_font_size(
    text: str,
    box: Box,
    *,
    min_font: int,
    max_font: int,
    max_lines: int | None = None,
    prefer_single_line: bool = False,
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
        prefer_single_line=prefer_single_line,
    )
    return max(min_font, fitted.font_size)


def _add_fitted_text(
    slide,
    *,
    box: Box,
    text: str,
    font_name: str,
    color,
    min_font: int,
    max_font: int,
    max_lines: int | None = None,
    bold: bool = False,
    align=PP_ALIGN.CENTER,
    prefer_single_line: bool = False,
) -> None:
    if not text.strip() or box.w <= 0 or box.h <= 0:
        return

    font_size = _fit_font_size(
        text,
        box,
        min_font=min_font,
        max_font=max_font,
        max_lines=max_lines,
        prefer_single_line=prefer_single_line,
    )
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


def render_triple_role_panels(
    slide,
    *,
    panels: Sequence[Mapping[str, Any]],
    panel_region: Box,
    layout: Mapping[str, Any],
    style: Mapping[str, Any],
) -> None:
    panel_gap = float(layout.get("panel_gap", 0.24))
    default_cols = max(1, len(panels))
    panel_boxes = distribute_columns(
        panel_region,
        default_cols,
        gap=panel_gap,
    )

    visible_panels = min(len(panels), len(panel_boxes))
    panel_boxes = panel_boxes[:visible_panels]

    panel_inner_pad_x = float(layout.get("panel_inner_pad_x", 0.12))
    panel_inner_pad_top = float(layout.get("panel_inner_pad_top", 0.10))
    visual_h = float(layout.get("panel_visual_h", 1.14))
    title_h = float(layout.get("panel_title_h", 0.24))
    caption_h = float(layout.get("panel_caption_h", 0.28))
    title_to_visual_gap = float(layout.get("title_to_visual_gap", 0.05))
    visual_to_caption_gap = float(layout.get("visual_to_caption_gap", 0.06))
    caption_to_formula_gap = float(layout.get("caption_to_formula_gap", 0.05))
    formula_bottom_pad = float(layout.get("formula_bottom_pad", 0.08))

    for panel, panel_box in zip(panels, panel_boxes):
        add_rounded_box(
            slide,
            panel_box.x,
            panel_box.y,
            panel_box.w,
            panel_box.h,
            line_color=panel.get("line_color", style["panel_line_color"]),
            fill_color=panel.get("fill_color", style["panel_fill_color"]),
            line_width_pt=float(
                panel.get("line_width_pt", style["panel_line_width_pt"])
            ),
        )

        inner_x = panel_box.x + panel_inner_pad_x
        inner_w = panel_box.w - 2 * panel_inner_pad_x

        panel_title = str(panel.get("title", "")).strip()
        title_box = Box(inner_x, panel_box.y + panel_inner_pad_top, inner_w, title_h)
        _add_fitted_text(
            slide,
            box=title_box,
            text=panel_title,
            font_name=TITLE_FONT,
            color=style["panel_title_color"],
            min_font=int(layout.get("panel_title_min_font", 12)),
            max_font=int(
                panel.get(
                    "title_font_size",
                    layout.get("panel_title_max_font", 16),
                )
            ),
            max_lines=2,
            bold=True,
            align=PP_ALIGN.CENTER,
        )

        visual_box = Box(
            inner_x,
            title_box.bottom + title_to_visual_gap,
            inner_w,
            visual_h,
        )
        mini_visual = str(panel.get("mini_visual", "")).strip()
        if mini_visual:
            add_mini_visual(
                slide,
                kind=mini_visual,
                x=visual_box.x,
                y=visual_box.y,
                w=visual_box.w,
                h=visual_box.h,
                suffix="_triple_role",
                variant=str(panel.get("visual_variant", style["visual_variant"])),
            )

        caption_text = str(panel.get("caption", "")).strip()
        caption_box = Box(
            inner_x,
            visual_box.bottom + visual_to_caption_gap,
            inner_w,
            caption_h,
        )
        _add_fitted_text(
            slide,
            box=caption_box,
            text=caption_text,
            font_name=BODY_FONT,
            color=style["panel_caption_color"],
            min_font=int(layout.get("panel_caption_min_font", 11)),
            max_font=int(
                panel.get(
                    "caption_font_size",
                    layout.get("panel_caption_max_font", 13),
                )
            ),
            max_lines=2,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

        formula_text = str(panel.get("formula", "")).strip()
        formula_box = Box(
            inner_x,
            caption_box.bottom + caption_to_formula_gap,
            inner_w,
            max(
                0.0,
                panel_box.bottom
                - (caption_box.bottom + caption_to_formula_gap)
                - formula_bottom_pad,
            ),
        )
        _add_fitted_text(
            slide,
            box=formula_box,
            text=formula_text,
            font_name=FORMULA_FONT,
            color=style["panel_formula_color"],
            min_font=int(layout.get("panel_formula_min_font", 11)),
            max_font=int(
                panel.get(
                    "formula_font_size",
                    layout.get("panel_formula_max_font", 13),
                )
            ),
            max_lines=int(layout.get("panel_formula_max_lines", 2)),
            bold=False,
            align=PP_ALIGN.CENTER,
        )
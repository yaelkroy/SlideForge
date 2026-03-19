from __future__ import annotations

from typing import Any, Mapping

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, FORMULA_FONT
from slideforge.config.themes import SlideTheme, get_theme, resolve_color
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, fit_text, layout_notation_table
from slideforge.render.header import render_header_from_spec
from slideforge.render.primitives import add_footer, add_rounded_box, add_textbox


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


def _add_cell_text(
    slide,
    *,
    box: Box,
    text: str,
    font_name: str,
    font_size: int,
    color,
    bold: bool = False,
    align=PP_ALIGN.LEFT,
) -> None:
    if not text.strip() or box.w <= 0 or box.h <= 0:
        return

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


def _box_from_dict(raw: Mapping[str, Any], fallback: Box) -> Box:
    return Box(
        raw.get("x", fallback.x),
        raw.get("y", fallback.y),
        raw.get("w", fallback.w),
        raw.get("h", fallback.h),
    )


def _looks_formula_like(text: str) -> bool:
    if not text:
        return False
    formula_chars = set("=⋅∈()[]{}₀₁₂₃₄₅₆₇₈₉±→←↦θγμσ^·/")
    return any(ch in formula_chars for ch in text)


def _resolve_notation_style(
    spec: Mapping[str, Any],
    *,
    theme_obj: SlideTheme,
) -> dict[str, Any]:
    notation_style = dict(spec.get("notation_style", {}) or {})

    table_fill_default = theme_obj.box_fill_color
    if table_fill_default is None:
        table_fill_default = theme_obj.panel_fill_color
    if table_fill_default is None:
        table_fill_default = theme_obj.box_body_color

    return {
        "table_fill_color": resolve_color(notation_style.get("table_fill_color"), table_fill_default),
        "table_line_color": resolve_color(notation_style.get("table_line_color"), theme_obj.box_line_color),
        "header_color": resolve_color(notation_style.get("header_color"), theme_obj.box_title_color),
        "symbol_color": resolve_color(notation_style.get("symbol_color"), theme_obj.body_color),
        "meaning_color": resolve_color(notation_style.get("meaning_color"), theme_obj.subtitle_color),
        "example_formula_color": resolve_color(notation_style.get("example_formula_color"), theme_obj.body_color),
        "example_text_color": resolve_color(notation_style.get("example_text_color"), theme_obj.subtitle_color),
        "formulas_color": resolve_color(notation_style.get("formulas_color"), theme_obj.body_color),
        "footer_color": resolve_color(notation_style.get("footer_color"), theme_obj.footer_color),
        "footer_dark": bool(notation_style.get("footer_dark", theme_obj.footer_dark)),
        "table_line_width_pt": float(notation_style.get("table_line_width_pt", 1.25)),
    }


def build_notation_panel_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    slide_theme_name = spec.get("theme", "concept")
    theme_obj = get_theme(slide_theme_name=slide_theme_name)

    bg = spec.get("background") or choose_background(slide_theme_name, counters)
    slide = new_slide(prs, bg)

    layout = dict(spec.get("layout", {}) or {})
    rows = list(spec.get("rows", []) or [])
    columns = list(spec.get("columns", ["symbol", "meaning", "visual example"]) or [])
    formulas = list(spec.get("formulas", []) or [])

    header_result = render_header_from_spec(
        slide,
        spec,
        theme=theme_obj,
    )

    notation_style = _resolve_notation_style(spec, theme_obj=theme_obj)

    fallback_table_box = Box(
        float(layout.get("table_x", 0.88)),
        float(layout.get("table_y", header_result.content_top_y + float(layout.get("content_to_table_gap", 0.10)))),
        float(layout.get("table_w", 11.20)),
        float(layout.get("table_h", 4.85)),
    )

    table_box_dict = layout.get("table_box")
    if isinstance(table_box_dict, Mapping):
        table_outer = _box_from_dict(table_box_dict, fallback_table_box)
    else:
        table_outer = fallback_table_box

    add_rounded_box(
        slide,
        table_outer.x,
        table_outer.y,
        table_outer.w,
        table_outer.h,
        line_color=notation_style["table_line_color"],
        fill_color=notation_style["table_fill_color"],
        line_width_pt=notation_style["table_line_width_pt"],
    )

    table_layout = layout_notation_table(
        table_outer,
        rows=len(rows),
        col_ratios=tuple(layout.get("col_ratios", (0.18, 0.38, 0.44))),
        header_h=float(layout.get("header_h", 0.34)),
        row_gap=float(layout.get("row_gap", 0.04)),
        col_gap=float(layout.get("col_gap", 0.12)),
        min_body_font=int(layout.get("min_body_font", 13)),
        max_body_font=int(layout.get("max_body_font", 18)),
        min_header_font=int(layout.get("min_header_font", 12)),
        max_header_font=int(layout.get("max_header_font", 16)),
    )

    header_cols = [
        Box(c.x, table_layout.header_box.y, c.w, table_layout.header_box.h)
        for c in table_layout.col_boxes
    ]

    for idx, header in enumerate(columns[:3]):
        header_text = str(header).strip()
        header_align = PP_ALIGN.CENTER if idx == 0 else PP_ALIGN.LEFT
        header_font = _fit_text_size(
            header_text,
            header_cols[idx],
            min_font=table_layout.recommended_header_font,
            max_font=table_layout.recommended_header_font,
            max_lines=2,
        )
        _add_cell_text(
            slide,
            box=header_cols[idx],
            text=header_text,
            font_name=BODY_FONT,
            font_size=header_font,
            color=notation_style["header_color"],
            bold=True,
            align=header_align,
        )

    for row_idx, row in enumerate(rows):
        if row_idx >= len(table_layout.row_boxes):
            break

        row_box = table_layout.row_boxes[row_idx]

        symbol_box = Box(
            table_layout.col_boxes[0].x,
            row_box.y,
            table_layout.col_boxes[0].w,
            row_box.h,
        )
        meaning_box = Box(
            table_layout.col_boxes[1].x,
            row_box.y,
            table_layout.col_boxes[1].w,
            row_box.h,
        )
        example_box = Box(
            table_layout.col_boxes[2].x,
            row_box.y,
            table_layout.col_boxes[2].w,
            row_box.h,
        )

        symbol_text = str(row.get("symbol", "")).strip()
        meaning_text = str(row.get("meaning", "")).strip()
        example_text = str(row.get("example", "")).strip()

        symbol_font = _fit_text_size(
            symbol_text,
            symbol_box,
            min_font=max(14, table_layout.recommended_body_font),
            max_font=max(16, table_layout.recommended_body_font + 1),
            max_lines=2,
        )
        meaning_font = _fit_text_size(
            meaning_text,
            meaning_box,
            min_font=max(13, table_layout.recommended_body_font - 1),
            max_font=table_layout.recommended_body_font,
            max_lines=3,
        )
        example_font = _fit_text_size(
            example_text,
            example_box,
            min_font=max(13, table_layout.recommended_body_font - 1),
            max_font=table_layout.recommended_body_font,
            max_lines=3,
        )

        _add_cell_text(
            slide,
            box=symbol_box,
            text=symbol_text,
            font_name=FORMULA_FONT,
            font_size=symbol_font,
            color=notation_style["symbol_color"],
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        _add_cell_text(
            slide,
            box=meaning_box,
            text=meaning_text,
            font_name=BODY_FONT,
            font_size=meaning_font,
            color=notation_style["meaning_color"],
            bold=False,
            align=PP_ALIGN.LEFT,
        )

        example_font_name = FORMULA_FONT if _looks_formula_like(example_text) else BODY_FONT
        example_color = (
            notation_style["example_formula_color"]
            if example_font_name == FORMULA_FONT
            else notation_style["example_text_color"]
        )

        _add_cell_text(
            slide,
            box=example_box,
            text=example_text,
            font_name=example_font_name,
            font_size=example_font,
            color=example_color,
            bold=False,
            align=PP_ALIGN.LEFT,
        )

    if formulas:
        formula_text = "   •   ".join(
            item.strip() for item in formulas if item and item.strip()
        )
        formula_box = Box(
            float(layout.get("formula_x", 1.00)),
            float(layout.get("formula_y", max(table_outer.bottom + 0.18, 6.55))),
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
            color=notation_style["formulas_color"],
            bold=False,
            align=layout.get("formula_align", PP_ALIGN.CENTER),
        )

    add_footer(
        slide,
        dark=notation_style["footer_dark"],
        color=notation_style["footer_color"],
    )
from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, NAVY, SLATE, TITLE_FONT
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, fit_text, layout_notation_table
from slideforge.render.primitives import add_divider_line, add_footer, add_rounded_box, add_textbox


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


def build_notation_panel_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    theme = spec.get("theme", "concept")
    bg = spec.get("background") or choose_background(theme, counters)
    slide = new_slide(prs, bg)

    layout = spec.get("layout", {})
    title = spec.get("title") or spec["slide_title"]
    subtitle = spec.get("subtitle", "").strip()
    rows = spec.get("rows", [])
    columns = spec.get("columns", ["symbol", "meaning", "visual example"])
    formulas = spec.get("formulas", [])

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
        add_textbox(
            slide,
            x=0.96,
            y=layout.get("subtitle_y", 0.98),
            w=11.08,
            h=0.42,
            text=subtitle,
            font_name=BODY_FONT,
            font_size=16,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    table_box_dict = layout.get(
        "table_box",
        {"x": 0.88, "y": 1.55, "w": 11.20, "h": 4.85},
    )
    table_outer = Box(
        table_box_dict["x"],
        table_box_dict["y"],
        table_box_dict["w"],
        table_box_dict["h"],
    )

    add_rounded_box(
        slide,
        table_outer.x,
        table_outer.y,
        table_outer.w,
        table_outer.h,
    )

    table_layout = layout_notation_table(
        table_outer,
        rows=len(rows),
        col_ratios=tuple(layout.get("col_ratios", (0.18, 0.38, 0.44))),
        header_h=layout.get("header_h", 0.34),
        row_gap=layout.get("row_gap", 0.04),
        col_gap=layout.get("col_gap", 0.12),
        min_body_font=layout.get("min_body_font", 13),
        max_body_font=layout.get("max_body_font", 18),
        min_header_font=layout.get("min_header_font", 12),
        max_header_font=layout.get("max_header_font", 16),
    )

    inner = table_outer.inset(0.14, 0.10)

    header_cols = [
        Box(c.x, table_layout.header_box.y, c.w, table_layout.header_box.h)
        for c in table_layout.col_boxes
    ]

    for idx, header in enumerate(columns[:3]):
        header_align = PP_ALIGN.CENTER if idx == 0 else PP_ALIGN.LEFT
        header_font = _fit_text_size(
            header,
            header_cols[idx],
            min_font=table_layout.recommended_header_font,
            max_font=table_layout.recommended_header_font,
            max_lines=2,
        )
        _add_cell_text(
            slide,
            box=header_cols[idx],
            text=header,
            font_name=BODY_FONT,
            font_size=header_font,
            color=SLATE,
            bold=True,
            align=header_align,
        )

    for row_idx, row in enumerate(rows):
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

        symbol_text = row.get("symbol", "").strip()
        meaning_text = row.get("meaning", "").strip()
        example_text = row.get("example", "").strip()

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
            color=NAVY,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        _add_cell_text(
            slide,
            box=meaning_box,
            text=meaning_text,
            font_name=BODY_FONT,
            font_size=meaning_font,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.LEFT,
        )

        example_font_name = FORMULA_FONT if any(
            ch in example_text for ch in "=⋅∈()[]{}₀₁₂₃₄₅₆₇₈₉±→"
        ) else BODY_FONT

        _add_cell_text(
            slide,
            box=example_box,
            text=example_text,
            font_name=example_font_name,
            font_size=example_font,
            color=NAVY if example_font_name == FORMULA_FONT else SLATE,
            bold=False,
            align=PP_ALIGN.LEFT,
        )

    if formulas:
        formula_text = "   •   ".join(
            item.strip() for item in formulas if item and item.strip()
        )
        formula_box = Box(
            1.00,
            layout.get("formula_y", 6.55),
            11.00,
            0.22,
        )
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

    add_footer(slide, dark=False)
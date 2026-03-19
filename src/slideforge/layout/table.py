from __future__ import annotations

from dataclasses import dataclass

from slideforge.layout.base import Box, Unit
from slideforge.layout.grid import distribute_columns, distribute_rows
from slideforge.layout.text_fit import clamp


@dataclass
class TableLayoutResult:
    outer_box: Box
    header_box: Box
    row_boxes: list[Box]
    col_boxes: list[Box]
    recommended_body_font: int
    recommended_header_font: int


def layout_notation_table(
    outer_box: Box,
    *,
    rows: int,
    col_ratios: tuple[float, float, float] = (0.18, 0.38, 0.44),
    header_h: Unit = 0.34,
    row_gap: Unit = 0.04,
    col_gap: Unit = 0.12,
    min_body_font: int = 13,
    max_body_font: int = 18,
    min_header_font: int = 12,
    max_header_font: int = 16,
) -> TableLayoutResult:
    """
    Compute a notation table layout with readable row height and a recommended font size.

    This intentionally avoids tiny table fonts by deriving body font primarily from row height.
    """
    inner = outer_box.inset(0.14, 0.10)
    header_box = Box(inner.x, inner.y, inner.w, header_h)

    body_y = header_box.bottom + 0.06
    body_h = max(0.0, inner.bottom - body_y)

    row_boxes = distribute_rows(
        Box(inner.x, body_y, inner.w, body_h),
        rows,
        gap=row_gap,
    )
    col_boxes = distribute_columns(
        Box(inner.x, body_y, inner.w, body_h),
        3,
        gap=col_gap,
        ratios=col_ratios,
    )

    row_h = row_boxes[0].h if row_boxes else 0.45

    body_by_height = int((row_h * 72.0) / 1.35)
    recommended_body_font = int(clamp(body_by_height, min_body_font, max_body_font))

    header_by_height = int((header_h * 72.0) / 1.25)
    recommended_header_font = int(clamp(header_by_height, min_header_font, max_header_font))

    return TableLayoutResult(
        outer_box=outer_box,
        header_box=header_box,
        row_boxes=row_boxes,
        col_boxes=col_boxes,
        recommended_body_font=recommended_body_font,
        recommended_header_font=recommended_header_font,
    )
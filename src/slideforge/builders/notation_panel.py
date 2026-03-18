from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, NAVY, SLATE, TITLE_FONT
from slideforge.io.backgrounds import choose_background
from slideforge.render.primitives import add_divider_line, add_footer, add_rounded_box, add_textbox


def build_notation_panel_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    theme = spec.get("theme", "concept")
    bg = spec.get("background") or choose_background(theme, counters)
    slide = new_slide(prs, bg)

    layout = spec.get("layout", {})
    table_box = layout.get("table_box", {"x": 0.78, "y": 1.55, "w": 11.55, "h": 4.85})
    rows = spec.get("rows", [])

    add_textbox(
        slide,
        x=0.80,
        y=layout.get("title_y", 0.42),
        w=11.70,
        h=0.50,
        text=spec["title"],
        font_name=TITLE_FONT,
        font_size=24,
        color=NAVY,
        bold=True,
    )
    add_divider_line(slide, dark=False)

    subtitle = spec.get("subtitle", "").strip()
    if subtitle:
        add_textbox(
            slide,
            x=0.95,
            y=layout.get("subtitle_y", 0.98),
            w=11.10,
            h=0.42,
            text=subtitle,
            font_name=BODY_FONT,
            font_size=14,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    add_rounded_box(slide, table_box["x"], table_box["y"], table_box["w"], table_box["h"])

    columns = spec.get("columns", ["symbol", "meaning", "visual example"])
    col_x = [
        table_box["x"] + 0.20,
        table_box["x"] + 2.20,
        table_box["x"] + 7.10,
    ]
    col_w = [1.50, 4.50, 3.95]

    for idx, header in enumerate(columns[:3]):
        add_textbox(
            slide,
            x=col_x[idx],
            y=table_box["y"] + 0.10,
            w=col_w[idx],
            h=0.22,
            text=header,
            font_name=BODY_FONT,
            font_size=12,
            color=SLATE,
            bold=True,
            align=PP_ALIGN.CENTER if idx == 0 else PP_ALIGN.LEFT,
        )

    row_top = table_box["y"] + 0.44
    row_h = (table_box["h"] - 0.58) / max(1, len(rows))

    for idx, row in enumerate(rows):
        y = row_top + idx * row_h

        add_textbox(
            slide,
            x=col_x[0],
            y=y,
            w=col_w[0],
            h=row_h,
            text=row.get("symbol", ""),
            font_name=FORMULA_FONT,
            font_size=13,
            color=NAVY,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        add_textbox(
            slide,
            x=col_x[1],
            y=y,
            w=col_w[1],
            h=row_h,
            text=row.get("meaning", ""),
            font_name=BODY_FONT,
            font_size=11,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.LEFT,
        )
        add_textbox(
            slide,
            x=col_x[2],
            y=y,
            w=col_w[2],
            h=row_h,
            text=row.get("example", ""),
            font_name=FORMULA_FONT if any(ch in row.get("example", "") for ch in "=⋅∈()[]{}") else BODY_FONT,
            font_size=11,
            color=NAVY,
            bold=False,
            align=PP_ALIGN.LEFT,
        )

    formulas = spec.get("formulas", [])
    if formulas:
        add_textbox(
            slide,
            x=1.00,
            y=layout.get("formula_y", 6.55),
            w=11.00,
            h=0.20,
            text="   •   ".join(formulas),
            font_name=FORMULA_FONT,
            font_size=10,
            color=NAVY,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    add_footer(slide, dark=False)
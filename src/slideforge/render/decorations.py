from __future__ import annotations

from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

from slideforge.config.constants import (
    ACCENT,
    BODY_FONT,
    GHOST_TEXT,
    OFFWHITE,
    SLATE,
    TITLE_PANEL_FILL,
    TITLE_PANEL_LINE,
)
from slideforge.render.cards import _add_shape, add_rounded_box
from slideforge.render.text import _add_text_to_shape, add_textbox



def add_divider_line(
    slide,
    dark: bool = False,
    *,
    x: float = 0.8,
    y: float = 1.1,
    w: float = 2.4,
    h: float = 0.04,
    color: RGBColor | None = None,
) -> None:
    actual_color = color or (OFFWHITE if dark else ACCENT)
    _add_shape(
        slide,
        shape_type=MSO_SHAPE.RECTANGLE,
        x=x,
        y=y,
        w=w,
        h=h,
        line_color=actual_color,
        fill_color=actual_color,
        line_width_pt=0.75,
    )



def add_header_rule(
    slide,
    *,
    x: float = 0.8,
    y: float = 1.1,
    w: float = 2.4,
    h: float = 0.04,
    color: RGBColor = ACCENT,
) -> None:
    add_divider_line(slide, x=x, y=y, w=w, h=h, color=color)



def add_callout(
    slide,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    font_size: int = 11,
    color: RGBColor = SLATE,
    bold: bool = False,
    align=PP_ALIGN.CENTER,
):
    add_textbox(
        slide,
        x=x,
        y=y,
        w=w,
        h=h,
        text=text,
        font_name=BODY_FONT,
        font_size=font_size,
        color=color,
        bold=bold,
        align=align,
    )



def add_pill_tag(
    slide,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    fill_color: RGBColor = TITLE_PANEL_FILL,
    line_color: RGBColor = TITLE_PANEL_LINE,
    text_color: RGBColor = OFFWHITE,
    font_size: int = 12,
    bold: bool = False,
):
    shape = add_rounded_box(
        slide,
        x=x,
        y=y,
        w=w,
        h=h,
        line_color=line_color,
        fill_color=fill_color,
        line_width_pt=1.0,
    )
    _add_text_to_shape(
        shape,
        text=text,
        font_name=BODY_FONT,
        font_size=font_size,
        color=text_color,
        bold=bold,
        align=PP_ALIGN.CENTER,
        vertical_anchor=MSO_ANCHOR.MIDDLE,
    )



def add_ghost_label(
    slide,
    x: float,
    y: float,
    w: float,
    text: str,
    font_size: int = 10,
    color: RGBColor = GHOST_TEXT,
) -> None:
    add_textbox(
        slide,
        x=x,
        y=y,
        w=w,
        h=0.2,
        text=text,
        font_name=BODY_FONT,
        font_size=font_size,
        color=color,
        bold=False,
        align=PP_ALIGN.CENTER,
    )


__all__ = [
    "add_callout",
    "add_divider_line",
    "add_ghost_label",
    "add_header_rule",
    "add_pill_tag",
]

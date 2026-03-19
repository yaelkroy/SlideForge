from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

from slideforge.config.constants import BODY_FONT, TITLE_FONT
from slideforge.config.themes import SlideTheme, get_theme
from slideforge.layout.autofit import Box, TextFit, fit_text
from slideforge.render.primitives import add_divider_line, add_textbox


@dataclass(frozen=True)
class HeaderTextSpec:
    text: str
    font_name: str
    min_font_size: int
    max_font_size: int
    max_lines: int
    color: RGBColor
    bold: bool = False
    align: Any = PP_ALIGN.LEFT
    line_spacing: float = 1.15
    prefer_single_line: bool = False
    vertical_anchor: Any = MSO_ANCHOR.TOP


@dataclass(frozen=True)
class HeaderBlock:
    box: Box
    fit: TextFit
    spec: HeaderTextSpec


@dataclass
class HeaderLayoutResult:
    title: HeaderBlock
    divider_box: Box | None
    subtitle: HeaderBlock | None
    content_top_y: float
    content_top_box: Box
    debug: dict[str, Any] = field(default_factory=dict)


def _fit_block(
    text: str,
    box: Box,
    *,
    font_name: str,
    min_font_size: int,
    max_font_size: int,
    max_lines: int,
    color: RGBColor,
    bold: bool = False,
    align=PP_ALIGN.LEFT,
    line_spacing: float = 1.15,
    prefer_single_line: bool = False,
    vertical_anchor=MSO_ANCHOR.TOP,
) -> HeaderBlock:
    safe_text = (text or "").strip()
    fit = fit_text(
        safe_text,
        box.w,
        box.h,
        min_font_size=min_font_size,
        max_font_size=max_font_size,
        line_spacing=line_spacing,
        prefer_single_line=prefer_single_line,
        max_lines=max_lines,
    )
    actual_h = min(box.h, max(0.12, fit.estimated_height))
    actual_box = Box(box.x, box.y, box.w, actual_h)
    spec = HeaderTextSpec(
        text=safe_text,
        font_name=font_name,
        min_font_size=min_font_size,
        max_font_size=max_font_size,
        max_lines=max_lines,
        color=color,
        bold=bold,
        align=align,
        line_spacing=line_spacing,
        prefer_single_line=prefer_single_line,
        vertical_anchor=vertical_anchor,
    )
    return HeaderBlock(box=actual_box, fit=fit, spec=spec)


def _draw_block(slide, block: HeaderBlock) -> None:
    add_textbox(
        slide,
        x=block.box.x,
        y=block.box.y,
        w=block.box.w,
        h=block.box.h,
        text=block.spec.text,
        font_name=block.spec.font_name,
        font_size=block.fit.font_size,
        color=block.spec.color,
        bold=block.spec.bold,
        align=block.spec.align,
        vertical_anchor=block.spec.vertical_anchor,
    )


def _resolve_theme(
    spec: Mapping[str, Any] | None = None,
    *,
    theme: str | SlideTheme | None = None,
    slide_theme_name: str | None = None,
    override_key: str = "header_style",
) -> SlideTheme:
    overrides = {}
    if spec:
        overrides = dict(spec.get(override_key, {}) or {})
    return get_theme(theme, slide_theme_name=slide_theme_name, overrides=overrides)


def layout_header(
    *,
    title: str,
    subtitle: str = "",
    theme: str | SlideTheme | None = None,
    slide_theme_name: str | None = None,
    header_style: Mapping[str, Any] | None = None,
    layout: Mapping[str, Any] | None = None,
) -> HeaderLayoutResult:
    layout = dict(layout or {})
    theme_obj = get_theme(
        theme,
        slide_theme_name=slide_theme_name,
        overrides=header_style or {},
    )

    title_box_budget = Box(
        layout.get("title_x", 0.80),
        layout.get("title_y", 0.42),
        layout.get("title_w", 11.70),
        layout.get("title_h", 0.80),
    )
    title_block = _fit_block(
        title,
        title_box_budget,
        font_name=layout.get("title_font_name", TITLE_FONT),
        min_font_size=int(layout.get("title_min_font", 21)),
        max_font_size=int(layout.get("title_max_font", 30)),
        max_lines=int(layout.get("title_max_lines", 3)),
        color=layout.get("title_color", theme_obj.title_color),
        bold=bool(layout.get("title_bold", True)),
        align=layout.get("title_align", PP_ALIGN.LEFT),
        line_spacing=float(layout.get("title_line_spacing", 1.10)),
        prefer_single_line=bool(layout.get("title_prefer_single_line", False)),
        vertical_anchor=layout.get("title_vertical_anchor", MSO_ANCHOR.TOP),
    )

    show_divider = bool(layout.get("show_divider", True))
    divider_gap = float(layout.get("title_to_divider_gap", 0.10))
    divider_h = float(layout.get("divider_h", 0.04))
    divider_x = float(layout.get("divider_x", 0.80))
    divider_w = float(layout.get("divider_w", 2.40))
    divider_y = float(layout.get("divider_y", title_block.box.bottom + divider_gap))
    divider_color = layout.get("divider_color", theme_obj.divider_color)

    divider_box = None
    if show_divider:
        divider_box = Box(divider_x, divider_y, divider_w, divider_h)

    subtitle_text = (subtitle or "").strip()
    subtitle_block: HeaderBlock | None = None

    if subtitle_text:
        subtitle_y = float(
            layout.get(
                "subtitle_y",
                (divider_box.bottom if divider_box else title_block.box.bottom) + float(layout.get("divider_to_subtitle_gap", 0.12)),
            )
        )
        subtitle_box_budget = Box(
            layout.get("subtitle_x", 0.96),
            subtitle_y,
            layout.get("subtitle_w", 11.08),
            layout.get("subtitle_h", 0.52),
        )
        subtitle_block = _fit_block(
            subtitle_text,
            subtitle_box_budget,
            font_name=layout.get("subtitle_font_name", BODY_FONT),
            min_font_size=int(layout.get("subtitle_min_font", 13)),
            max_font_size=int(layout.get("subtitle_max_font", 17)),
            max_lines=int(layout.get("subtitle_max_lines", 2)),
            color=layout.get("subtitle_color", theme_obj.subtitle_color),
            bold=bool(layout.get("subtitle_bold", False)),
            align=layout.get("subtitle_align", PP_ALIGN.CENTER),
            line_spacing=float(layout.get("subtitle_line_spacing", 1.12)),
            prefer_single_line=bool(layout.get("subtitle_prefer_single_line", False)),
            vertical_anchor=layout.get("subtitle_vertical_anchor", MSO_ANCHOR.TOP),
        )

    content_gap = float(layout.get("subtitle_to_content_gap", 0.18))
    if subtitle_block is not None:
        content_top_y = float(layout.get("content_top_y", subtitle_block.box.bottom + content_gap))
    elif divider_box is not None:
        content_top_y = float(layout.get("content_top_y", divider_box.bottom + content_gap))
    else:
        content_top_y = float(layout.get("content_top_y", title_block.box.bottom + content_gap))

    content_top_box = Box(
        layout.get("content_x", 0.80),
        content_top_y,
        layout.get("content_w", 11.70),
        layout.get("content_h", max(0.0, 7.50 - content_top_y - 0.35)),
    )

    return HeaderLayoutResult(
        title=title_block,
        divider_box=divider_box,
        subtitle=subtitle_block,
        content_top_y=content_top_y,
        content_top_box=content_top_box,
        debug={
            "theme_name": theme_obj.name,
            "show_divider": show_divider,
        },
    )


def render_header(
    slide,
    *,
    title: str,
    subtitle: str = "",
    theme: str | SlideTheme | None = None,
    slide_theme_name: str | None = None,
    header_style: Mapping[str, Any] | None = None,
    layout: Mapping[str, Any] | None = None,
) -> HeaderLayoutResult:
    result = layout_header(
        title=title,
        subtitle=subtitle,
        theme=theme,
        slide_theme_name=slide_theme_name,
        header_style=header_style,
        layout=layout,
    )

    _draw_block(slide, result.title)

    if result.divider_box is not None:
        add_divider_line(
            slide,
            x=result.divider_box.x,
            y=result.divider_box.y,
            w=result.divider_box.w,
            h=result.divider_box.h,
            color=(layout or {}).get("divider_color", get_theme(theme, slide_theme_name=slide_theme_name, overrides=header_style or {}).divider_color),
        )

    if result.subtitle is not None:
        _draw_block(slide, result.subtitle)

    return result


def render_header_from_spec(
    slide,
    spec: Mapping[str, Any],
    *,
    theme: str | SlideTheme | None = None,
    title_key: str = "title",
    fallback_title_key: str = "slide_title",
    subtitle_key: str = "subtitle",
    layout_key: str = "layout",
    header_style_key: str = "header_style",
) -> HeaderLayoutResult:
    layout = dict(spec.get(layout_key, {}) or {})
    header_style = dict(spec.get(header_style_key, {}) or {})
    slide_theme_name = spec.get("theme")

    title = str(spec.get(title_key) or spec.get(fallback_title_key) or "").strip()
    subtitle = str(spec.get(subtitle_key, "") or "").strip()

    return render_header(
        slide,
        title=title,
        subtitle=subtitle,
        theme=theme,
        slide_theme_name=slide_theme_name,
        header_style=header_style,
        layout=layout,
    )


def content_box_from_header(
    header_result: HeaderLayoutResult,
    *,
    x: float = 0.90,
    right_margin: float = 1.23,
    bottom_margin: float = 1.10,
    slide_width: float = 13.333,
    slide_height: float = 7.5,
) -> Box:
    return Box(
        x=x,
        y=header_result.content_top_y,
        w=max(0.0, slide_width - x - right_margin),
        h=max(0.0, slide_height - header_result.content_top_y - bottom_margin),
    )
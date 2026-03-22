from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, TITLE_FONT
from slideforge.io.backgrounds import choose_background
from slideforge.layout.title_composite import layout_title_composite
from slideforge.render.primitives import add_footer
from slideforge.render.title_panels import render_centered_text_block, render_title_visual_composite
from slideforge.style.title_style import resolve_title_style


def _join_items(items: list[str]) -> str:
    return "   •   ".join(str(item).strip() for item in items if str(item).strip())


def build_title_composite_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    slide_theme_name = str(spec.get("theme", "title"))
    bg = spec.get("background") or choose_background(slide_theme_name, counters)
    slide = new_slide(prs, bg)

    layout = dict(spec.get("layout", {}) or {})
    style = resolve_title_style(spec, slide_theme_name=slide_theme_name)
    title_layout = layout_title_composite(layout, panel_count=len(list(spec.get("composite_visual", {}).get("panels", []) or [])))

    title = spec.get("title") or spec["slide_title"]
    subtitle = str(spec.get("subtitle", "")).strip()
    author_line = str(spec.get("author_line", "")).strip()
    tiny_footer = str(spec.get("tiny_footer", "")).strip()
    bullets_text = _join_items(list(spec.get("bullets", []) or []))

    render_centered_text_block(
        slide,
        box=title_layout.title_box,
        text=title,
        font_name=TITLE_FONT,
        min_font=int(layout.get("title_min_font", 24)),
        max_font=int(layout.get("title_max_font", 32)),
        max_lines=int(layout.get("title_max_lines", 3)),
        color=style.title_color,
        bold=True,
    )

    if subtitle:
        render_centered_text_block(
            slide,
            box=title_layout.subtitle_box,
            text=subtitle,
            font_name=BODY_FONT,
            min_font=int(layout.get("subtitle_min_font", 15)),
            max_font=int(layout.get("subtitle_max_font", 18)),
            max_lines=int(layout.get("subtitle_max_lines", 2)),
            color=style.subtitle_color,
        )

    if spec.get("show_author_line", True) and author_line:
        render_centered_text_block(
            slide,
            box=title_layout.author_box,
            text=author_line,
            font_name=BODY_FONT,
            min_font=int(layout.get("author_min_font", 11)),
            max_font=int(layout.get("author_max_font", 13)),
            max_lines=1,
            color=style.author_color,
        )

    composite_visual = dict(spec.get("composite_visual", {}) or {})
    panels = list(composite_visual.get("panels", []) or [])
    if panels:
        render_title_visual_composite(
            slide,
            panels=panels,
            fallback_boxes=title_layout.panel_boxes,
            connectors=list(composite_visual.get("connectors", []) or []),
            style=style,
        )

    if bullets_text:
        render_centered_text_block(
            slide,
            box=title_layout.bullets_box,
            text=bullets_text,
            font_name=BODY_FONT,
            min_font=int(layout.get("bullets_min_font", 12)),
            max_font=int(layout.get("bullets_max_font", 14)),
            max_lines=int(layout.get("bullets_max_lines", 2)),
            color=style.bullets_color,
            bold=True,
        )

    if tiny_footer:
        render_centered_text_block(
            slide,
            box=title_layout.tiny_footer_box,
            text=tiny_footer,
            font_name=BODY_FONT,
            min_font=int(layout.get("tiny_footer_min_font", 10)),
            max_font=int(layout.get("tiny_footer_max_font", 12)),
            max_lines=1,
            color=style.tiny_footer_color,
        )

    if spec.get("show_footer_author", True):
        add_footer(slide, dark=style.footer_dark, color=style.theme.footer_color)

from __future__ import annotations

from typing import Any, Mapping

from pptx import Presentation

from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, FORMULA_FONT
from slideforge.config.themes import get_theme
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box
from slideforge.layout.multi_panel_summary import build_multi_panel_band_specs, layout_multi_panel_summary
from slideforge.render.header import render_header_from_spec
from slideforge.render.multi_panel_cards import render_multi_panel_bands, render_multi_panel_panels
from slideforge.render.primitives import add_footer
from slideforge.style.multi_panel_summary_style import resolve_multi_panel_summary_style


def _join_items(items: list[str]) -> str:
    return "   •   ".join(item.strip() for item in items if item and item.strip())


def _box_from_dict(raw: Mapping[str, Any], fallback: Box) -> Box:
    return Box(raw.get("x", fallback.x), raw.get("y", fallback.y), raw.get("w", fallback.w), raw.get("h", fallback.h))


def build_multi_panel_summary_slide(prs: Presentation, spec: dict[str, Any], counters: dict[str, int]) -> None:
    slide_theme_name = spec.get("theme", "concept")
    theme_obj = get_theme(slide_theme_name=slide_theme_name)
    bg = spec.get("background") or choose_background(slide_theme_name, counters)
    slide = new_slide(prs, bg)

    layout = dict(spec.get("layout", {}) or {})
    style = resolve_multi_panel_summary_style(spec, theme_obj=theme_obj)
    panels = list(spec.get("panels", []) or [])
    bullets_text = _join_items(list(spec.get("bullets", []) or []))
    formulas_text = _join_items(list(spec.get("formulas", []) or []))
    takeaway = str(spec.get("takeaway", "")).strip()

    header_result = render_header_from_spec(slide, spec, theme=theme_obj)
    panel_region_fallback = Box(
        float(layout.get("panel_x", 0.88)),
        float(layout.get("panel_y", header_result.content_top_y + float(layout.get("content_to_panel_gap", 0.14)))),
        float(layout.get("panel_w", 11.24)),
        float(layout.get("panel_h", 3.05)),
    )
    panel_region_raw = layout.get("panel_region")
    panel_region = _box_from_dict(panel_region_raw, panel_region_fallback) if isinstance(panel_region_raw, Mapping) else panel_region_fallback

    layout_result = layout_multi_panel_summary(panel_region, panel_count=len(panels), layout=layout)
    render_multi_panel_panels(slide, panels=panels, layout_result=layout_result, layout=layout, style=style)

    if bool(layout.get("use_manual_bottom_bands", False)):
        from slideforge.render.primitives import add_textbox
        occupied_bottom = panel_region.bottom
        band_x = float(layout.get("bottom_text_x", panel_region.x + float(layout.get("bottom_text_side_pad", 0.48))))
        band_w = float(layout.get("bottom_text_w", panel_region.w - 2 * float(layout.get("bottom_text_side_pad", 0.48))))
        if bullets_text:
            add_textbox(slide, x=band_x, y=float(layout.get("bullets_y", occupied_bottom + 0.18)), w=band_w, h=float(layout.get("bullets_h", 0.28)), text=bullets_text, font_name=BODY_FONT, font_size=int(layout.get("bullets_max_font", 13)), color=style["bullets_color"], bold=bool(layout.get("bullets_bold", False)), align=layout.get("bullets_align"))
        if formulas_text:
            add_textbox(slide, x=band_x, y=float(layout.get("formula_y", occupied_bottom + 0.56)), w=band_w, h=float(layout.get("formula_h", 0.28)), text=formulas_text, font_name=FORMULA_FONT, font_size=int(layout.get("formula_max_font", 13)), color=style["formulas_color"], bold=False, align=layout.get("formula_align"))
        if takeaway:
            add_textbox(slide, x=band_x, y=float(layout.get("takeaway_y", occupied_bottom + 0.92)), w=band_w, h=float(layout.get("takeaway_h", 0.30)), text=takeaway, font_name=BODY_FONT, font_size=int(layout.get("takeaway_max_font", 13)), color=style["takeaway_color"], bold=True, align=layout.get("takeaway_align"))
    else:
        variants = build_multi_panel_band_specs(bullets_text=bullets_text, formulas_text=formulas_text, takeaway=takeaway, style=style, layout=layout, body_font=BODY_FONT, formula_font=FORMULA_FONT)
        render_multi_panel_bands(slide, layout_result=layout_result, variants=variants, layout=layout, style=style)

    add_footer(slide, dark=style["footer_dark"], color=style["footer_color"])

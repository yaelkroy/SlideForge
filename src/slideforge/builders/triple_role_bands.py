from __future__ import annotations

from typing import Any, Mapping

from slideforge.config.constants import BODY_FONT, FORMULA_FONT
from slideforge.layout.multi_panel_summary import build_multi_panel_band_specs, layout_multi_panel_summary
from slideforge.render.multi_panel_cards import render_multi_panel_bands


def render_triple_role_bottom_bands(
    slide,
    *,
    panel_region,
    bullets_text: str,
    formulas_text: str,
    takeaway: str,
    layout: Mapping[str, Any],
    style: Mapping[str, Any],
) -> None:
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
        return
    layout_result = layout_multi_panel_summary(panel_region, panel_count=0, layout=layout)
    variants = build_multi_panel_band_specs(bullets_text=bullets_text, formulas_text=formulas_text, takeaway=takeaway, style=style, layout=layout, body_font=BODY_FONT, formula_font=FORMULA_FONT)
    render_multi_panel_bands(slide, layout_result=layout_result, variants=variants, layout=layout, style=style)


__all__ = ["render_triple_role_bottom_bands"]

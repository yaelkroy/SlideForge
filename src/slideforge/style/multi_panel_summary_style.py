from __future__ import annotations

from typing import Any, Mapping

from slideforge.config.constants import OFFWHITE
from slideforge.config.themes import SlideTheme, resolve_color


def resolve_multi_panel_summary_style(
    spec: Mapping[str, Any],
    *,
    theme_obj: SlideTheme,
) -> dict[str, Any]:
    raw = dict(spec.get("multi_panel_summary_style", {}) or {})
    legacy = dict(spec.get("triple_role_style", {}) or {})
    role_style = {**legacy, **raw}

    panel_fill_default = theme_obj.box_fill_color or theme_obj.panel_fill_color or OFFWHITE
    panel_line_default = theme_obj.box_line_color or theme_obj.panel_line_color

    return {
        "panel_fill_color": resolve_color(role_style.get("panel_fill_color"), panel_fill_default),
        "panel_line_color": resolve_color(role_style.get("panel_line_color"), panel_line_default),
        "panel_title_color": resolve_color(role_style.get("panel_title_color"), theme_obj.box_title_color),
        "panel_caption_color": resolve_color(role_style.get("panel_caption_color"), theme_obj.subtitle_color),
        "panel_formula_color": resolve_color(role_style.get("panel_formula_color"), theme_obj.body_color),
        "bullets_color": resolve_color(role_style.get("bullets_color"), theme_obj.subtitle_color),
        "formulas_color": resolve_color(role_style.get("formulas_color"), theme_obj.body_color),
        "takeaway_color": resolve_color(role_style.get("takeaway_color"), theme_obj.subtitle_color),
        "footer_color": resolve_color(role_style.get("footer_color"), theme_obj.footer_color),
        "footer_dark": bool(role_style.get("footer_dark", theme_obj.footer_dark)),
        "visual_variant": str(role_style.get("visual_variant", theme_obj.panel_visual_variant)),
        "panel_line_width_pt": float(role_style.get("panel_line_width_pt", 1.2)),
    }

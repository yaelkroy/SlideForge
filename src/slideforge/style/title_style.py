from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from pptx.dml.color import RGBColor

from slideforge.config.themes import SlideTheme, get_theme, resolve_color


@dataclass(frozen=True)
class TitleCompositeStyle:
    theme: SlideTheme
    title_color: RGBColor
    subtitle_color: RGBColor
    author_color: RGBColor
    bullets_color: RGBColor
    tiny_footer_color: RGBColor
    panel_fill_color: RGBColor | None
    panel_line_color: RGBColor
    panel_label_color: RGBColor
    panel_note_color: RGBColor
    panel_visual_variant: str
    connector_color: RGBColor
    connector_width_pt: float
    footer_dark: bool


_TITLE_STYLE_THEME_ALIASES: dict[str, str] = {
    "inherit": "",
    "light_academic": "light_academic",
    "dark_hero": "dark_hero",
    "dark_section": "dark_section",
    "light_title": "light_academic",
    "dark_title": "dark_hero",
}


def _legacy_style_preset_to_theme(preset: str | None, slide_theme_name: str | None) -> str | None:
    if not preset:
        return None
    key = str(preset).strip().lower()
    if key in _TITLE_STYLE_THEME_ALIASES:
        resolved = _TITLE_STYLE_THEME_ALIASES[key]
        return resolved or None
    if key == "title":
        return "dark_hero"
    if key == "section":
        return "dark_section"
    if key == "concept":
        return "light_academic"
    if key == "content":
        return "light_academic"
    if slide_theme_name == "title":
        return "dark_hero"
    return None


def _coerce_optional_color(value: Any, default: RGBColor | None) -> RGBColor | None:
    if value is None:
        return default
    if default is None:
        return None if value is None else resolve_color(value, RGBColor(255, 255, 255))
    return resolve_color(value, default)


# Legacy keys still accepted, but they now resolve against a SlideTheme instead of a parallel style system.
_LEGACY_TO_THEME_FIELD: dict[str, str] = {
    "panel_fill_color": "panel_fill_color",
    "panel_line_color": "panel_line_color",
    "panel_label_color": "panel_label_color",
    "panel_note_color": "panel_note_color",
    "connector_color": "connector_color",
}


def resolve_title_style(spec: Mapping[str, Any], *, slide_theme_name: str | None) -> TitleCompositeStyle:
    style_overrides = dict(spec.get("title_style", {}) or {})
    explicit_theme = style_overrides.pop("theme", None)
    preset = style_overrides.get("preset") or spec.get("style_variant")

    base_theme_name = explicit_theme or _legacy_style_preset_to_theme(preset, slide_theme_name)
    theme_obj = get_theme(theme=base_theme_name, slide_theme_name=slide_theme_name)

    # Allow title-style overrides to flow through the theme system when they match theme fields.
    theme_override_candidates = {
        key: value
        for key, value in style_overrides.items()
        if key in {
            "title_color",
            "subtitle_color",
            "body_color",
            "muted_color",
            "footer_color",
            "footer_dark",
            "accent_color",
            "divider_color",
            "connector_color",
            "connector_width_pt",
            "box_fill_color",
            "box_line_color",
            "box_title_color",
            "box_body_color",
            "panel_fill_color",
            "panel_line_color",
            "panel_label_color",
            "panel_note_color",
            "panel_visual_variant",
            "pill_fill_color",
            "pill_line_color",
            "pill_text_color",
            "callout_color",
            "ghost_text_color",
        }
    }
    if theme_override_candidates:
        theme_obj = get_theme(theme_obj, overrides=theme_override_candidates)

    title_color = resolve_color(style_overrides.get("title_color"), theme_obj.title_color)
    subtitle_color = resolve_color(style_overrides.get("subtitle_color"), theme_obj.subtitle_color)
    author_color = resolve_color(style_overrides.get("author_color"), theme_obj.muted_color)
    bullets_color = resolve_color(style_overrides.get("bullets_color"), theme_obj.subtitle_color)
    tiny_footer_color = resolve_color(style_overrides.get("tiny_footer_color"), theme_obj.muted_color)

    panel_fill_color = _coerce_optional_color(style_overrides.get("panel_fill_color"), theme_obj.panel_fill_color)
    panel_line_color = resolve_color(style_overrides.get("panel_line_color"), theme_obj.panel_line_color)
    panel_label_color = resolve_color(style_overrides.get("panel_label_color"), theme_obj.panel_label_color)
    panel_note_color = resolve_color(style_overrides.get("panel_note_color"), theme_obj.panel_note_color)
    panel_visual_variant = str(style_overrides.get("panel_visual_variant", theme_obj.panel_visual_variant))

    connector_color = resolve_color(style_overrides.get("connector_color"), theme_obj.connector_color)
    connector_width_pt = float(style_overrides.get("connector_width_pt", theme_obj.connector_width_pt))
    footer_dark = bool(style_overrides.get("footer_dark", theme_obj.footer_dark))

    return TitleCompositeStyle(
        theme=theme_obj,
        title_color=title_color,
        subtitle_color=subtitle_color,
        author_color=author_color,
        bullets_color=bullets_color,
        tiny_footer_color=tiny_footer_color,
        panel_fill_color=panel_fill_color,
        panel_line_color=panel_line_color,
        panel_label_color=panel_label_color,
        panel_note_color=panel_note_color,
        panel_visual_variant=panel_visual_variant,
        connector_color=connector_color,
        connector_width_pt=connector_width_pt,
        footer_dark=footer_dark,
    )

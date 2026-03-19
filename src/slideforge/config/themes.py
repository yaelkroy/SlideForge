from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any, Mapping

from pptx.dml.color import RGBColor

from slideforge.config.constants import (
    ACCENT,
    BOX_LINE,
    DARK_BOX_FILL,
    GHOST_TEXT,
    LIGHT_BOX_FILL,
    MUTED,
    NAVY,
    OFFWHITE,
    SLATE,
    TITLE_PANEL_FILL,
    TITLE_PANEL_LINE,
    WHITE,
)

ColorLike = RGBColor | str | tuple[int, int, int] | list[int]


COLOR_NAME_MAP: dict[str, RGBColor] = {
    "ACCENT": ACCENT,
    "BOX_LINE": BOX_LINE,
    "DARK_BOX_FILL": DARK_BOX_FILL,
    "GHOST_TEXT": GHOST_TEXT,
    "LIGHT_BOX_FILL": LIGHT_BOX_FILL,
    "MUTED": MUTED,
    "NAVY": NAVY,
    "OFFWHITE": OFFWHITE,
    "SLATE": SLATE,
    "TITLE_PANEL_FILL": TITLE_PANEL_FILL,
    "TITLE_PANEL_LINE": TITLE_PANEL_LINE,
    "WHITE": WHITE,
}


def hex_to_rgb(value: str) -> RGBColor:
    cleaned = value.strip().lstrip("#")
    if len(cleaned) != 6:
        raise ValueError(f"Expected 6-digit hex color, got: {value!r}")
    return RGBColor(
        int(cleaned[0:2], 16),
        int(cleaned[2:4], 16),
        int(cleaned[4:6], 16),
    )


def resolve_color(value: Any, default: RGBColor) -> RGBColor:
    if value is None:
        return default

    if isinstance(value, RGBColor):
        return value

    if isinstance(value, str):
        named = COLOR_NAME_MAP.get(value.strip().upper())
        if named is not None:
            return named
        return hex_to_rgb(value)

    if isinstance(value, (tuple, list)) and len(value) == 3:
        r, g, b = value
        return RGBColor(int(r), int(g), int(b))

    return default


@dataclass(frozen=True)
class SlideTheme:
    name: str

    # Header / text
    title_color: RGBColor
    subtitle_color: RGBColor
    body_color: RGBColor
    muted_color: RGBColor
    footer_color: RGBColor
    footer_dark: bool

    # Accent / rules / connectors
    accent_color: RGBColor
    divider_color: RGBColor
    connector_color: RGBColor
    connector_width_pt: float

    # Generic boxes / cards
    box_fill_color: RGBColor | None
    box_line_color: RGBColor
    box_title_color: RGBColor
    box_body_color: RGBColor

    # Title-composite / hero panels
    panel_fill_color: RGBColor | None
    panel_line_color: RGBColor
    panel_label_color: RGBColor
    panel_note_color: RGBColor
    panel_visual_variant: str

    # Other UI-like pieces
    pill_fill_color: RGBColor
    pill_line_color: RGBColor
    pill_text_color: RGBColor
    callout_color: RGBColor
    ghost_text_color: RGBColor

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def derive(self, **overrides: Any) -> "SlideTheme":
        color_fields = {
            "title_color": self.title_color,
            "subtitle_color": self.subtitle_color,
            "body_color": self.body_color,
            "muted_color": self.muted_color,
            "footer_color": self.footer_color,
            "accent_color": self.accent_color,
            "divider_color": self.divider_color,
            "connector_color": self.connector_color,
            "box_line_color": self.box_line_color,
            "box_title_color": self.box_title_color,
            "box_body_color": self.box_body_color,
            "panel_line_color": self.panel_line_color,
            "panel_label_color": self.panel_label_color,
            "panel_note_color": self.panel_note_color,
            "pill_fill_color": self.pill_fill_color,
            "pill_line_color": self.pill_line_color,
            "pill_text_color": self.pill_text_color,
            "callout_color": self.callout_color,
            "ghost_text_color": self.ghost_text_color,
        }

        nullable_color_fields = {
            "box_fill_color": self.box_fill_color,
            "panel_fill_color": self.panel_fill_color,
        }

        normalized: dict[str, Any] = {}

        for key, default in color_fields.items():
            if key in overrides:
                normalized[key] = resolve_color(overrides[key], default)

        for key, default in nullable_color_fields.items():
            if key in overrides:
                if overrides[key] is None:
                    normalized[key] = None
                else:
                    fallback = default if default is not None else OFFWHITE
                    normalized[key] = resolve_color(overrides[key], fallback)

        for key in ("connector_width_pt",):
            if key in overrides:
                normalized[key] = float(overrides[key])

        for key in ("footer_dark",):
            if key in overrides:
                normalized[key] = bool(overrides[key])

        for key in ("name", "panel_visual_variant"):
            if key in overrides:
                normalized[key] = str(overrides[key])

        return replace(self, **normalized)


LIGHT_ACADEMIC_THEME = SlideTheme(
    name="light_academic",
    title_color=NAVY,
    subtitle_color=SLATE,
    body_color=NAVY,
    muted_color=MUTED,
    footer_color=MUTED,
    footer_dark=False,
    accent_color=ACCENT,
    divider_color=ACCENT,
    connector_color=ACCENT,
    connector_width_pt=1.6,
    box_fill_color=LIGHT_BOX_FILL,
    box_line_color=BOX_LINE,
    box_title_color=SLATE,
    box_body_color=NAVY,
    panel_fill_color=LIGHT_BOX_FILL,
    panel_line_color=BOX_LINE,
    panel_label_color=NAVY,
    panel_note_color=NAVY,
    panel_visual_variant="dark_on_light",
    pill_fill_color=TITLE_PANEL_FILL,
    pill_line_color=TITLE_PANEL_LINE,
    pill_text_color=OFFWHITE,
    callout_color=SLATE,
    ghost_text_color=GHOST_TEXT,
)

DARK_HERO_THEME = SlideTheme(
    name="dark_hero",
    title_color=OFFWHITE,
    subtitle_color=GHOST_TEXT,
    body_color=OFFWHITE,
    muted_color=TITLE_PANEL_LINE,
    footer_color=OFFWHITE,
    footer_dark=True,
    accent_color=TITLE_PANEL_LINE,
    divider_color=TITLE_PANEL_LINE,
    connector_color=TITLE_PANEL_LINE,
    connector_width_pt=1.6,
    box_fill_color=DARK_BOX_FILL,
    box_line_color=TITLE_PANEL_LINE,
    box_title_color=OFFWHITE,
    box_body_color=OFFWHITE,
    panel_fill_color=TITLE_PANEL_FILL,
    panel_line_color=TITLE_PANEL_LINE,
    panel_label_color=OFFWHITE,
    panel_note_color=OFFWHITE,
    panel_visual_variant="light_on_dark",
    pill_fill_color=TITLE_PANEL_FILL,
    pill_line_color=TITLE_PANEL_LINE,
    pill_text_color=OFFWHITE,
    callout_color=TITLE_PANEL_LINE,
    ghost_text_color=GHOST_TEXT,
)

DARK_SECTION_THEME = SlideTheme(
    name="dark_section",
    title_color=OFFWHITE,
    subtitle_color=TITLE_PANEL_LINE,
    body_color=OFFWHITE,
    muted_color=TITLE_PANEL_LINE,
    footer_color=OFFWHITE,
    footer_dark=True,
    accent_color=TITLE_PANEL_LINE,
    divider_color=TITLE_PANEL_LINE,
    connector_color=TITLE_PANEL_LINE,
    connector_width_pt=1.45,
    box_fill_color=TITLE_PANEL_FILL,
    box_line_color=TITLE_PANEL_LINE,
    box_title_color=OFFWHITE,
    box_body_color=OFFWHITE,
    panel_fill_color=TITLE_PANEL_FILL,
    panel_line_color=TITLE_PANEL_LINE,
    panel_label_color=OFFWHITE,
    panel_note_color=OFFWHITE,
    panel_visual_variant="light_on_dark",
    pill_fill_color=TITLE_PANEL_FILL,
    pill_line_color=TITLE_PANEL_LINE,
    pill_text_color=OFFWHITE,
    callout_color=TITLE_PANEL_LINE,
    ghost_text_color=GHOST_TEXT,
)


THEME_PRESETS: dict[str, SlideTheme] = {
    "light_academic": LIGHT_ACADEMIC_THEME,
    "dark_hero": DARK_HERO_THEME,
    "dark_section": DARK_SECTION_THEME,
}


DEFAULT_THEME_BY_SLIDE_THEME_NAME: dict[str, str] = {
    "title": "dark_hero",
    "section": "dark_section",
    "concept": "light_academic",
    "content": "light_academic",
}


def theme_name_for_slide_theme(slide_theme_name: str | None) -> str:
    if not slide_theme_name:
        return "light_academic"
    return DEFAULT_THEME_BY_SLIDE_THEME_NAME.get(slide_theme_name, "light_academic")


def get_theme(
    theme: str | SlideTheme | None = None,
    *,
    slide_theme_name: str | None = None,
    overrides: Mapping[str, Any] | None = None,
) -> SlideTheme:
    if isinstance(theme, SlideTheme):
        base = theme
    else:
        theme_name = theme or theme_name_for_slide_theme(slide_theme_name)
        base = THEME_PRESETS.get(theme_name, LIGHT_ACADEMIC_THEME)

    if not overrides:
        return base

    return base.derive(**dict(overrides))


def get_theme_dict(
    theme: str | SlideTheme | None = None,
    *,
    slide_theme_name: str | None = None,
    overrides: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return get_theme(
        theme,
        slide_theme_name=slide_theme_name,
        overrides=overrides,
    ).to_dict()
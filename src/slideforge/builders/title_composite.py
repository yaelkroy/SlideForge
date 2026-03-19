from __future__ import annotations

from typing import Any, Mapping

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import (
    ACCENT,
    BODY_FONT,
    BOX_LINE,
    DARK_BOX_FILL,
    FORMULA_FONT,
    GHOST_TEXT,
    LIGHT_BOX_FILL,
    MUTED,
    NAVY,
    OFFWHITE,
    SLATE,
    TITLE_FONT,
    TITLE_PANEL_FILL,
    TITLE_PANEL_LINE,
    WHITE,
)
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, distribute_columns, fit_text
from slideforge.render.primitives import (
    add_footer,
    add_rounded_box,
    add_soft_connector,
    add_textbox,
)


COLOR_NAME_MAP: dict[str, RGBColor] = {
    "ACCENT": ACCENT,
    "BODY": SLATE,
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


STYLE_PRESETS: dict[str, dict[str, Any]] = {
    "light_academic": {
        "title_color": NAVY,
        "subtitle_color": SLATE,
        "author_color": SLATE,
        "bullets_color": SLATE,
        "tiny_footer_color": SLATE,
        "panel_fill_color": LIGHT_BOX_FILL,
        "panel_line_color": BOX_LINE,
        "panel_label_color": NAVY,
        "panel_note_color": NAVY,
        "panel_visual_variant": "dark_on_light",
        "connector_color": ACCENT,
        "connector_width_pt": 1.6,
        "footer_dark": False,
    },
    "dark_hero": {
        "title_color": OFFWHITE,
        "subtitle_color": GHOST_TEXT,
        "author_color": TITLE_PANEL_LINE,
        "bullets_color": GHOST_TEXT,
        "tiny_footer_color": TITLE_PANEL_LINE,
        "panel_fill_color": TITLE_PANEL_FILL,
        "panel_line_color": TITLE_PANEL_LINE,
        "panel_label_color": OFFWHITE,
        "panel_note_color": OFFWHITE,
        "panel_visual_variant": "light_on_dark",
        "connector_color": TITLE_PANEL_LINE,
        "connector_width_pt": 1.6,
        "footer_dark": True,
    },
}


def _fit_text_size(
    text: str,
    box: Box,
    *,
    min_font: int,
    max_font: int,
    max_lines: int,
) -> int:
    if not text.strip() or box.w <= 0 or box.h <= 0:
        return max_font
    fitted = fit_text(
        text,
        box.w,
        box.h,
        min_font_size=min_font,
        max_font_size=max_font,
        max_lines=max_lines,
    )
    return max(min_font, fitted.font_size)


def _join_items(items: list[str]) -> str:
    return "   •   ".join(item.strip() for item in items if item and item.strip())


def _panel_box_from_spec(panel: Mapping[str, Any], fallback: Box) -> Box:
    return Box(
        panel.get("x", fallback.x),
        panel.get("y", fallback.y),
        panel.get("w", fallback.w),
        panel.get("h", fallback.h),
    )


def _hex_to_rgb(value: str) -> RGBColor:
    cleaned = value.strip().lstrip("#")
    if len(cleaned) != 6:
        raise ValueError(f"Expected 6-digit hex color, got: {value!r}")
    return RGBColor(
        int(cleaned[0:2], 16),
        int(cleaned[2:4], 16),
        int(cleaned[4:6], 16),
    )


def _coerce_color(value: Any, default: RGBColor) -> RGBColor:
    if value is None:
        return default
    if isinstance(value, RGBColor):
        return value
    if isinstance(value, str):
        named = COLOR_NAME_MAP.get(value.strip().upper())
        if named is not None:
            return named
        return _hex_to_rgb(value)
    if isinstance(value, (tuple, list)) and len(value) == 3:
        r, g, b = value
        return RGBColor(int(r), int(g), int(b))
    return default


def _resolve_style(spec: Mapping[str, Any], theme: str) -> dict[str, Any]:
    style_overrides = dict(spec.get("title_style", {}))
    preset_name = (
        style_overrides.pop("preset", None)
        or spec.get("style_variant")
        or ("dark_hero" if theme == "title" else "light_academic")
    )
    base = dict(STYLE_PRESETS.get(preset_name, STYLE_PRESETS["light_academic"]))
    base.update(style_overrides)

    return {
        "title_color": _coerce_color(base.get("title_color"), NAVY),
        "subtitle_color": _coerce_color(base.get("subtitle_color"), SLATE),
        "author_color": _coerce_color(base.get("author_color"), SLATE),
        "bullets_color": _coerce_color(base.get("bullets_color"), SLATE),
        "tiny_footer_color": _coerce_color(base.get("tiny_footer_color"), SLATE),
        "panel_fill_color": _coerce_color(base.get("panel_fill_color"), LIGHT_BOX_FILL),
        "panel_line_color": _coerce_color(base.get("panel_line_color"), BOX_LINE),
        "panel_label_color": _coerce_color(base.get("panel_label_color"), NAVY),
        "panel_note_color": _coerce_color(base.get("panel_note_color"), NAVY),
        "panel_visual_variant": str(base.get("panel_visual_variant", "dark_on_light")),
        "connector_color": _coerce_color(base.get("connector_color"), ACCENT),
        "connector_width_pt": float(base.get("connector_width_pt", 1.6)),
        "footer_dark": bool(base.get("footer_dark", False)),
    }


def _add_visual_panel(
    slide,
    *,
    panel_box: Box,
    panel: Mapping[str, Any],
    idx: int,
    style: Mapping[str, Any],
) -> None:
    label = str(panel.get("label", "")).strip()
    embedded_label = str(panel.get("embedded_label", "")).strip()
    mini_visual = str(panel.get("mini_visual", "")).strip()
    panel_style = dict(panel.get("style", {}))

    fill_color = _coerce_color(panel_style.get("fill_color"), style["panel_fill_color"])
    line_color = _coerce_color(panel_style.get("line_color"), style["panel_line_color"])
    label_color = _coerce_color(panel_style.get("label_color"), style["panel_label_color"])
    note_color = _coerce_color(panel_style.get("embedded_label_color"), style["panel_note_color"])
    visual_variant = str(panel_style.get("visual_variant", style["panel_visual_variant"]))

    add_rounded_box(
        slide,
        panel_box.x,
        panel_box.y,
        panel_box.w,
        panel_box.h,
        line_color=line_color,
        fill_color=fill_color,
    )

    top_pad = float(panel.get("top_pad", 0.10))
    label_h = float(panel.get("label_h", 0.18 if label else 0.0))
    bottom_note_h = float(panel.get("bottom_note_h", 0.18 if embedded_label else 0.0))
    inter_gap = float(panel.get("inter_gap", 0.06))

    visual_y = panel_box.y + top_pad + (label_h + inter_gap if label else 0.0)
    visual_h = float(
        panel.get(
            "visual_h",
            panel_box.h - top_pad - bottom_note_h - 0.12 - (label_h + inter_gap if label else 0.0),
        )
    )
    visual_h = max(0.70, min(visual_h, panel_box.h - 0.30))
    visual_pad_x = float(panel.get("visual_pad_x", 0.12))
    visual_x = panel_box.x + visual_pad_x
    visual_w = panel_box.w - 2 * visual_pad_x

    if label:
        label_box = Box(
            panel_box.x + 0.08,
            panel_box.y + 0.06,
            panel_box.w - 0.16,
            max(0.16, label_h),
        )
        label_font = _fit_text_size(label, label_box, min_font=11, max_font=13, max_lines=1)
        add_textbox(
            slide,
            x=label_box.x,
            y=label_box.y,
            w=label_box.w,
            h=label_box.h,
            text=label,
            font_name=BODY_FONT,
            font_size=label_font,
            color=label_color,
            bold=True,
            align=PP_ALIGN.CENTER,
        )

    if mini_visual:
        add_mini_visual(
            slide,
            kind=mini_visual,
            x=visual_x,
            y=visual_y,
            w=visual_w,
            h=visual_h,
            suffix=f"_title_composite_{idx}",
            variant=visual_variant,
        )

    if embedded_label:
        note_box = Box(panel_box.x + 0.08, panel_box.bottom - 0.24, panel_box.w - 0.16, 0.18)
        note_font = _fit_text_size(embedded_label, note_box, min_font=10, max_font=12, max_lines=1)
        add_textbox(
            slide,
            x=note_box.x,
            y=note_box.y,
            w=note_box.w,
            h=note_box.h,
            text=embedded_label,
            font_name=FORMULA_FONT,
            font_size=note_font,
            color=note_color,
            bold=False,
            align=PP_ALIGN.CENTER,
        )


def build_title_composite_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    theme = spec.get("theme", "title")
    bg = spec.get("background") or choose_background(theme, counters)
    slide = new_slide(prs, bg)

    layout = spec.get("layout", {})
    style = _resolve_style(spec, theme=theme)

    title = spec.get("title") or spec["slide_title"]
    subtitle = str(spec.get("subtitle", "")).strip()
    author_line = str(spec.get("author_line", "")).strip()
    tiny_footer = str(spec.get("tiny_footer", "")).strip()
    bullets = spec.get("bullets", [])

    title_box = Box(0.78, layout.get("title_y", 0.90), 11.75, layout.get("title_h", 0.96))
    title_font = _fit_text_size(
        title,
        title_box,
        min_font=int(layout.get("title_min_font", 24)),
        max_font=int(layout.get("title_max_font", 32)),
        max_lines=int(layout.get("title_max_lines", 3)),
    )
    add_textbox(
        slide,
        x=title_box.x,
        y=title_box.y,
        w=title_box.w,
        h=title_box.h,
        text=title,
        font_name=TITLE_FONT,
        font_size=title_font,
        color=style["title_color"],
        bold=True,
        align=PP_ALIGN.CENTER,
    )

    if subtitle:
        subtitle_box = Box(
            1.10,
            layout.get("subtitle_y", 2.02),
            10.90,
            layout.get("subtitle_h", 0.42),
        )
        subtitle_font = _fit_text_size(
            subtitle,
            subtitle_box,
            min_font=int(layout.get("subtitle_min_font", 15)),
            max_font=int(layout.get("subtitle_max_font", 18)),
            max_lines=int(layout.get("subtitle_max_lines", 2)),
        )
        add_textbox(
            slide,
            x=subtitle_box.x,
            y=subtitle_box.y,
            w=subtitle_box.w,
            h=subtitle_box.h,
            text=subtitle,
            font_name=BODY_FONT,
            font_size=subtitle_font,
            color=style["subtitle_color"],
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    if spec.get("show_author_line", True) and author_line:
        author_box = Box(
            2.80,
            layout.get("author_y", 2.70),
            7.80,
            layout.get("author_h", 0.24),
        )
        author_font = _fit_text_size(
            author_line,
            author_box,
            min_font=int(layout.get("author_min_font", 11)),
            max_font=int(layout.get("author_max_font", 13)),
            max_lines=1,
        )
        add_textbox(
            slide,
            x=author_box.x,
            y=author_box.y,
            w=author_box.w,
            h=author_box.h,
            text=author_line,
            font_name=BODY_FONT,
            font_size=author_font,
            color=style["author_color"],
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    visual_region_dict = layout.get(
        "visual_region",
        {"x": 0.82, "y": 3.02, "w": 11.55, "h": 2.48},
    )
    visual_region = Box(
        visual_region_dict["x"],
        visual_region_dict["y"],
        visual_region_dict["w"],
        visual_region_dict["h"],
    )

    composite_visual = spec.get("composite_visual", {})
    panels = composite_visual.get("panels", [])

    if panels:
        fallback_boxes = distribute_columns(
            visual_region,
            len(panels),
            gap=float(layout.get("panel_gap", 0.25)),
        )
        actual_boxes: list[Box] = []

        for idx, (panel, fallback) in enumerate(zip(panels, fallback_boxes)):
            panel_box = _panel_box_from_spec(panel, fallback)
            actual_boxes.append(panel_box)
            _add_visual_panel(
                slide,
                panel_box=panel_box,
                panel=panel,
                idx=idx,
                style=style,
            )

        for conn in composite_visual.get("connectors", []):
            from_idx = conn.get("from")
            to_idx = conn.get("to")
            if (
                isinstance(from_idx, int)
                and isinstance(to_idx, int)
                and 0 <= from_idx < len(actual_boxes)
                and 0 <= to_idx < len(actual_boxes)
            ):
                a = actual_boxes[from_idx]
                b = actual_boxes[to_idx]
                connector_color = _coerce_color(
                    conn.get("color"),
                    style["connector_color"],
                )
                connector_width = float(conn.get("width_pt", style["connector_width_pt"]))
                add_soft_connector(
                    slide,
                    x1=a.right,
                    y1=a.y + a.h / 2,
                    x2=b.x,
                    y2=b.y + b.h / 2,
                    color=connector_color,
                    width_pt=connector_width,
                )

    if bullets:
        bullets_region_dict = layout.get(
            "bullets_region",
            {"x": 2.65, "y": 5.60, "w": 8.10, "h": 0.34},
        )
        bullets_box = Box(
            bullets_region_dict["x"],
            bullets_region_dict["y"],
            bullets_region_dict["w"],
            bullets_region_dict["h"],
        )
        bullets_text = _join_items(bullets)
        bullets_font = _fit_text_size(
            bullets_text,
            bullets_box,
            min_font=int(layout.get("bullets_min_font", 12)),
            max_font=int(layout.get("bullets_max_font", 14)),
            max_lines=int(layout.get("bullets_max_lines", 2)),
        )
        add_textbox(
            slide,
            x=bullets_box.x,
            y=bullets_box.y,
            w=bullets_box.w,
            h=bullets_box.h,
            text=bullets_text,
            font_name=BODY_FONT,
            font_size=bullets_font,
            color=style["bullets_color"],
            bold=True,
            align=PP_ALIGN.CENTER,
        )

    if tiny_footer:
        tiny_footer_region_dict = layout.get(
            "tiny_footer_region",
            {"x": 2.00, "y": 6.36, "w": 9.35, "h": 0.22},
        )
        tiny_footer_box = Box(
            tiny_footer_region_dict["x"],
            tiny_footer_region_dict["y"],
            tiny_footer_region_dict["w"],
            tiny_footer_region_dict["h"],
        )
        tiny_footer_font = _fit_text_size(
            tiny_footer,
            tiny_footer_box,
            min_font=int(layout.get("tiny_footer_min_font", 10)),
            max_font=int(layout.get("tiny_footer_max_font", 12)),
            max_lines=1,
        )
        add_textbox(
            slide,
            x=tiny_footer_box.x,
            y=tiny_footer_box.y,
            w=tiny_footer_box.w,
            h=tiny_footer_box.h,
            text=tiny_footer,
            font_name=BODY_FONT,
            font_size=tiny_footer_font,
            color=style["tiny_footer_color"],
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    if spec.get("show_footer_author", True):
        add_footer(slide, dark=style["footer_dark"])
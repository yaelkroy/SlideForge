from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import ACCENT, BODY_FONT, FORMULA_FONT, NAVY, SLATE, TITLE_FONT
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, distribute_columns, fit_text
from slideforge.render.primitives import (
    add_footer,
    add_rounded_box,
    add_soft_connector,
    add_textbox,
)


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


def _panel_box_from_spec(panel: dict[str, Any], fallback: Box) -> Box:
    return Box(
        panel.get("x", fallback.x),
        panel.get("y", fallback.y),
        panel.get("w", fallback.w),
        panel.get("h", fallback.h),
    )


def _add_visual_panel(
    slide,
    *,
    panel_box: Box,
    panel: dict[str, Any],
    idx: int,
) -> None:
    label = panel.get("label", "").strip()
    embedded_label = panel.get("embedded_label", "").strip()
    mini_visual = panel.get("mini_visual", "").strip()

    # Subtle backing card helps the hero banner read as one academic composition.
    add_rounded_box(slide, panel_box.x, panel_box.y, panel_box.w, panel_box.h)

    top_pad = 0.10
    label_h = 0.18 if label else 0.0
    bottom_note_h = 0.18 if embedded_label else 0.0
    inter_gap = 0.06

    visual_y = panel_box.y + top_pad + (label_h + inter_gap if label else 0.0)
    visual_h = panel.get(
        "visual_h",
        panel_box.h - top_pad - bottom_note_h - 0.12 - (label_h + inter_gap if label else 0.0),
    )
    visual_h = max(0.70, min(visual_h, panel_box.h - 0.30))
    visual_x = panel_box.x + 0.12
    visual_w = panel_box.w - 0.24

    if label:
        label_box = Box(panel_box.x + 0.08, panel_box.y + 0.06, panel_box.w - 0.16, label_h)
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
            color=NAVY,
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
            variant="dark_on_light",
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
            color=NAVY,
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
    title = spec.get("title") or spec["slide_title"]
    subtitle = spec.get("subtitle", "").strip()
    author_line = spec.get("author_line", "").strip()
    tiny_footer = spec.get("tiny_footer", "").strip()
    bullets = spec.get("bullets", [])

    title_box = Box(0.78, layout.get("title_y", 0.90), 11.75, 0.96)
    title_font = _fit_text_size(title, title_box, min_font=24, max_font=32, max_lines=3)
    add_textbox(
        slide,
        x=title_box.x,
        y=title_box.y,
        w=title_box.w,
        h=title_box.h,
        text=title,
        font_name=TITLE_FONT,
        font_size=title_font,
        color=NAVY,
        bold=True,
        align=PP_ALIGN.CENTER,
    )

    if subtitle:
        subtitle_box = Box(1.10, layout.get("subtitle_y", 2.02), 10.90, 0.42)
        subtitle_font = _fit_text_size(subtitle, subtitle_box, min_font=15, max_font=18, max_lines=2)
        add_textbox(
            slide,
            x=subtitle_box.x,
            y=subtitle_box.y,
            w=subtitle_box.w,
            h=subtitle_box.h,
            text=subtitle,
            font_name=BODY_FONT,
            font_size=subtitle_font,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    if spec.get("show_author_line", True) and author_line:
        author_box = Box(2.80, layout.get("author_y", 2.70), 7.80, 0.24)
        author_font = _fit_text_size(author_line, author_box, min_font=11, max_font=13, max_lines=1)
        add_textbox(
            slide,
            x=author_box.x,
            y=author_box.y,
            w=author_box.w,
            h=author_box.h,
            text=author_line,
            font_name=BODY_FONT,
            font_size=author_font,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    visual_region_dict = layout.get("visual_region", {"x": 0.82, "y": 3.02, "w": 11.55, "h": 2.48})
    visual_region = Box(
        visual_region_dict["x"],
        visual_region_dict["y"],
        visual_region_dict["w"],
        visual_region_dict["h"],
    )

    composite_visual = spec.get("composite_visual", {})
    panels = composite_visual.get("panels", [])

    if panels:
        fallback_boxes = distribute_columns(visual_region, len(panels), gap=0.25)
        actual_boxes: list[Box] = []

        for idx, (panel, fallback) in enumerate(zip(panels, fallback_boxes)):
            panel_box = _panel_box_from_spec(panel, fallback)
            actual_boxes.append(panel_box)
            _add_visual_panel(slide, panel_box=panel_box, panel=panel, idx=idx)

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
                add_soft_connector(
                    slide,
                    x1=a.right,
                    y1=a.y + a.h / 2,
                    x2=b.x,
                    y2=b.y + b.h / 2,
                    color=ACCENT,
                    width_pt=1.6,
                )

    if bullets:
        bullets_region_dict = layout.get("bullets_region", {"x": 2.65, "y": 5.60, "w": 8.10, "h": 0.34})
        bullets_box = Box(
            bullets_region_dict["x"],
            bullets_region_dict["y"],
            bullets_region_dict["w"],
            bullets_region_dict["h"],
        )
        bullets_text = _join_items(bullets)
        bullets_font = _fit_text_size(bullets_text, bullets_box, min_font=12, max_font=14, max_lines=2)
        add_textbox(
            slide,
            x=bullets_box.x,
            y=bullets_box.y,
            w=bullets_box.w,
            h=bullets_box.h,
            text=bullets_text,
            font_name=BODY_FONT,
            font_size=bullets_font,
            color=SLATE,
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
        tiny_footer_font = _fit_text_size(tiny_footer, tiny_footer_box, min_font=10, max_font=12, max_lines=1)
        add_textbox(
            slide,
            x=tiny_footer_box.x,
            y=tiny_footer_box.y,
            w=tiny_footer_box.w,
            h=tiny_footer_box.h,
            text=tiny_footer,
            font_name=BODY_FONT,
            font_size=tiny_footer_font,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    if spec.get("show_footer_author", True):
        add_footer(slide, dark=False)
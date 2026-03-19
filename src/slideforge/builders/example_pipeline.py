from __future__ import annotations

from typing import Any, Mapping

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, OFFWHITE, TITLE_FONT
from slideforge.config.themes import SlideTheme, get_theme, resolve_color
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, centered_visual_in_card, distribute_columns, fit_text
from slideforge.render.header import render_header_from_spec
from slideforge.render.primitives import (
    add_footer,
    add_rounded_box,
    add_soft_connector,
    add_textbox,
)


def _join_items(items: list[str]) -> str:
    cleaned = [item.strip() for item in items if item and item.strip()]
    return "   •   ".join(cleaned)


def _fit_stage_text(
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


def _box_from_dict(raw: Mapping[str, Any], fallback: Box) -> Box:
    return Box(
        raw.get("x", fallback.x),
        raw.get("y", fallback.y),
        raw.get("w", fallback.w),
        raw.get("h", fallback.h),
    )


def _resolve_pipeline_style(
    spec: Mapping[str, Any],
    *,
    theme_obj: SlideTheme,
) -> dict[str, Any]:
    pipeline_style = dict(spec.get("pipeline_style", {}) or {})

    card_fill_default = theme_obj.box_fill_color
    if card_fill_default is None:
        card_fill_default = theme_obj.panel_fill_color
    if card_fill_default is None:
        card_fill_default = OFFWHITE

    return {
        "card_fill_color": resolve_color(pipeline_style.get("card_fill_color"), card_fill_default),
        "card_line_color": resolve_color(pipeline_style.get("card_line_color"), theme_obj.box_line_color),
        "card_title_color": resolve_color(pipeline_style.get("card_title_color"), theme_obj.box_title_color),
        "card_caption_color": resolve_color(pipeline_style.get("card_caption_color"), theme_obj.subtitle_color),
        "card_formula_color": resolve_color(pipeline_style.get("card_formula_color"), theme_obj.body_color),
        "card_visual_variant": str(pipeline_style.get("card_visual_variant", theme_obj.panel_visual_variant)),
        "card_line_width_pt": float(pipeline_style.get("card_line_width_pt", 1.25)),
        "connector_color": resolve_color(pipeline_style.get("connector_color"), theme_obj.connector_color),
        "connector_width_pt": float(pipeline_style.get("connector_width_pt", theme_obj.connector_width_pt)),
        "bullets_color": resolve_color(pipeline_style.get("bullets_color"), theme_obj.subtitle_color),
        "takeaway_color": resolve_color(pipeline_style.get("takeaway_color"), theme_obj.subtitle_color),
        "footer_color": resolve_color(pipeline_style.get("footer_color"), theme_obj.footer_color),
        "footer_dark": bool(pipeline_style.get("footer_dark", theme_obj.footer_dark)),
        "title_align": pipeline_style.get("card_title_align", PP_ALIGN.CENTER),
        "caption_align": pipeline_style.get("card_caption_align", PP_ALIGN.CENTER),
        "formula_align": pipeline_style.get("card_formula_align", PP_ALIGN.CENTER),
    }


def _resolve_stage_style(
    stage: Mapping[str, Any],
    *,
    pipeline_style: Mapping[str, Any],
) -> dict[str, Any]:
    stage_style = dict(stage.get("style", {}) or {})
    return {
        "fill_color": resolve_color(stage_style.get("fill_color"), pipeline_style["card_fill_color"]),
        "line_color": resolve_color(stage_style.get("line_color"), pipeline_style["card_line_color"]),
        "title_color": resolve_color(stage_style.get("title_color"), pipeline_style["card_title_color"]),
        "caption_color": resolve_color(stage_style.get("caption_color"), pipeline_style["card_caption_color"]),
        "formula_color": resolve_color(stage_style.get("formula_color"), pipeline_style["card_formula_color"]),
        "visual_variant": str(stage_style.get("visual_variant", pipeline_style["card_visual_variant"])),
        "line_width_pt": float(stage_style.get("line_width_pt", pipeline_style["card_line_width_pt"])),
    }


def _add_stage_card(
    slide,
    stage: dict[str, Any],
    card_box: Box,
    idx: int,
    *,
    pipeline_style: Mapping[str, Any],
    layout: Mapping[str, Any],
) -> None:
    stage_style = _resolve_stage_style(stage, pipeline_style=pipeline_style)

    add_rounded_box(
        slide,
        card_box.x,
        card_box.y,
        card_box.w,
        card_box.h,
        line_color=stage_style["line_color"],
        fill_color=stage_style["fill_color"],
        line_width_pt=stage_style["line_width_pt"],
    )

    title_text = str(stage.get("title", "")).strip()
    caption_text = str(stage.get("caption", "")).strip()
    formula_text = str(stage.get("formula", "")).strip()

    title_h = float(stage.get("title_h", layout.get("stage_title_h", 0.24)))
    caption_h = float(stage.get("caption_h", layout.get("stage_caption_h", 0.24 if caption_text else 0.0)))
    formula_h = float(stage.get("formula_h", layout.get("stage_formula_h", 0.18 if formula_text else 0.0)))

    title_box = Box(card_box.x + 0.10, card_box.y + 0.10, card_box.w - 0.20, title_h)
    title_font = _fit_stage_text(
        title_text,
        title_box,
        min_font=int(stage.get("title_min_font", layout.get("stage_title_min_font", 12))),
        max_font=int(stage.get("title_max_font", layout.get("stage_title_max_font", 15))),
        max_lines=int(stage.get("title_max_lines", layout.get("stage_title_max_lines", 2))),
    )
    add_textbox(
        slide,
        x=title_box.x,
        y=title_box.y,
        w=title_box.w,
        h=title_box.h,
        text=title_text,
        font_name=TITLE_FONT,
        font_size=title_font,
        color=stage_style["title_color"],
        bold=True,
        align=pipeline_style["title_align"],
    )

    visual_box = centered_visual_in_card(
        card_box,
        title_h=title_h,
        caption_h=caption_h,
        formula_h=formula_h,
        top_pad=float(stage.get("top_pad", layout.get("stage_top_pad", 0.10))),
        bottom_pad=float(stage.get("bottom_pad", layout.get("stage_bottom_pad", 0.12))),
        gap_above_visual=float(stage.get("gap_above_visual", layout.get("stage_gap_above_visual", 0.10))),
        gap_below_visual=float(stage.get("gap_below_visual", layout.get("stage_gap_below_visual", 0.10))),
    )

    visual_override = stage.get("visual_box")
    if isinstance(visual_override, Mapping):
        visual_box = _box_from_dict(visual_override, visual_box)

    add_mini_visual(
        slide,
        kind=str(stage.get("mini_visual", "")),
        x=visual_box.x,
        y=visual_box.y,
        w=visual_box.w,
        h=visual_box.h,
        suffix=f"_example_pipeline_{idx}",
        variant=stage_style["visual_variant"],
    )

    current_y = visual_box.bottom + float(stage.get("below_visual_gap", layout.get("stage_below_visual_gap", 0.08)))

    if caption_text:
        caption_box = Box(card_box.x + 0.12, current_y, card_box.w - 0.24, caption_h)
        caption_font = _fit_stage_text(
            caption_text,
            caption_box,
            min_font=int(stage.get("caption_min_font", layout.get("stage_caption_min_font", 11))),
            max_font=int(stage.get("caption_max_font", layout.get("stage_caption_max_font", 13))),
            max_lines=int(stage.get("caption_max_lines", layout.get("stage_caption_max_lines", 2))),
        )
        add_textbox(
            slide,
            x=caption_box.x,
            y=caption_box.y,
            w=caption_box.w,
            h=caption_box.h,
            text=caption_text,
            font_name=BODY_FONT,
            font_size=caption_font,
            color=stage_style["caption_color"],
            bold=False,
            align=pipeline_style["caption_align"],
        )
        current_y += caption_h + float(stage.get("caption_to_formula_gap", layout.get("caption_to_formula_gap", 0.04)))

    if formula_text:
        formula_box = Box(card_box.x + 0.10, current_y, card_box.w - 0.20, formula_h)
        formula_font = _fit_stage_text(
            formula_text,
            formula_box,
            min_font=int(stage.get("formula_min_font", layout.get("stage_formula_min_font", 11))),
            max_font=int(stage.get("formula_max_font", layout.get("stage_formula_max_font", 13))),
            max_lines=int(stage.get("formula_max_lines", layout.get("stage_formula_max_lines", 2))),
        )
        add_textbox(
            slide,
            x=formula_box.x,
            y=formula_box.y,
            w=formula_box.w,
            h=formula_box.h,
            text=formula_text,
            font_name=FORMULA_FONT,
            font_size=formula_font,
            color=stage_style["formula_color"],
            bold=False,
            align=pipeline_style["formula_align"],
        )


def _default_pipeline_region(
    *,
    header_content_top_y: float,
    layout: Mapping[str, Any],
    has_bullets: bool,
    has_takeaway: bool,
) -> Box:
    pipeline_x = float(layout.get("pipeline_x", 0.82))
    pipeline_y = float(layout.get("pipeline_y", header_content_top_y + float(layout.get("content_to_pipeline_gap", 0.20))))
    pipeline_w = float(layout.get("pipeline_w", 11.32))

    if "pipeline_h" in layout:
        pipeline_h = float(layout["pipeline_h"])
    else:
        if has_takeaway:
            bottom_limit = float(layout.get("pipeline_bottom_limit", 4.70))
        elif has_bullets:
            bottom_limit = float(layout.get("pipeline_bottom_limit", 4.95))
        else:
            bottom_limit = float(layout.get("pipeline_bottom_limit", 5.30))
        pipeline_h = max(1.40, bottom_limit - pipeline_y)

    return Box(pipeline_x, pipeline_y, pipeline_w, pipeline_h)


def build_example_pipeline_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    slide_theme_name = spec.get("theme", "concept")
    theme_obj = get_theme(slide_theme_name=slide_theme_name)

    bg = spec.get("background") or choose_background(slide_theme_name, counters)
    slide = new_slide(prs, bg)

    layout = dict(spec.get("layout", {}) or {})
    stages = list(spec.get("example_pipeline", {}).get("stages", []) or [])
    bullets = list(spec.get("bullets", []) or [])
    takeaway = str(spec.get("takeaway", "")).strip()

    header_result = render_header_from_spec(
        slide,
        spec,
        theme=theme_obj,
    )

    pipeline_style = _resolve_pipeline_style(spec, theme_obj=theme_obj)

    region_dict = layout.get("pipeline_region")
    if isinstance(region_dict, Mapping):
        fallback_region = _default_pipeline_region(
            header_content_top_y=header_result.content_top_y,
            layout=layout,
            has_bullets=bool(bullets),
            has_takeaway=bool(takeaway),
        )
        region = _box_from_dict(region_dict, fallback_region)
    else:
        region = _default_pipeline_region(
            header_content_top_y=header_result.content_top_y,
            layout=layout,
            has_bullets=bool(bullets),
            has_takeaway=bool(takeaway),
        )

    gap = float(layout.get("pipeline_gap", 0.30))

    count = max(1, len(stages))
    card_boxes = distribute_columns(region, count, gap=gap)

    for idx, stage in enumerate(stages):
        card_box = card_boxes[idx]
        _add_stage_card(
            slide,
            stage,
            card_box,
            idx,
            pipeline_style=pipeline_style,
            layout=layout,
        )

        if idx < count - 1:
            next_box = card_boxes[idx + 1]
            add_soft_connector(
                slide,
                x1=card_box.right,
                y1=card_box.y + card_box.h / 2,
                x2=next_box.x,
                y2=next_box.y + next_box.h / 2,
                color=pipeline_style["connector_color"],
                width_pt=pipeline_style["connector_width_pt"],
            )

    if bullets:
        bullets_text = _join_items(bullets)
        bullets_box = Box(
            float(layout.get("bullets_x", 1.00)),
            float(layout.get("bullets_y", region.bottom + 0.28)),
            float(layout.get("bullets_w", 11.00)),
            float(layout.get("bullets_h", 0.24)),
        )
        bullets_font = _fit_stage_text(
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
            color=pipeline_style["bullets_color"],
            bold=bool(layout.get("bullets_bold", False)),
            align=layout.get("bullets_align", PP_ALIGN.CENTER),
        )

    if takeaway:
        takeaway_box = Box(
            float(layout.get("takeaway_x", 1.02)),
            float(layout.get("takeaway_y", region.bottom + 0.72)),
            float(layout.get("takeaway_w", 10.96)),
            float(layout.get("takeaway_h", 0.42)),
        )
        takeaway_font = _fit_stage_text(
            takeaway,
            takeaway_box,
            min_font=int(layout.get("takeaway_min_font", 12)),
            max_font=int(layout.get("takeaway_max_font", 14)),
            max_lines=int(layout.get("takeaway_max_lines", 2)),
        )
        add_textbox(
            slide,
            x=takeaway_box.x,
            y=takeaway_box.y,
            w=takeaway_box.w,
            h=takeaway_box.h,
            text=takeaway,
            font_name=BODY_FONT,
            font_size=takeaway_font,
            color=pipeline_style["takeaway_color"],
            bold=bool(layout.get("takeaway_bold", False)),
            align=layout.get("takeaway_align", PP_ALIGN.CENTER),
        )

    add_footer(
        slide,
        dark=pipeline_style["footer_dark"],
        color=pipeline_style["footer_color"],
    )
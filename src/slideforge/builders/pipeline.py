from __future__ import annotations

from typing import Any, Mapping

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual, add_visual_with_caption
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

    takeaway_fill_default = theme_obj.box_fill_color
    if takeaway_fill_default is None:
        takeaway_fill_default = card_fill_default

    return {
        "card_fill_color": resolve_color(pipeline_style.get("card_fill_color"), card_fill_default),
        "card_line_color": resolve_color(pipeline_style.get("card_line_color"), theme_obj.box_line_color),
        "card_title_color": resolve_color(pipeline_style.get("card_title_color"), theme_obj.box_title_color),
        "card_body_color": resolve_color(pipeline_style.get("card_body_color"), theme_obj.subtitle_color),
        "card_footer_color": resolve_color(pipeline_style.get("card_footer_color"), theme_obj.body_color),
        "card_visual_variant": str(pipeline_style.get("card_visual_variant", theme_obj.panel_visual_variant)),
        "card_line_width_pt": float(pipeline_style.get("card_line_width_pt", 1.25)),
        "connector_color": resolve_color(pipeline_style.get("connector_color"), theme_obj.connector_color),
        "connector_width_pt": float(pipeline_style.get("connector_width_pt", theme_obj.connector_width_pt)),
        "examples_label_color": resolve_color(pipeline_style.get("examples_label_color"), theme_obj.subtitle_color),
        "examples_visual_variant": str(pipeline_style.get("examples_visual_variant", theme_obj.panel_visual_variant)),
        "takeaway_fill_color": resolve_color(pipeline_style.get("takeaway_fill_color"), takeaway_fill_default),
        "takeaway_line_color": resolve_color(pipeline_style.get("takeaway_line_color"), theme_obj.box_line_color),
        "takeaway_text_color": resolve_color(pipeline_style.get("takeaway_text_color"), theme_obj.subtitle_color),
        "takeaway_line_width_pt": float(pipeline_style.get("takeaway_line_width_pt", 1.25)),
        "footer_color": resolve_color(pipeline_style.get("footer_color"), theme_obj.footer_color),
        "footer_dark": bool(pipeline_style.get("footer_dark", theme_obj.footer_dark)),
    }


def _resolve_step_style(
    step: Mapping[str, Any],
    *,
    pipeline_style: Mapping[str, Any],
) -> dict[str, Any]:
    step_style = dict(step.get("style", {}) or {})
    return {
        "fill_color": resolve_color(step_style.get("fill_color"), pipeline_style["card_fill_color"]),
        "line_color": resolve_color(step_style.get("line_color"), pipeline_style["card_line_color"]),
        "title_color": resolve_color(step_style.get("title_color"), pipeline_style["card_title_color"]),
        "body_color": resolve_color(step_style.get("body_color"), pipeline_style["card_body_color"]),
        "footer_color": resolve_color(step_style.get("footer_color"), pipeline_style["card_footer_color"]),
        "visual_variant": str(step_style.get("visual_variant", pipeline_style["card_visual_variant"])),
        "line_width_pt": float(step_style.get("line_width_pt", pipeline_style["card_line_width_pt"])),
    }


def _pipeline_card(
    slide,
    step: dict[str, Any],
    card_box: Box,
    idx: int,
    *,
    pipeline_style: Mapping[str, Any],
    layout: Mapping[str, Any],
) -> None:
    step_style = _resolve_step_style(step, pipeline_style=pipeline_style)

    add_rounded_box(
        slide,
        card_box.x,
        card_box.y,
        card_box.w,
        card_box.h,
        line_color=step_style["line_color"],
        fill_color=step_style["fill_color"],
        line_width_pt=step_style["line_width_pt"],
    )

    title_text = str(step.get("title", "")).strip()
    body_text = str(step.get("body", "")).strip()
    footer_text = str(step.get("footer", "")).strip()

    title_h = float(step.get("title_h", layout.get("step_title_h", 0.24)))
    body_h = float(step.get("body_h", layout.get("step_body_h", 0.22 if body_text else 0.0)))
    footer_h = float(step.get("footer_h", layout.get("step_footer_h", 0.18 if footer_text else 0.0)))

    title_box = Box(card_box.x + 0.10, card_box.y + 0.10, card_box.w - 0.20, title_h)
    title_font = _fit_text_size(
        title_text,
        title_box,
        min_font=int(step.get("title_min_font", layout.get("step_title_min_font", 12))),
        max_font=int(step.get("title_max_font", layout.get("step_title_max_font", 15))),
        max_lines=int(step.get("title_max_lines", layout.get("step_title_max_lines", 2))),
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
        color=step_style["title_color"],
        bold=True,
        align=PP_ALIGN.CENTER,
    )

    visual_box = centered_visual_in_card(
        card_box,
        title_h=title_h,
        caption_h=body_h,
        formula_h=footer_h,
        top_pad=float(step.get("top_pad", layout.get("step_top_pad", 0.10))),
        bottom_pad=float(step.get("bottom_pad", layout.get("step_bottom_pad", 0.12))),
        gap_above_visual=float(step.get("gap_above_visual", layout.get("step_gap_above_visual", 0.10))),
        gap_below_visual=float(step.get("gap_below_visual", layout.get("step_gap_below_visual", 0.10))),
    )

    visual_override = step.get("visual_box")
    if isinstance(visual_override, Mapping):
        visual_box = _box_from_dict(visual_override, visual_box)

    add_mini_visual(
        slide,
        kind=str(step.get("mini_visual", "")),
        x=visual_box.x,
        y=visual_box.y,
        w=visual_box.w,
        h=visual_box.h,
        suffix=f"_pipeline_{idx}",
        variant=step_style["visual_variant"],
    )

    current_y = visual_box.bottom + float(step.get("below_visual_gap", layout.get("step_below_visual_gap", 0.08)))

    if body_text:
        body_box = Box(card_box.x + 0.12, current_y, card_box.w - 0.24, body_h)
        body_font = _fit_text_size(
            body_text,
            body_box,
            min_font=int(step.get("body_min_font", layout.get("step_body_min_font", 11))),
            max_font=int(step.get("body_max_font", layout.get("step_body_max_font", 13))),
            max_lines=int(step.get("body_max_lines", layout.get("step_body_max_lines", 2))),
        )
        add_textbox(
            slide,
            x=body_box.x,
            y=body_box.y,
            w=body_box.w,
            h=body_box.h,
            text=body_text,
            font_name=BODY_FONT,
            font_size=body_font,
            color=step_style["body_color"],
            bold=False,
            align=PP_ALIGN.CENTER,
        )
        current_y += body_h + float(step.get("body_to_footer_gap", layout.get("body_to_footer_gap", 0.04)))

    if footer_text:
        footer_box = Box(card_box.x + 0.10, current_y, card_box.w - 0.20, footer_h)
        footer_font = _fit_text_size(
            footer_text,
            footer_box,
            min_font=int(step.get("footer_min_font", layout.get("step_footer_min_font", 11))),
            max_font=int(step.get("footer_max_font", layout.get("step_footer_max_font", 13))),
            max_lines=int(step.get("footer_max_lines", layout.get("step_footer_max_lines", 2))),
        )
        add_textbox(
            slide,
            x=footer_box.x,
            y=footer_box.y,
            w=footer_box.w,
            h=footer_box.h,
            text=footer_text,
            font_name=FORMULA_FONT,
            font_size=footer_font,
            color=step_style["footer_color"],
            bold=False,
            align=PP_ALIGN.CENTER,
        )


def _default_pipeline_region(
    *,
    header_content_top_y: float,
    layout: Mapping[str, Any],
    has_examples: bool,
    has_takeaway: bool,
) -> Box:
    pipeline_x = float(layout.get("pipeline_x", 0.86))
    pipeline_y = float(layout.get("pipeline_y", header_content_top_y + float(layout.get("content_to_pipeline_gap", 0.18))))
    pipeline_w = float(layout.get("pipeline_w", 11.28))

    if "pipeline_h" in layout:
        pipeline_h = float(layout["pipeline_h"])
    else:
        if has_takeaway:
            bottom_limit = float(layout.get("pipeline_bottom_limit", 4.30))
        elif has_examples:
            bottom_limit = float(layout.get("pipeline_bottom_limit", 4.95))
        else:
            bottom_limit = float(layout.get("pipeline_bottom_limit", 5.30))
        pipeline_h = max(1.25, bottom_limit - pipeline_y)

    return Box(pipeline_x, pipeline_y, pipeline_w, pipeline_h)


def build_pipeline_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    slide_theme_name = spec.get("theme", "concept")
    theme_obj = get_theme(slide_theme_name=slide_theme_name)

    bg = spec.get("background") or choose_background(slide_theme_name, counters)
    slide = new_slide(prs, bg)

    layout = dict(spec.get("layout", {}) or {})
    steps = list(spec.get("pipeline", {}).get("steps", []) or [])

    takeaway = str(spec.get("takeaway", "")).strip()
    examples = list(spec.get("examples", []) or [])

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
            has_examples=bool(examples),
            has_takeaway=bool(takeaway),
        )
        region = _box_from_dict(region_dict, fallback_region)
    else:
        region = _default_pipeline_region(
            header_content_top_y=header_result.content_top_y,
            layout=layout,
            has_examples=bool(examples),
            has_takeaway=bool(takeaway),
        )

    gap = float(layout.get("pipeline_gap", 0.22))

    count = max(1, len(steps))
    card_boxes = distribute_columns(region, count, gap=gap)

    for idx, step in enumerate(steps):
        card_box = card_boxes[idx]
        _pipeline_card(
            slide,
            step,
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
                y2=card_box.y + next_box.h / 2,
                color=pipeline_style["connector_color"],
                width_pt=pipeline_style["connector_width_pt"],
            )

    if examples:
        examples_label_box = Box(
            float(layout.get("examples_label_x", 1.10)),
            float(layout.get("examples_label_y", region.bottom + 0.22)),
            float(layout.get("examples_label_w", 10.90)),
            float(layout.get("examples_label_h", 0.20)),
        )
        examples_label_text = str(layout.get("examples_label_text", "Running examples"))
        examples_label_font = _fit_text_size(
            examples_label_text,
            examples_label_box,
            min_font=int(layout.get("examples_label_min_font", 12)),
            max_font=int(layout.get("examples_label_max_font", 13)),
            max_lines=1,
        )
        add_textbox(
            slide,
            x=examples_label_box.x,
            y=examples_label_box.y,
            w=examples_label_box.w,
            h=examples_label_box.h,
            text=examples_label_text,
            font_name=BODY_FONT,
            font_size=examples_label_font,
            color=pipeline_style["examples_label_color"],
            bold=True,
            align=layout.get("examples_label_align", PP_ALIGN.CENTER),
        )

        ex_y = float(layout.get("examples_y", examples_label_box.bottom + 0.04))
        ex_h = float(layout.get("examples_h", 0.98))
        ex_gap = float(layout.get("examples_gap", 0.38))
        ex_x = float(layout.get("examples_x", 1.18))

        max_examples = int(layout.get("max_examples", 2))
        rendered_examples = examples[:max_examples]

        if "examples_w" in layout:
            ex_w = float(layout["examples_w"])
            x_positions = [ex_x + idx * (ex_w + ex_gap) for idx in range(len(rendered_examples))]
        else:
            total_w = float(layout.get("examples_total_w", 10.97))
            if rendered_examples:
                ex_w = (total_w - ex_gap * (len(rendered_examples) - 1)) / len(rendered_examples)
            else:
                ex_w = 4.85
            x_positions = [ex_x + idx * (ex_w + ex_gap) for idx in range(len(rendered_examples))]

        for idx, ex in enumerate(rendered_examples):
            if isinstance(ex, dict):
                ex_kind = str(ex.get("mini_visual", ""))
                ex_text = str(ex.get("text", ""))
                ex_variant = str(ex.get("visual_variant", pipeline_style["examples_visual_variant"]))
                ex_font = int(ex.get("caption_font_size", layout.get("examples_caption_font_size", 12)))
            else:
                ex_kind = ""
                ex_text = str(ex)
                ex_variant = pipeline_style["examples_visual_variant"]
                ex_font = int(layout.get("examples_caption_font_size", 12))

            add_visual_with_caption(
                slide,
                kind=ex_kind,
                x=x_positions[idx],
                y=ex_y,
                w=ex_w,
                h=ex_h,
                caption=ex_text,
                suffix=f"_pipeline_example_{idx}",
                variant=ex_variant,
                caption_font_size=ex_font,
            )

    if takeaway:
        fallback_takeaway_box = Box(
            float(layout.get("takeaway_x", 1.00)),
            float(layout.get("takeaway_y", 5.40)),
            float(layout.get("takeaway_w", 10.90)),
            float(layout.get("takeaway_h", 0.70)),
        )
        takeaway_dict = layout.get("takeaway_box")
        takeaway_box = (
            _box_from_dict(takeaway_dict, fallback_takeaway_box)
            if isinstance(takeaway_dict, Mapping)
            else fallback_takeaway_box
        )

        add_rounded_box(
            slide,
            takeaway_box.x,
            takeaway_box.y,
            takeaway_box.w,
            takeaway_box.h,
            line_color=pipeline_style["takeaway_line_color"],
            fill_color=pipeline_style["takeaway_fill_color"],
            line_width_pt=pipeline_style["takeaway_line_width_pt"],
        )

        takeaway_text_box = Box(
            takeaway_box.x + float(layout.get("takeaway_inner_pad_x", 0.16)),
            takeaway_box.y + float(layout.get("takeaway_inner_pad_y", 0.10)),
            takeaway_box.w - 2 * float(layout.get("takeaway_inner_pad_x", 0.16)),
            takeaway_box.h - float(layout.get("takeaway_text_h_pad", 0.16)),
        )
        takeaway_font = _fit_text_size(
            takeaway,
            takeaway_text_box,
            min_font=int(layout.get("takeaway_min_font", 12)),
            max_font=int(layout.get("takeaway_max_font", 14)),
            max_lines=int(layout.get("takeaway_max_lines", 3)),
        )
        add_textbox(
            slide,
            x=takeaway_text_box.x,
            y=takeaway_text_box.y,
            w=takeaway_text_box.w,
            h=takeaway_text_box.h,
            text=takeaway,
            font_name=BODY_FONT,
            font_size=takeaway_font,
            color=pipeline_style["takeaway_text_color"],
            bold=bool(layout.get("takeaway_bold", False)),
            align=layout.get("takeaway_align", PP_ALIGN.CENTER),
        )

    add_footer(
        slide,
        dark=pipeline_style["footer_dark"],
        color=pipeline_style["footer_color"],
    )
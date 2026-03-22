from __future__ import annotations

from typing import Any, Mapping

from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual, add_visual_with_caption
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, OFFWHITE, TITLE_FONT
from slideforge.config.themes import SlideTheme, resolve_color
from slideforge.layout.autofit import Box, centered_visual_in_card, fit_text
from slideforge.render.primitives import add_rounded_box, add_soft_connector, add_textbox
from slideforge.spec.pipeline_normalization import PipelineExample, PipelineStage


def fit_text_size(text: str, box: Box, *, min_font: int, max_font: int, max_lines: int) -> int:
    if not str(text or "").strip() or box.w <= 0 or box.h <= 0:
        return max_font
    fitted = fit_text(
        str(text).strip(),
        box.w,
        box.h,
        min_font_size=min_font,
        max_font_size=max_font,
        max_lines=max_lines,
    )
    return max(min_font, fitted.font_size)


def _box_from_dict(raw: Mapping[str, Any], fallback: Box) -> Box:
    return Box(
        float(raw.get("x", fallback.x)),
        float(raw.get("y", fallback.y)),
        float(raw.get("w", fallback.w)),
        float(raw.get("h", fallback.h)),
    )


def resolve_pipeline_style(spec: Mapping[str, Any], *, theme_obj: SlideTheme) -> dict[str, Any]:
    pipeline_style = dict(spec.get("pipeline_style", {}) or {})
    card_fill_default = theme_obj.box_fill_color or theme_obj.panel_fill_color or OFFWHITE
    takeaway_fill_default = theme_obj.box_fill_color or card_fill_default
    return {
        "card_fill_color": resolve_color(pipeline_style.get("card_fill_color"), card_fill_default),
        "card_line_color": resolve_color(pipeline_style.get("card_line_color"), theme_obj.box_line_color),
        "card_title_color": resolve_color(pipeline_style.get("card_title_color"), theme_obj.box_title_color),
        "card_caption_color": resolve_color(pipeline_style.get("card_caption_color"), theme_obj.subtitle_color),
        "card_formula_color": resolve_color(pipeline_style.get("card_formula_color"), theme_obj.body_color),
        "card_footer_color": resolve_color(pipeline_style.get("card_footer_color"), theme_obj.body_color),
        "card_visual_variant": str(pipeline_style.get("card_visual_variant", theme_obj.panel_visual_variant)),
        "card_line_width_pt": float(pipeline_style.get("card_line_width_pt", 1.25)),
        "connector_color": resolve_color(pipeline_style.get("connector_color"), theme_obj.connector_color),
        "connector_width_pt": float(pipeline_style.get("connector_width_pt", theme_obj.connector_width_pt)),
        "examples_label_color": resolve_color(pipeline_style.get("examples_label_color"), theme_obj.subtitle_color),
        "examples_visual_variant": str(pipeline_style.get("examples_visual_variant", theme_obj.panel_visual_variant)),
        "bullets_color": resolve_color(pipeline_style.get("bullets_color"), theme_obj.subtitle_color),
        "takeaway_fill_color": resolve_color(pipeline_style.get("takeaway_fill_color"), takeaway_fill_default),
        "takeaway_line_color": resolve_color(pipeline_style.get("takeaway_line_color"), theme_obj.box_line_color),
        "takeaway_text_color": resolve_color(pipeline_style.get("takeaway_text_color"), theme_obj.subtitle_color),
        "takeaway_line_width_pt": float(pipeline_style.get("takeaway_line_width_pt", 1.25)),
        "takeaway_color": resolve_color(pipeline_style.get("takeaway_color"), theme_obj.subtitle_color),
        "footer_color": resolve_color(pipeline_style.get("footer_color"), theme_obj.footer_color),
        "footer_dark": bool(pipeline_style.get("footer_dark", theme_obj.footer_dark)),
        "title_align": pipeline_style.get("card_title_align", PP_ALIGN.CENTER),
        "caption_align": pipeline_style.get("card_caption_align", PP_ALIGN.CENTER),
        "formula_align": pipeline_style.get("card_formula_align", PP_ALIGN.CENTER),
    }


def resolve_stage_style(stage: PipelineStage, *, pipeline_style: Mapping[str, Any]) -> dict[str, Any]:
    stage_style = dict(stage.style or {})
    return {
        "fill_color": resolve_color(stage_style.get("fill_color"), pipeline_style["card_fill_color"]),
        "line_color": resolve_color(stage_style.get("line_color"), pipeline_style["card_line_color"]),
        "title_color": resolve_color(stage_style.get("title_color"), pipeline_style["card_title_color"]),
        "caption_color": resolve_color(stage_style.get("caption_color") or stage_style.get("body_color"), pipeline_style["card_caption_color"]),
        "formula_color": resolve_color(stage_style.get("formula_color") or stage_style.get("footer_color"), pipeline_style.get("card_formula_color", pipeline_style.get("card_footer_color"))),
        "visual_variant": str(stage_style.get("visual_variant", pipeline_style["card_visual_variant"])),
        "line_width_pt": float(stage_style.get("line_width_pt", pipeline_style["card_line_width_pt"])),
    }


def render_stage_card(slide, stage: PipelineStage, card_box: Box, idx: int, *, pipeline_style: Mapping[str, Any], layout: Mapping[str, Any], suffix_prefix: str) -> None:
    stage_style = resolve_stage_style(stage, pipeline_style=pipeline_style)
    raw = stage.raw
    add_rounded_box(
        slide, card_box.x, card_box.y, card_box.w, card_box.h,
        line_color=stage_style["line_color"], fill_color=stage_style["fill_color"], line_width_pt=stage_style["line_width_pt"],
    )

    title_h = float(raw.get("title_h", layout.get("stage_title_h", layout.get("step_title_h", 0.24))))
    caption_h_default = 0.24 if stage.caption else 0.0
    caption_h = float(raw.get("caption_h", raw.get("body_h", layout.get("stage_caption_h", layout.get("step_body_h", caption_h_default)))))
    formula_h_default = 0.18 if stage.formula else 0.0
    formula_h = float(raw.get("formula_h", raw.get("footer_h", layout.get("stage_formula_h", layout.get("step_footer_h", formula_h_default)))))

    title_box = Box(card_box.x + 0.10, card_box.y + 0.10, card_box.w - 0.20, title_h)
    title_font = fit_text_size(
        stage.title, title_box,
        min_font=int(raw.get("title_min_font", layout.get("stage_title_min_font", layout.get("step_title_min_font", 12)))),
        max_font=int(raw.get("title_max_font", layout.get("stage_title_max_font", layout.get("step_title_max_font", 15)))),
        max_lines=int(raw.get("title_max_lines", layout.get("stage_title_max_lines", layout.get("step_title_max_lines", 2)))),
    )
    add_textbox(slide, x=title_box.x, y=title_box.y, w=title_box.w, h=title_box.h, text=stage.title, font_name=TITLE_FONT, font_size=title_font, color=stage_style["title_color"], bold=True, align=pipeline_style["title_align"])

    visual_box = centered_visual_in_card(
        card_box,
        title_h=title_h,
        caption_h=caption_h,
        formula_h=formula_h,
        top_pad=float(raw.get("top_pad", layout.get("stage_top_pad", layout.get("step_top_pad", 0.10)))),
        bottom_pad=float(raw.get("bottom_pad", layout.get("stage_bottom_pad", layout.get("step_bottom_pad", 0.12)))),
        gap_above_visual=float(raw.get("gap_above_visual", layout.get("stage_gap_above_visual", layout.get("step_gap_above_visual", 0.10)))),
        gap_below_visual=float(raw.get("gap_below_visual", layout.get("stage_gap_below_visual", layout.get("step_gap_below_visual", 0.10)))),
    )
    if stage.visual_box:
        visual_box = _box_from_dict(stage.visual_box, visual_box)

    add_mini_visual(slide, kind=stage.mini_visual, x=visual_box.x, y=visual_box.y, w=visual_box.w, h=visual_box.h, suffix=f"_{suffix_prefix}_{idx}", variant=stage_style["visual_variant"])

    current_y = visual_box.bottom + float(raw.get("below_visual_gap", layout.get("stage_below_visual_gap", layout.get("step_below_visual_gap", 0.08))))
    if stage.caption:
        caption_box = Box(card_box.x + 0.12, current_y, card_box.w - 0.24, caption_h)
        caption_font = fit_text_size(
            stage.caption, caption_box,
            min_font=int(raw.get("caption_min_font", raw.get("body_min_font", layout.get("stage_caption_min_font", layout.get("step_body_min_font", 11))))),
            max_font=int(raw.get("caption_max_font", raw.get("body_max_font", layout.get("stage_caption_max_font", layout.get("step_body_max_font", 13))))),
            max_lines=int(raw.get("caption_max_lines", raw.get("body_max_lines", layout.get("stage_caption_max_lines", layout.get("step_body_max_lines", 2))))),
        )
        add_textbox(slide, x=caption_box.x, y=caption_box.y, w=caption_box.w, h=caption_box.h, text=stage.caption, font_name=BODY_FONT, font_size=caption_font, color=stage_style["caption_color"], bold=False, align=pipeline_style["caption_align"])
        current_y += caption_h + float(raw.get("caption_to_formula_gap", raw.get("body_to_footer_gap", layout.get("caption_to_formula_gap", layout.get("body_to_footer_gap", 0.04)))))

    if stage.formula:
        formula_box = Box(card_box.x + 0.10, current_y, card_box.w - 0.20, formula_h)
        formula_font = fit_text_size(
            stage.formula, formula_box,
            min_font=int(raw.get("formula_min_font", raw.get("footer_min_font", layout.get("stage_formula_min_font", layout.get("step_footer_min_font", 11))))),
            max_font=int(raw.get("formula_max_font", raw.get("footer_max_font", layout.get("stage_formula_max_font", layout.get("step_footer_max_font", 13))))),
            max_lines=int(raw.get("formula_max_lines", raw.get("footer_max_lines", layout.get("stage_formula_max_lines", layout.get("step_footer_max_lines", 2))))),
        )
        add_textbox(slide, x=formula_box.x, y=formula_box.y, w=formula_box.w, h=formula_box.h, text=stage.formula, font_name=FORMULA_FONT, font_size=formula_font, color=stage_style["formula_color"], bold=False, align=pipeline_style["formula_align"])


def render_connectors(slide, connectors, *, style: Mapping[str, Any]) -> None:
    for seg in connectors:
        add_soft_connector(slide, x1=seg.x1, y1=seg.y1, x2=seg.x2, y2=seg.y2, color=style["connector_color"], width_pt=style["connector_width_pt"])


def render_examples_row(slide, examples: list[PipelineExample], boxes: list[Box], *, label_box: Box | None, label_text: str, style: Mapping[str, Any], layout: Mapping[str, Any], suffix_prefix: str) -> None:
    if label_box is not None:
        font = fit_text_size(label_text, label_box, min_font=int(layout.get("examples_label_min_font", 12)), max_font=int(layout.get("examples_label_max_font", 13)), max_lines=1)
        add_textbox(slide, x=label_box.x, y=label_box.y, w=label_box.w, h=label_box.h, text=label_text, font_name=BODY_FONT, font_size=font, color=style["examples_label_color"], bold=True, align=layout.get("examples_label_align", PP_ALIGN.CENTER))
    for idx, (ex, box) in enumerate(zip(examples[:len(boxes)], boxes)):
        add_visual_with_caption(slide, kind=ex.mini_visual, x=box.x, y=box.y, w=box.w, h=box.h, caption=ex.text, suffix=f"_{suffix_prefix}_{idx}", variant=ex.visual_variant or style["examples_visual_variant"], caption_font_size=ex.caption_font_size or int(layout.get("examples_caption_font_size", 12)))


def render_bullets_box(slide, bullets: list[str], box: Box | None, *, style: Mapping[str, Any], layout: Mapping[str, Any]) -> None:
    if box is None or not bullets:
        return
    text = "   •   ".join([b.strip() for b in bullets if str(b).strip()])
    font = fit_text_size(text, box, min_font=int(layout.get("bullets_min_font", 12)), max_font=int(layout.get("bullets_max_font", 14)), max_lines=int(layout.get("bullets_max_lines", 2)))
    add_textbox(slide, x=box.x, y=box.y, w=box.w, h=box.h, text=text, font_name=BODY_FONT, font_size=font, color=style["bullets_color"], bold=bool(layout.get("bullets_bold", False)), align=layout.get("bullets_align", PP_ALIGN.CENTER))


def render_takeaway(slide, takeaway: str, box: Box | None, *, style: Mapping[str, Any], layout: Mapping[str, Any], boxed: bool) -> None:
    if box is None or not str(takeaway or "").strip():
        return
    if boxed:
        add_rounded_box(slide, box.x, box.y, box.w, box.h, line_color=style["takeaway_line_color"], fill_color=style["takeaway_fill_color"], line_width_pt=style["takeaway_line_width_pt"])
        text_box = Box(
            box.x + float(layout.get("takeaway_inner_pad_x", 0.16)),
            box.y + float(layout.get("takeaway_inner_pad_y", 0.10)),
            box.w - 2 * float(layout.get("takeaway_inner_pad_x", 0.16)),
            box.h - float(layout.get("takeaway_text_h_pad", 0.16)),
        )
        min_font = int(layout.get("takeaway_min_font", 12))
        max_font = int(layout.get("takeaway_max_font", 14))
        max_lines = int(layout.get("takeaway_max_lines", 3))
        color = style["takeaway_text_color"]
    else:
        text_box = box
        min_font = int(layout.get("takeaway_min_font", 12))
        max_font = int(layout.get("takeaway_max_font", 14))
        max_lines = int(layout.get("takeaway_max_lines", 2))
        color = style["takeaway_color"]
    font = fit_text_size(takeaway, text_box, min_font=min_font, max_font=max_font, max_lines=max_lines)
    add_textbox(slide, x=text_box.x, y=text_box.y, w=text_box.w, h=text_box.h, text=takeaway, font_name=BODY_FONT, font_size=font, color=color, bold=bool(layout.get("takeaway_bold", False)), align=layout.get("takeaway_align", PP_ALIGN.CENTER))

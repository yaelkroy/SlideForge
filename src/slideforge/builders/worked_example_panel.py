from __future__ import annotations

from typing import Any, Mapping, Sequence

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, OFFWHITE
from slideforge.config.themes import get_theme, resolve_color
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, fit_text
from slideforge.render.header import render_header_from_spec
from slideforge.render.math_blocks import MathBlockStyle, render_compact_derivation_stack, render_result_callout
from slideforge.render.primitives import add_box_title, add_footer, add_rounded_box, add_textbox


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _lines(items: Sequence[Any] | None) -> list[str]:
    return [_clean(item) for item in (items or []) if _clean(item)]


def _fit(text: str, box: Box, min_font: int, max_font: int, max_lines: int | None, line_spacing: float = 1.12) -> int:
    if not _clean(text) or box.w <= 0 or box.h <= 0:
        return max_font
    fitted = fit_text(
        text,
        box.w,
        box.h,
        min_font_size=min_font,
        max_font_size=max_font,
        max_lines=max_lines,
        line_spacing=line_spacing,
    )
    return max(min_font, fitted.font_size)


def _estimate(text: str, width: float, min_font: int, max_font: int, max_lines: int | None, extra: float = 0.04) -> float:
    if not _clean(text) or width <= 0:
        return 0.0
    fitted = fit_text(text, width, 10.0, min_font_size=min_font, max_font_size=max_font, max_lines=max_lines)
    return max(0.0, fitted.estimated_height + extra)


def _box_from(raw: Mapping[str, Any] | None, fallback: Box) -> Box:
    if not isinstance(raw, Mapping):
        return fallback
    return Box(float(raw.get("x", fallback.x)), float(raw.get("y", fallback.y)), float(raw.get("w", fallback.w)), float(raw.get("h", fallback.h)))


def _style(spec: Mapping[str, Any], theme_obj) -> dict[str, Any]:
    raw = dict(spec.get("worked_example_style", {}) or {})
    fill = theme_obj.box_fill_color or theme_obj.panel_fill_color or OFFWHITE
    style = {
        "surface_fill_color": resolve_color(raw.get("surface_fill_color"), fill),
        "surface_line_color": resolve_color(raw.get("surface_line_color"), theme_obj.box_line_color),
        "surface_line_width_pt": float(raw.get("surface_line_width_pt", 1.2)),
        "label_color": resolve_color(raw.get("label_color"), theme_obj.box_title_color),
        "body_color": resolve_color(raw.get("body_color"), theme_obj.subtitle_color),
        "formula_color": resolve_color(raw.get("formula_color"), theme_obj.body_color),
        "result_color": resolve_color(raw.get("result_color"), theme_obj.body_color),
        "takeaway_color": resolve_color(raw.get("takeaway_color"), theme_obj.subtitle_color),
        "footer_color": resolve_color(raw.get("footer_color"), theme_obj.footer_color),
        "footer_dark": bool(raw.get("footer_dark", theme_obj.footer_dark)),
        "visual_variant": str(raw.get("visual_variant", theme_obj.panel_visual_variant)),
    }
    style["math"] = MathBlockStyle(
        body_color=style["body_color"],
        formula_color=style["formula_color"],
        result_color=style["result_color"],
        label_color=style["label_color"],
        card_fill_color=style["surface_fill_color"],
        card_line_color=style["surface_line_color"],
        final_answer_fill_color=style["surface_fill_color"],
    )
    return style


def _steps(raw_steps: Sequence[Any] | None) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for idx, step in enumerate(raw_steps or [], start=1):
        if isinstance(step, Mapping):
            out.append(
                {
                    "title": _clean(step.get("title") or step.get("label") or f"Step {idx}"),
                    "body": _clean(step.get("body") or step.get("text") or step.get("explanation")),
                    "formula": _clean(step.get("formula") or step.get("equation") or step.get("result")),
                    "note": _clean(step.get("note")),
                }
            )
        else:
            out.append({"title": f"Step {idx}", "body": _clean(step), "formula": "", "note": ""})
    return out


def _serialize_steps(steps: Sequence[Mapping[str, str]]) -> str:
    blocks = []
    for step in steps:
        block = "\n".join([value for value in [step.get("title"), step.get("body"), step.get("formula"), step.get("note")] if _clean(value)])
        if block:
            blocks.append(block)
    return "\n\n".join(blocks)


def _result(result_raw: Any, fallback: Sequence[Any] | None) -> tuple[str, list[str]]:
    if isinstance(result_raw, Mapping):
        return _clean(result_raw.get("label") or result_raw.get("title") or "Result"), _lines(
            [
                result_raw.get("body") or result_raw.get("text") or result_raw.get("explanation"),
                result_raw.get("formula") or result_raw.get("equation"),
                result_raw.get("note"),
            ]
        )
    return "Result", _lines([result_raw]) or _lines(fallback)


def _content(spec: Mapping[str, Any]) -> dict[str, Any]:
    result_label, result_lines = _result(spec.get("result"), spec.get("formulas"))
    return {
        "explanation": _clean(spec.get("text_explanation") or spec.get("explanation")),
        "steps": _steps(spec.get("steps")),
        "result_label": result_label,
        "result_lines": result_lines,
        "takeaway": _clean(spec.get("takeaway")),
        "mini_visual": _clean(spec.get("mini_visual")),
        "visual_label": _clean(spec.get("visual_label") or "Geometry"),
        "visual_caption": _clean(spec.get("visual_caption")),
        "explanation_label": _clean(spec.get("explanation_label") or "Idea"),
        "steps_label": _clean(spec.get("steps_label") or "Steps"),
        "takeaway_label": _clean(spec.get("takeaway_label") or "Takeaway"),
    }


def _outer(layout: Mapping[str, Any], header_result) -> Box:
    fallback = Box(
        float(layout.get("content_x", 0.88)),
        float(layout.get("content_y", header_result.content_top_y + float(layout.get("content_gap_from_header", 0.12)))),
        float(layout.get("content_w", 11.24)),
        float(layout.get("content_h", 5.10)),
    )
    return _box_from(layout.get("content_box"), fallback)


def _card_height(text: str, width: float, min_font: int, max_font: int, min_h: float, max_h: float, max_lines: int | None, extra: float) -> float:
    if not _clean(text):
        return 0.0
    return max(min_h, min(max_h, _estimate(text, width, min_font, max_font, max_lines, extra) + 0.12))


def _two_column(layout: Mapping[str, Any], outer: Box, content: Mapping[str, Any]) -> dict[str, Box | None]:
    col_gap = float(layout.get("column_gap", 0.20))
    block_gap = float(layout.get("block_gap", 0.10))
    preferred = float(layout.get("visual_share", 0.30))
    min_share = float(layout.get("visual_min_share", max(0.24, preferred - 0.07)))
    max_share = float(layout.get("visual_max_share", min(0.46, preferred + 0.08)))
    steps_text = _serialize_steps(content["steps"])
    result_text = "\n".join(content["result_lines"])
    steps_min_h = float(layout.get("steps_min_h", 2.05))
    best = None

    for share in [preferred, max(min_share, preferred - 0.03), max(min_share, preferred - 0.06), min(max_share, preferred + 0.03), min_share, max_share]:
        visual_w = max(2.25, outer.w * share - col_gap * 0.5)
        right_w = max(3.10, outer.w - visual_w - col_gap)
        inner_w = max(0.1, right_w - 0.24)
        expl_h = _card_height(content["explanation"], inner_w, 12, 16, float(layout.get("explanation_min_h", 0.40)), float(layout.get("explanation_max_h", 0.82)), 4, 0.04)
        result_h = _card_height(result_text, inner_w, 12, 17, float(layout.get("result_min_h", 0.56)), float(layout.get("result_max_h", 0.98)), 5, 0.05)
        take_h = _card_height(content["takeaway"], inner_w, 11, 14, float(layout.get("takeaway_min_h", 0.40)), float(layout.get("takeaway_max_h", 0.80)), 4, 0.04)
        steps_need = _estimate(steps_text, inner_w, 10, 13, None, 0.12) + 0.22
        gaps = (block_gap if expl_h and steps_text else 0.0) + (block_gap if (result_h or take_h) and steps_text else 0.0) + (block_gap if result_h and take_h else 0.0)
        steps_avail = max(0.0, outer.h - expl_h - result_h - take_h - gaps)
        score = max(0.0, max(steps_min_h, steps_need) - steps_avail) * 10.0 + share
        cand = (score, visual_w, right_w, expl_h, result_h, take_h)
        if best is None or cand[0] < best[0]:
            best = cand

    _, visual_w, right_w, expl_h, result_h, take_h = best
    base_gaps = (block_gap if expl_h and steps_text else 0.0) + (block_gap if (result_h or take_h) and steps_text else 0.0) + (block_gap if result_h and take_h else 0.0)
    steps_h = max(0.0, outer.h - expl_h - result_h - take_h - base_gaps)
    if steps_h < steps_min_h:
        deficit = steps_min_h - steps_h
        for key, floor in (("take", float(layout.get("takeaway_floor_h", 0.34))), ("result", float(layout.get("result_floor_h", 0.42))), ("expl", float(layout.get("explanation_floor_h", 0.36)))):
            if deficit <= 0:
                break
            if key == "take":
                cut = min(deficit, max(0.0, take_h - floor))
                take_h -= cut
            elif key == "result":
                cut = min(deficit, max(0.0, result_h - floor))
                result_h -= cut
            else:
                cut = min(deficit, max(0.0, expl_h - floor))
                expl_h -= cut
            deficit -= cut
        steps_h = max(0.0, outer.h - expl_h - result_h - take_h - base_gaps)

    right_x = outer.x + visual_w + col_gap
    y = outer.y
    expl_box = Box(right_x, y, right_w, expl_h) if expl_h > 0 else None
    y = y + expl_h + (block_gap if expl_h and steps_h > 0 else 0.0)
    steps_box = Box(right_x, y, right_w, steps_h) if steps_h > 0 else None
    y = y + steps_h + (block_gap if steps_h > 0 and (result_h > 0 or take_h > 0) else 0.0)
    result_box = Box(right_x, y, right_w, result_h) if result_h > 0 else None
    y = y + result_h + (block_gap if result_h > 0 and take_h > 0 else 0.0)
    take_box = Box(right_x, y, right_w, take_h) if take_h > 0 else None
    visual_h = min(outer.h, max(2.30, outer.h * float(layout.get("two_column_visual_height_share", 0.82))))
    visual_y = outer.y + float(layout.get("two_column_visual_y_offset", 0.02))
    visual_h = min(visual_h, outer.y + outer.h - visual_y)
    return {"visual": Box(outer.x, visual_y, visual_w, max(0.0, visual_h)), "explanation": expl_box, "steps": steps_box, "result": result_box, "takeaway": take_box}


def _top_visual(layout: Mapping[str, Any], outer: Box, content: Mapping[str, Any]) -> dict[str, Box | None]:
    gap = float(layout.get("block_gap", 0.10))
    col_gap = float(layout.get("column_gap", 0.20))
    right_share = float(layout.get("lower_right_share", 0.33))
    heavy = 0.16 if len(content["steps"]) >= 3 or len(content["result_lines"]) >= 2 else 0.0
    visual_h = max(1.72, min(2.55, float(layout.get("top_visual_h", 2.02)) - heavy * 0.65))
    lower_y = outer.y + visual_h + gap
    lower_h = max(1.20, outer.h - visual_h - gap)
    right_w = max(2.75, outer.w * right_share - col_gap * 0.5)
    left_w = max(3.25, outer.w - right_w - col_gap)
    right_x = outer.x + left_w + col_gap
    result_h = _card_height("\n".join(content["result_lines"]), max(0.1, right_w - 0.24), 12, 17, float(layout.get("result_min_h", 0.70)), float(layout.get("result_max_h", 1.18)), 5, 0.05)
    take_h = _card_height(content["takeaway"], max(0.1, right_w - 0.24), 11, 14, float(layout.get("takeaway_min_h", 0.58)), float(layout.get("takeaway_max_h", 1.00)), 4, 0.04)
    if result_h + take_h + (gap if result_h and take_h else 0.0) > lower_h:
        overflow = result_h + take_h + (gap if result_h and take_h else 0.0) - lower_h
        cut = min(overflow, max(0.0, take_h - float(layout.get("takeaway_floor_h", 0.40))))
        take_h -= cut
        overflow -= cut
        if overflow > 0:
            result_h -= min(overflow, max(0.0, result_h - float(layout.get("result_floor_h", 0.48))))
    return {
        "visual": Box(outer.x, outer.y, outer.w, visual_h),
        "explanation": None,
        "steps": Box(outer.x, lower_y, left_w, lower_h),
        "result": Box(right_x, lower_y, right_w, result_h) if result_h > 0 else None,
        "takeaway": Box(right_x, lower_y + result_h + (gap if result_h and take_h else 0.0), right_w, take_h) if take_h > 0 else None,
    }


def _boxes(layout: Mapping[str, Any], outer: Box, content: Mapping[str, Any]) -> dict[str, Box | None]:
    return _top_visual(layout, outer, content) if _clean(layout.get("worked_layout_mode")).lower() == "top_visual" else _two_column(layout, outer, content)


def _card(slide, box: Box, style: Mapping[str, Any]) -> None:
    add_rounded_box(slide, box.x, box.y, box.w, box.h, line_color=style["surface_line_color"], fill_color=style["surface_fill_color"], line_width_pt=style["surface_line_width_pt"])


def _text_card(slide, box: Box, label: str, text: str, style: Mapping[str, Any], color: RGBColor, min_font: int, max_font: int, max_lines: int | None, bold: bool = False) -> None:
    if box.w <= 0 or box.h <= 0 or not _clean(text):
        return
    _card(slide, box, style)
    add_box_title(slide, x=box.x + 0.10, y=box.y + 0.07, w=max(0.0, box.w - 0.20), text=label, color=style["label_color"], font_size=11)
    inner = Box(box.x + 0.12, box.y + 0.36, max(0.0, box.w - 0.24), max(0.0, box.h - 0.50))
    add_textbox(slide, x=inner.x, y=inner.y, w=inner.w, h=inner.h, text=text, font_name=BODY_FONT, font_size=_fit(text, inner, min_font, max_font, max_lines), color=color, bold=bold, align=PP_ALIGN.LEFT)


def _visual_card(slide, box: Box, content: Mapping[str, Any], style: Mapping[str, Any]) -> None:
    _card(slide, box, style)
    add_box_title(slide, x=box.x + 0.10, y=box.y + 0.07, w=max(0.0, box.w - 0.20), text=content["visual_label"], color=style["label_color"], font_size=11)
    caption_h = 0.0
    if content["visual_caption"]:
        caption_h = max(0.16, min(0.34, _estimate(content["visual_caption"], max(0.1, box.w - 0.24), 9, 11, 2)))
    img_box = Box(box.x + 0.08, box.y + 0.31, max(0.0, box.w - 0.16), max(0.0, box.h - 0.41 - caption_h))
    if content["mini_visual"]:
        add_mini_visual(slide, kind=content["mini_visual"], x=img_box.x, y=img_box.y, w=img_box.w, h=img_box.h, suffix="_worked_example_panel", variant=style["visual_variant"])
    if caption_h > 0:
        cap = Box(box.x + 0.10, img_box.y + img_box.h + 0.04, max(0.0, box.w - 0.20), caption_h)
        add_textbox(slide, x=cap.x, y=cap.y, w=cap.w, h=cap.h, text=content["visual_caption"], font_name=BODY_FONT, font_size=_fit(content["visual_caption"], cap, 9, 11, 2), color=style["body_color"], bold=False, align=PP_ALIGN.CENTER)


def _steps_card(slide, box: Box, content: Mapping[str, Any], style: Mapping[str, Any]) -> None:
    if box.w <= 0 or box.h <= 0 or not content["steps"]:
        return
    _card(slide, box, style)
    add_box_title(slide, x=box.x + 0.10, y=box.y + 0.07, w=max(0.0, box.w - 0.20), text=content["steps_label"], color=style["label_color"])
    inner = Box(box.x + 0.12, box.y + 0.34, max(0.0, box.w - 0.24), max(0.0, box.h - 0.48))
    render_compact_derivation_stack(slide, box=inner, steps=content["steps"], style=style["math"], min_body_font=10, max_body_font=13, min_formula_font=11, max_formula_font=14, final_answer="", emphasize_final_answer=False, align=PP_ALIGN.LEFT)


def build_worked_example_panel_slide(prs: Presentation, spec: dict[str, Any], counters: dict[str, int]) -> None:
    theme_name = spec.get("theme", "concept")
    theme_obj = get_theme(slide_theme_name=theme_name)
    slide = new_slide(prs, spec.get("background") or choose_background(theme_name, counters))
    style = _style(spec, theme_obj)
    content = _content(spec)
    layout = dict(spec.get("layout", {}) or {})
    header_result = render_header_from_spec(slide, spec, theme=theme_obj)
    boxes = _boxes(layout, _outer(layout, header_result), content)

    _visual_card(slide, boxes["visual"], content, style)
    if boxes["explanation"] and content["explanation"]:
        _text_card(slide, boxes["explanation"], content["explanation_label"], content["explanation"], style, style["body_color"], 12, 16, 4)
    if boxes["steps"]:
        _steps_card(slide, boxes["steps"], content, style)
    if boxes["result"] and content["result_lines"]:
        render_result_callout(slide, box=boxes["result"], result_lines=content["result_lines"], label=content["result_label"], style=style["math"], min_font=12, max_font=16, emphasize_final_answer=True, align=PP_ALIGN.LEFT, draw_card=True)
    if boxes["takeaway"] and content["takeaway"]:
        _text_card(slide, boxes["takeaway"], content["takeaway_label"], content["takeaway"], style, style["takeaway_color"], 11, 14, 4, bold=True)
    add_footer(slide, dark=style["footer_dark"], color=style["footer_color"])


__all__ = ["build_worked_example_panel_slide"]

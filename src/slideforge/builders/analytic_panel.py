from __future__ import annotations

from typing import Any, Mapping, Sequence

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, OFFWHITE
from slideforge.config.themes import get_theme, resolve_color
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, fit_text
from slideforge.layout.analytic_panel import AnalyticPanelLayoutResult, layout_analytic_panel
from slideforge.render.header import render_header_from_spec
from slideforge.render.math_blocks import MathBlockStyle, render_compact_derivation_stack, render_result_callout
from slideforge.render.primitives import add_box_title, add_footer, add_rounded_box, add_textbox


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _lines(items: Sequence[Any] | None) -> list[str]:
    return [_clean(item) for item in (items or []) if _clean(item)]


def _fit(text: str, box: Box, min_font: int, max_font: int, max_lines: int | None, *, line_spacing: float = 1.10) -> int:
    if not _clean(text) or box.w <= 0 or box.h <= 0:
        return max_font
    fitted = fit_text(
        text,
        box.w * 0.96,
        box.h * 0.90,
        min_font_size=min_font,
        max_font_size=max_font,
        max_lines=max_lines,
        line_spacing=line_spacing,
    )
    return max(min_font, fitted.font_size - 1)


def _estimate(text: str, width: float, min_font: int, max_font: int, max_lines: int | None, *, extra: float = 0.05) -> float:
    if not _clean(text) or width <= 0:
        return 0.0
    fitted = fit_text(text, width * 0.96, 10.0, min_font_size=min_font, max_font_size=max_font, max_lines=max_lines)
    return max(0.0, fitted.estimated_height + extra)


def _box_from(raw: Mapping[str, Any] | None, fallback: Box) -> Box:
    if not isinstance(raw, Mapping):
        return fallback
    return Box(float(raw.get("x", fallback.x)), float(raw.get("y", fallback.y)), float(raw.get("w", fallback.w)), float(raw.get("h", fallback.h)))


def _style(spec: Mapping[str, Any], theme_obj) -> dict[str, Any]:
    raw = dict(spec.get("worked_example_style", spec.get("analytic_panel_style", {})) or {})
    surface_fill = resolve_color(raw.get("surface_fill_color"), theme_obj.box_fill_color or theme_obj.panel_fill_color or OFFWHITE)
    surface_line = resolve_color(raw.get("surface_line_color"), theme_obj.box_line_color)
    style = {
        "surface_fill_color": surface_fill,
        "surface_line_color": surface_line,
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
        card_fill_color=surface_fill,
        card_line_color=surface_line,
        final_answer_fill_color=surface_fill,
    )
    return style


def _normalize_steps(raw_steps: Sequence[Any] | None, explanation: str) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    if explanation:
        out.append({"title": "Idea", "body": explanation, "formula": "", "note": ""})
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
    blocks: list[str] = []
    for step in steps:
        block = "\n".join(v for v in [step.get("title"), step.get("body"), step.get("formula"), step.get("note")] if _clean(v))
        if block:
            blocks.append(block)
    return "\n\n".join(blocks)


def _result(result_raw: Any, fallback: Sequence[Any] | None) -> tuple[str, list[str]]:
    if isinstance(result_raw, Mapping):
        return _clean(result_raw.get("label") or result_raw.get("title") or "Result"), _lines([
            result_raw.get("body") or result_raw.get("text") or result_raw.get("explanation"),
            result_raw.get("formula") or result_raw.get("equation"),
            result_raw.get("note"),
        ])
    return "Result", _lines([result_raw]) or _lines(fallback)


def _content(spec: Mapping[str, Any]) -> dict[str, Any]:
    explanation = _clean(spec.get("text_explanation") or spec.get("explanation"))
    result_label, result_lines = _result(spec.get("result"), spec.get("formulas"))
    raw_steps = list(spec.get("steps") or [])
    step_count = len(raw_steps)
    explanation_into_steps = explanation if step_count >= 3 else ""
    steps = _normalize_steps(raw_steps, explanation_into_steps)
    explanation_box_text = "" if explanation_into_steps else explanation
    return {
        "explanation": explanation_box_text,
        "steps": steps,
        "steps_text": _serialize_steps(steps),
        "result_label": result_label,
        "result_lines": result_lines,
        "result_text": "\n".join(result_lines),
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
        float(layout.get("content_x", 0.86)),
        float(layout.get("content_y", header_result.content_top_y + float(layout.get("content_gap_from_header", 0.12)))),
        float(layout.get("content_w", 11.30)),
        float(layout.get("content_h", 5.18)),
    )
    return _box_from(layout.get("content_box"), fallback)


def _card(slide, box: Box, style: Mapping[str, Any]) -> None:
    add_rounded_box(slide, box.x, box.y, box.w, box.h, line_color=style["surface_line_color"], fill_color=style["surface_fill_color"], line_width_pt=style["surface_line_width_pt"])


def _text_card(slide, box: Box, label: str, text: str, style: Mapping[str, Any], color, min_font: int, max_font: int, max_lines: int | None, *, bold: bool = False) -> None:
    if box.w <= 0 or box.h <= 0 or not _clean(text):
        return
    _card(slide, box, style)
    add_box_title(slide, x=box.x + 0.12, y=box.y + 0.06, w=max(0.0, box.w - 0.24), text=label, color=style["label_color"], font_size=11)
    inner = Box(box.x + 0.16, box.y + 0.34, max(0.0, box.w - 0.32), max(0.0, box.h - 0.50))
    add_textbox(slide, x=inner.x, y=inner.y, w=inner.w, h=inner.h, text=text, font_name=BODY_FONT, font_size=_fit(text, inner, min_font, max_font, max_lines), color=color, bold=bold, align=PP_ALIGN.LEFT)


def _visual_card(slide, box: Box, content: Mapping[str, Any], style: Mapping[str, Any], *, suppress_caption: bool = False) -> None:
    _card(slide, box, style)
    add_box_title(slide, x=box.x + 0.12, y=box.y + 0.06, w=max(0.0, box.w - 0.24), text=content["visual_label"], color=style["label_color"], font_size=11)
    caption_h = 0.0
    caption = "" if suppress_caption else content["visual_caption"]
    if caption:
        caption_h = max(0.18, min(0.34, _estimate(caption, max(0.1, box.w - 0.36), 9, 11, 2, extra=0.02)))
    img_box = Box(box.x + 0.16, box.y + 0.30, max(0.0, box.w - 0.32), max(0.0, box.h - 0.46 - caption_h))
    if content["mini_visual"]:
        add_mini_visual(slide, kind=content["mini_visual"], x=img_box.x, y=img_box.y, w=img_box.w, h=img_box.h, suffix="_analytic_panel", variant=style["visual_variant"])
    if caption_h > 0:
        cap = Box(box.x + 0.16, img_box.y + img_box.h + 0.03, max(0.0, box.w - 0.32), caption_h)
        add_textbox(slide, x=cap.x, y=cap.y, w=cap.w, h=cap.h, text=caption, font_name=BODY_FONT, font_size=_fit(caption, cap, 9, 11, 2), color=style["body_color"], align=PP_ALIGN.CENTER)


def _fallback_layout(outer: Box, content: Mapping[str, Any], layout: Mapping[str, Any], layout_result: AnalyticPanelLayoutResult) -> AnalyticPanelLayoutResult:
    if not layout_result.split_required and layout_result.score < 34.0:
        return layout_result
    return layout_analytic_panel(
        outer,
        explanation_text=content["explanation"],
        steps_text=content["steps_text"],
        result_text=content["result_text"],
        takeaway_text=content["takeaway"],
        layout_mode="two_column",
        visual_kind=content["mini_visual"],
        force_candidates=["two_column_text_heavy", "two_column", "two_column_requested"],
        top_pad=float(layout.get("top_pad", 0.16)),
        bottom_pad=float(layout.get("bottom_pad", 0.14)),
        side_pad=float(layout.get("side_pad", 0.20)),
        gap=float(layout.get("gap", 0.10)),
        col_gap=float(layout.get("col_gap", layout.get("column_gap", 0.20))),
        min_steps_h=float(layout.get("min_steps_h", 1.95)),
        explanation_min_h=float(layout.get("explanation_min_h", 0.34)),
        explanation_max_h=float(layout.get("explanation_max_h", 0.62)),
        result_min_h=float(layout.get("result_min_h", 0.72)),
        result_max_h=float(layout.get("result_max_h", 1.08)),
        takeaway_min_h=float(layout.get("takeaway_min_h", 0.50)),
        takeaway_max_h=float(layout.get("takeaway_max_h", 0.84)),
    )


def _density(content: Mapping[str, Any]) -> int:
    score = len(content["steps"]) * 2 + len(content["result_lines"]) + (1 if content["takeaway"] else 0) + (1 if content["explanation"] else 0)
    score += 1 if len(content["steps_text"]) > 260 else 0
    return score


def build_analytic_panel_slide(prs: Presentation, spec: dict[str, Any], counters: dict[str, int]) -> None:
    theme_name = spec.get("theme", "concept")
    theme_obj = get_theme(slide_theme_name=theme_name)
    slide = new_slide(prs, spec.get("background") or choose_background(theme_name, counters))
    style = _style(spec, theme_obj)
    content = _content(spec)
    layout = dict(spec.get("layout", {}) or {})
    header_result = render_header_from_spec(slide, spec, theme=theme_obj)

    requested_mode = _clean(layout.get("worked_layout_mode") or layout.get("layout_mode") or "two_column").lower() or "two_column"
    density = _density(content)
    layout.setdefault("top_pad", 0.16)
    layout.setdefault("bottom_pad", 0.14)
    layout.setdefault("side_pad", 0.20)
    layout.setdefault("gap", 0.10)
    layout.setdefault("col_gap", layout.get("column_gap", 0.20))
    layout.setdefault("min_steps_h", 2.0 if density >= 8 else 1.8)
    layout.setdefault("explanation_min_h", 0.34)
    layout.setdefault("explanation_max_h", 0.62)
    layout.setdefault("result_min_h", 0.72)
    layout.setdefault("result_max_h", 1.08)
    layout.setdefault("takeaway_min_h", 0.50)
    layout.setdefault("takeaway_max_h", 0.84)

    outer = _outer(layout, header_result)
    layout_result = layout_analytic_panel(
        outer,
        explanation_text=content["explanation"],
        steps_text=content["steps_text"],
        result_text=content["result_text"],
        takeaway_text=content["takeaway"],
        layout_mode=requested_mode,
        visual_kind=content["mini_visual"],
        top_pad=float(layout.get("top_pad", 0.16)),
        bottom_pad=float(layout.get("bottom_pad", 0.14)),
        side_pad=float(layout.get("side_pad", 0.20)),
        gap=float(layout.get("gap", 0.10)),
        col_gap=float(layout.get("col_gap", layout.get("column_gap", 0.20))),
        min_steps_h=float(layout.get("min_steps_h", 1.95)),
        explanation_min_h=float(layout.get("explanation_min_h", 0.34)),
        explanation_max_h=float(layout.get("explanation_max_h", 0.62)),
        result_min_h=float(layout.get("result_min_h", 0.72)),
        result_max_h=float(layout.get("result_max_h", 1.08)),
        takeaway_min_h=float(layout.get("takeaway_min_h", 0.50)),
        takeaway_max_h=float(layout.get("takeaway_max_h", 0.84)),
    )
    layout_result = _fallback_layout(outer, content, layout, layout_result)

    suppress_caption = layout_result.diagram_box.h < 1.45 or layout_result.candidate_name.startswith("top_visual")
    _visual_card(slide, layout_result.diagram_box, content, style, suppress_caption=suppress_caption)

    if layout_result.explanation_box.h > 0 and content["explanation"]:
        _text_card(slide, layout_result.explanation_box, content["explanation_label"], content["explanation"], style, style["body_color"], 11, 14, 4)

    if layout_result.steps_box.h > 0 and content["steps"]:
        _card(slide, layout_result.steps_box, style)
        add_box_title(slide, x=layout_result.steps_box.x + 0.12, y=layout_result.steps_box.y + 0.06, w=max(0.0, layout_result.steps_box.w - 0.24), text=content["steps_label"], color=style["label_color"], font_size=11)
        inner = Box(layout_result.steps_box.x + 0.16, layout_result.steps_box.y + 0.34, max(0.0, layout_result.steps_box.w - 0.32), max(0.0, layout_result.steps_box.h - 0.52))
        render_compact_derivation_stack(
            slide,
            box=inner,
            steps=content["steps"],
            style=style["math"],
            min_body_font=10,
            max_body_font=12,
            min_formula_font=11,
            max_formula_font=13,
            final_answer="",
            emphasize_final_answer=False,
            align=PP_ALIGN.LEFT,
        )

    if layout_result.result_box.h > 0 and content["result_lines"]:
        render_result_callout(
            slide,
            box=layout_result.result_box,
            result_lines=content["result_lines"],
            label=content["result_label"],
            style=style["math"],
            min_font=11,
            max_font=15,
            emphasize_final_answer=True,
            align=PP_ALIGN.LEFT,
            draw_card=True,
        )

    if layout_result.takeaway_box.h > 0 and content["takeaway"]:
        _text_card(slide, layout_result.takeaway_box, content["takeaway_label"], content["takeaway"], style, style["takeaway_color"], 10, 13, 4, bold=True)

    add_footer(slide, dark=style["footer_dark"], color=style["footer_color"])


__all__ = ["build_analytic_panel_slide"]

from __future__ import annotations

from typing import Any, Mapping

from pptx import Presentation
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, OFFWHITE
from slideforge.config.themes import SlideTheme, get_theme, resolve_color
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, fit_text
from slideforge.render.header import render_header_from_spec
from slideforge.render.primitives import add_footer, add_rounded_box, add_textbox


# -----------------------------------------------------------------------------
# Basic helpers
# -----------------------------------------------------------------------------


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _clean_lines(items: list[Any] | tuple[Any, ...] | None) -> list[str]:
    return [_clean_text(item) for item in (items or []) if _clean_text(item)]


def _join_lines(items: list[Any] | tuple[Any, ...] | None, *, separator: str = "\n") -> str:
    return separator.join(_clean_lines(items))


def _box_from_dict(raw: Mapping[str, Any], fallback: Box) -> Box:
    return Box(
        raw.get("x", fallback.x),
        raw.get("y", fallback.y),
        raw.get("w", fallback.w),
        raw.get("h", fallback.h),
    )


def _estimate_text_height(
    text: str,
    *,
    width: float,
    min_font: int,
    max_font: int,
    max_lines: int | None,
    line_spacing: float = 1.12,
    prefer_single_line: bool = False,
    extra_pad: float = 0.05,
) -> float:
    text = _clean_text(text)
    if not text or width <= 0:
        return 0.0
    fitted = fit_text(
        text,
        width,
        10.0,
        min_font_size=min_font,
        max_font_size=max_font,
        max_lines=max_lines,
        line_spacing=line_spacing,
        prefer_single_line=prefer_single_line,
    )
    return max(0.0, fitted.estimated_height + extra_pad)


def _fit_font_size(
    text: str,
    box: Box,
    *,
    min_font: int,
    max_font: int,
    max_lines: int | None = None,
    line_spacing: float = 1.12,
    prefer_single_line: bool = False,
) -> int:
    text = _clean_text(text)
    if not text or box.w <= 0 or box.h <= 0:
        return max_font
    fitted = fit_text(
        text,
        box.w,
        box.h,
        min_font_size=min_font,
        max_font_size=max_font,
        max_lines=max_lines,
        line_spacing=line_spacing,
        prefer_single_line=prefer_single_line,
    )
    return max(min_font, fitted.font_size)


def _add_fitted_text(
    slide,
    *,
    box: Box,
    text: str,
    font_name: str,
    color,
    min_font: int,
    max_font: int,
    max_lines: int | None = None,
    line_spacing: float = 1.12,
    bold: bool = False,
    align=PP_ALIGN.LEFT,
    prefer_single_line: bool = False,
) -> None:
    text = _clean_text(text)
    if not text or box.w <= 0 or box.h <= 0:
        return
    font_size = _fit_font_size(
        text,
        box,
        min_font=min_font,
        max_font=max_font,
        max_lines=max_lines,
        line_spacing=line_spacing,
        prefer_single_line=prefer_single_line,
    )
    add_textbox(
        slide,
        x=box.x,
        y=box.y,
        w=box.w,
        h=box.h,
        text=text,
        font_name=font_name,
        font_size=font_size,
        color=color,
        bold=bold,
        align=align,
    )


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


# -----------------------------------------------------------------------------
# Step normalization
# -----------------------------------------------------------------------------


def _normalize_step(step: Any, index: int) -> dict[str, str]:
    if isinstance(step, Mapping):
        title = _clean_text(step.get("title") or step.get("label") or f"Step {index}")
        body = _clean_text(step.get("body") or step.get("text") or step.get("explanation"))
        formula = _clean_text(step.get("formula") or step.get("equation") or step.get("result"))
        note = _clean_text(step.get("note"))
    else:
        title = f"Step {index}"
        body = _clean_text(step)
        formula = ""
        note = ""
    return {"title": title, "body": body, "formula": formula, "note": note}


def _normalize_steps(steps_raw: list[Any] | None) -> list[dict[str, str]]:
    return [_normalize_step(step, idx + 1) for idx, step in enumerate(steps_raw or [])]


def _normalize_result(result_raw: Any, fallback_formula_lines: list[str]) -> tuple[str, str]:
    if isinstance(result_raw, Mapping):
        label = _clean_text(result_raw.get("label") or result_raw.get("title") or "Result")
        parts = [
            _clean_text(result_raw.get("body") or result_raw.get("text") or result_raw.get("explanation")),
            _clean_text(result_raw.get("formula") or result_raw.get("equation")),
            _clean_text(result_raw.get("note")),
        ]
        text = _join_lines(parts)
    else:
        label = "Result"
        text = _clean_text(result_raw) or _join_lines(fallback_formula_lines)
    return label, text


def _serialize_steps_for_fit(steps: list[dict[str, str]]) -> str:
    blocks: list[str] = []
    for step in steps:
        block = _join_lines([
            step.get("title"),
            step.get("body"),
            step.get("formula"),
            step.get("note"),
        ])
        if block:
            blocks.append(block)
    return "\n\n".join(blocks)


# -----------------------------------------------------------------------------
# Style
# -----------------------------------------------------------------------------


def _resolve_worked_example_style(
    spec: Mapping[str, Any],
    *,
    theme_obj: SlideTheme,
) -> dict[str, Any]:
    worked_style = dict(spec.get("worked_example_style", {}) or {})

    card_fill_default = theme_obj.box_fill_color
    if card_fill_default is None:
        card_fill_default = theme_obj.panel_fill_color
    if card_fill_default is None:
        card_fill_default = OFFWHITE

    return {
        "surface_fill_color": resolve_color(worked_style.get("surface_fill_color"), card_fill_default),
        "surface_line_color": resolve_color(worked_style.get("surface_line_color"), theme_obj.box_line_color),
        "surface_line_width_pt": float(worked_style.get("surface_line_width_pt", 1.2)),
        "label_color": resolve_color(worked_style.get("label_color"), theme_obj.box_title_color),
        "body_color": resolve_color(worked_style.get("body_color"), theme_obj.subtitle_color),
        "formula_color": resolve_color(worked_style.get("formula_color"), theme_obj.body_color),
        "result_color": resolve_color(worked_style.get("result_color"), theme_obj.body_color),
        "takeaway_color": resolve_color(worked_style.get("takeaway_color"), theme_obj.subtitle_color),
        "footer_color": resolve_color(worked_style.get("footer_color"), theme_obj.footer_color),
        "footer_dark": bool(worked_style.get("footer_dark", theme_obj.footer_dark)),
        "visual_variant": str(worked_style.get("visual_variant", theme_obj.panel_visual_variant)),
    }


# -----------------------------------------------------------------------------
# Cards
# -----------------------------------------------------------------------------


def _draw_card_label(
    slide,
    *,
    box: Box,
    text: str,
    color,
    min_font: int = 10,
    max_font: int = 12,
) -> float:
    text = _clean_text(text)
    if not text:
        return 0.0
    label_h = max(
        0.17,
        min(
            0.28,
            _estimate_text_height(
                text,
                width=max(0.1, box.w - 0.16),
                min_font=min_font,
                max_font=max_font,
                max_lines=2,
                extra_pad=0.01,
            ),
        ),
    )
    _add_fitted_text(
        slide,
        box=Box(box.x + 0.09, box.y + 0.045, max(0.0, box.w - 0.18), label_h),
        text=text,
        font_name=BODY_FONT,
        color=color,
        min_font=min_font,
        max_font=max_font,
        max_lines=2,
        bold=True,
        align=PP_ALIGN.LEFT,
    )
    return label_h


def _draw_text_card(
    slide,
    *,
    box: Box,
    label: str,
    text: str,
    style: Mapping[str, Any],
    font_name: str,
    color,
    min_font: int,
    max_font: int,
    max_lines: int | None,
    line_spacing: float = 1.12,
    bold: bool = False,
) -> None:
    if box.w <= 0 or box.h <= 0:
        return
    add_rounded_box(
        slide,
        box.x,
        box.y,
        box.w,
        box.h,
        line_color=style["surface_line_color"],
        fill_color=style["surface_fill_color"],
        line_width_pt=style["surface_line_width_pt"],
    )
    label_h = _draw_card_label(slide, box=box, text=label, color=style["label_color"])
    inner = Box(
        box.x + 0.10,
        box.y + 0.06 + label_h,
        max(0.0, box.w - 0.20),
        max(0.0, box.h - label_h - 0.12),
    )
    _add_fitted_text(
        slide,
        box=inner,
        text=text,
        font_name=font_name,
        color=color,
        min_font=min_font,
        max_font=max_font,
        max_lines=max_lines,
        line_spacing=line_spacing,
        bold=bold,
        align=PP_ALIGN.LEFT,
    )


# -----------------------------------------------------------------------------
# Steps card: render as one adaptive text frame to avoid clipping
# -----------------------------------------------------------------------------


def _steps_base_font(steps: list[dict[str, str]], box: Box) -> int:
    text = _serialize_steps_for_fit(steps)
    if not text or box.w <= 0 or box.h <= 0:
        return 12
    working_box = Box(box.x, box.y, max(0.1, box.w), max(0.1, box.h))
    return _fit_font_size(
        text,
        working_box,
        min_font=10,
        max_font=13,
        max_lines=None,
        line_spacing=1.08,
    )


def _add_text_frame(slide, *, box: Box):
    shape = slide.shapes.add_textbox(Inches(box.x), Inches(box.y), Inches(box.w), Inches(box.h))
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Inches(0.0)
    tf.margin_right = Inches(0.0)
    tf.margin_top = Inches(0.0)
    tf.margin_bottom = Inches(0.0)
    return tf


def _set_run_font(run, *, font_name: str, font_size: int, color, bold: bool = False):
    font = run.font
    font.name = font_name
    font.size = Pt(font_size)
    font.bold = bold
    if color is not None:
        font.color.rgb = color


def _add_paragraph(tf, *, text: str, font_name: str, font_size: int, color, bold: bool = False, first: bool = False, space_after_pt: int = 1):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = PP_ALIGN.LEFT
    p.line_spacing = 1.05
    p.space_after = Pt(space_after_pt)
    run = p.add_run()
    run.text = text
    _set_run_font(run, font_name=font_name, font_size=font_size, color=color, bold=bold)
    return p


def _draw_steps_card(
    slide,
    *,
    box: Box,
    label: str,
    steps: list[dict[str, str]],
    style: Mapping[str, Any],
) -> None:
    if box.w <= 0 or box.h <= 0:
        return
    add_rounded_box(
        slide,
        box.x,
        box.y,
        box.w,
        box.h,
        line_color=style["surface_line_color"],
        fill_color=style["surface_fill_color"],
        line_width_pt=style["surface_line_width_pt"],
    )
    label_h = _draw_card_label(slide, box=box, text=label, color=style["label_color"])

    inner = Box(
        box.x + 0.10,
        box.y + 0.06 + label_h,
        max(0.0, box.w - 0.20),
        max(0.0, box.h - label_h - 0.12),
    )
    if not steps or inner.w <= 0 or inner.h <= 0:
        return

    base_font = _steps_base_font(steps, inner)
    title_font = min(13, max(10, base_font + 1))
    body_font = max(10, base_font)
    formula_font = min(14, max(10, base_font + 1))
    note_font = max(10, base_font - 1)

    tf = _add_text_frame(slide, box=inner)
    first = True
    for idx, step in enumerate(steps):
        title = _clean_text(step.get("title"))
        body = _clean_text(step.get("body"))
        formula = _clean_text(step.get("formula"))
        note = _clean_text(step.get("note"))

        if title:
            _add_paragraph(
                tf,
                text=title,
                font_name=BODY_FONT,
                font_size=title_font,
                color=style["body_color"],
                bold=True,
                first=first,
                space_after_pt=1,
            )
            first = False
        if body:
            _add_paragraph(
                tf,
                text=body,
                font_name=BODY_FONT,
                font_size=body_font,
                color=style["body_color"],
                first=first,
                space_after_pt=1,
            )
            first = False
        if formula:
            _add_paragraph(
                tf,
                text=formula,
                font_name=FORMULA_FONT,
                font_size=formula_font,
                color=style["formula_color"],
                first=first,
                space_after_pt=1,
            )
            first = False
        if note:
            _add_paragraph(
                tf,
                text=note,
                font_name=BODY_FONT,
                font_size=note_font,
                color=style["body_color"],
                first=first,
                space_after_pt=1,
            )
            first = False
        if idx < len(steps) - 1:
            spacer = tf.add_paragraph()
            spacer.space_after = Pt(1)
            spacer.line_spacing = 0.95
            run = spacer.add_run()
            run.text = ""


# -----------------------------------------------------------------------------
# Layout
# -----------------------------------------------------------------------------


def _estimate_card_target_height(
    text: str,
    *,
    inner_width: float,
    min_font: int,
    max_font: int,
    min_h: float,
    max_h: float,
    max_lines: int | None,
    extra_pad: float,
) -> float:
    text = _clean_text(text)
    if not text:
        return 0.0
    h = _estimate_text_height(
        text,
        width=inner_width,
        min_font=min_font,
        max_font=max_font,
        max_lines=max_lines,
        extra_pad=extra_pad,
    ) + 0.14
    return _clamp(h, min_h, max_h)


def _candidate_visual_shares(layout: Mapping[str, Any]) -> list[float]:
    preferred = float(layout.get("visual_share", layout.get("visual_preferred_share", 0.34)))
    minimum = float(layout.get("visual_min_share", 0.28))
    maximum = float(layout.get("visual_max_share", 0.42))
    preferred = _clamp(preferred, minimum, maximum)

    shares: list[float] = []
    for raw in [preferred, preferred - 0.03, preferred - 0.06, preferred + 0.03, minimum, maximum]:
        value = round(_clamp(raw, minimum, maximum), 3)
        if value not in shares:
            shares.append(value)
    return shares


def _compute_two_column_layout(
    *,
    outer: Box,
    layout: Mapping[str, Any],
    explanation_text: str,
    steps: list[dict[str, str]],
    result_text: str,
    takeaway_text: str,
) -> dict[str, Box]:
    col_gap = float(layout.get("column_gap", 0.18))
    block_gap = float(layout.get("block_gap", 0.10))
    steps_min_h = float(layout.get("steps_min_h", 1.65))

    best: dict[str, Any] | None = None
    steps_text = _serialize_steps_for_fit(steps)

    for visual_share in _candidate_visual_shares(layout):
        visual_w = max(2.10, outer.w * visual_share - col_gap * 0.5)
        right_w = max(3.20, outer.w - visual_w - col_gap)
        inner_w = max(0.1, right_w - 0.20)

        explanation_h = _estimate_card_target_height(
            explanation_text,
            inner_width=inner_w,
            min_font=12,
            max_font=16,
            min_h=float(layout.get("explanation_min_h", 0.42)),
            max_h=float(layout.get("explanation_max_h", 0.78)),
            max_lines=4,
            extra_pad=0.05,
        )
        result_h = _estimate_card_target_height(
            result_text,
            inner_width=inner_w,
            min_font=12,
            max_font=16,
            min_h=float(layout.get("result_min_h", 0.48)),
            max_h=float(layout.get("result_max_h", 0.86)),
            max_lines=5,
            extra_pad=0.06,
        )
        takeaway_h = _estimate_card_target_height(
            takeaway_text,
            inner_width=inner_w,
            min_font=11,
            max_font=14,
            min_h=float(layout.get("takeaway_min_h", 0.40)),
            max_h=float(layout.get("takeaway_max_h", 0.70)),
            max_lines=4,
            extra_pad=0.05,
        )

        consumed = 0.0
        gaps = 0
        for h in [explanation_h, result_h, takeaway_h]:
            if h > 0:
                consumed += h
                gaps += 1
        if explanation_h > 0 and steps_text:
            consumed += block_gap
        if result_h > 0 and takeaway_h > 0:
            consumed += block_gap
        elif steps_text and (result_h > 0 or takeaway_h > 0):
            consumed += block_gap

        steps_available = max(0.0, outer.h - consumed)
        steps_demand = _estimate_text_height(
            steps_text,
            width=max(0.1, inner_w),
            min_font=10,
            max_font=13,
            max_lines=None,
            line_spacing=1.08,
            extra_pad=0.10,
        ) + 0.18

        shortage = max(0.0, max(steps_min_h, min(steps_demand, outer.h)) - steps_available)
        width_bonus_penalty = max(0.0, 3.55 - right_w) * 0.35
        score = shortage + width_bonus_penalty + abs(visual_share - float(layout.get("visual_share", 0.34))) * 0.08

        candidate = {
            "score": score,
            "visual_share": visual_share,
            "visual_w": visual_w,
            "right_w": right_w,
            "explanation_h": explanation_h,
            "result_h": result_h,
            "takeaway_h": takeaway_h,
            "steps_available": steps_available,
        }
        if best is None or candidate["score"] < best["score"]:
            best = candidate

    assert best is not None

    visual_w = best["visual_w"]
    right_w = best["right_w"]
    right_x = outer.x + visual_w + col_gap

    explanation_h = best["explanation_h"]
    result_h = best["result_h"]
    takeaway_h = best["takeaway_h"]

    # If steps are still tight, sacrifice result/takeaway height before shrinking steps.
    remaining = outer.h - explanation_h - result_h - takeaway_h
    if explanation_h > 0:
        remaining -= block_gap
    if result_h > 0 and takeaway_h > 0:
        remaining -= block_gap
    elif (result_h > 0 or takeaway_h > 0) and steps:
        remaining -= block_gap

    if remaining < steps_min_h:
        deficit = steps_min_h - remaining
        take_cut = min(deficit, max(0.0, takeaway_h - float(layout.get("takeaway_floor_h", 0.34))))
        takeaway_h -= take_cut
        deficit -= take_cut
        if deficit > 0:
            result_cut = min(deficit, max(0.0, result_h - float(layout.get("result_floor_h", 0.42))))
            result_h -= result_cut
            deficit -= result_cut
        if deficit > 0 and explanation_h > 0:
            expl_cut = min(deficit, max(0.0, explanation_h - float(layout.get("explanation_floor_h", 0.38))))
            explanation_h -= expl_cut

    y = outer.y
    explanation_box = Box(right_x, y, right_w, explanation_h) if explanation_h > 0 else None
    if explanation_box is not None:
        y += explanation_h + block_gap

    bottom_reserved = 0.0
    if result_h > 0:
        bottom_reserved += result_h
    if takeaway_h > 0:
        bottom_reserved += takeaway_h
    if result_h > 0 and takeaway_h > 0:
        bottom_reserved += block_gap

    steps_h = max(0.0, outer.y + outer.h - y - bottom_reserved)
    steps_box = Box(right_x, y, right_w, steps_h)
    y = steps_box.y + steps_box.h

    if result_h > 0 or takeaway_h > 0:
        y += block_gap
    result_box = Box(right_x, y, right_w, result_h) if result_h > 0 else None
    if result_box is not None:
        y += result_h
    if takeaway_h > 0 and result_box is not None:
        y += block_gap
    takeaway_box = Box(right_x, y, right_w, takeaway_h) if takeaway_h > 0 else None

    # Make the visual card less oversized by default.
    visual_height_share = float(layout.get("two_column_visual_height_share", 0.86))
    visual_height_share = _clamp(visual_height_share, 0.72, 1.0)
    visual_h = min(outer.h, max(2.45, outer.h * visual_height_share))
    visual_y = outer.y + float(layout.get("two_column_visual_y_offset", 0.02))
    if visual_y + visual_h > outer.y + outer.h:
        visual_h = outer.y + outer.h - visual_y
    visual_box = Box(outer.x, visual_y, visual_w, max(0.0, visual_h))

    return {
        "visual_box": visual_box,
        "explanation_box": explanation_box,
        "steps_box": steps_box,
        "result_box": result_box,
        "takeaway_box": takeaway_box,
    }


def _compute_top_visual_layout(
    *,
    outer: Box,
    layout: Mapping[str, Any],
    explanation_text: str,
    steps: list[dict[str, str]],
    result_text: str,
    takeaway_text: str,
) -> dict[str, Box]:
    block_gap = float(layout.get("block_gap", 0.10))
    lower_gap = float(layout.get("column_gap", 0.18))
    lower_right_share = _clamp(float(layout.get("lower_right_share", 0.33)), 0.26, 0.42)

    # Shrink the top visual when text is heavy.
    step_count = len(steps)
    heavy = 1.0 if step_count >= 3 or len(_clean_text(result_text)) > 60 else 0.0
    visual_h = float(layout.get("top_visual_h", 2.10)) - heavy * 0.22
    visual_h = _clamp(visual_h, 1.55, 2.45)
    if explanation_text:
        visual_h = max(1.55, visual_h - 0.08)

    lower_y = outer.y + visual_h + block_gap
    lower_h = max(1.30, outer.h - visual_h - block_gap)

    right_w = outer.w * lower_right_share - lower_gap * 0.5
    left_w = outer.w - right_w - lower_gap
    right_x = outer.x + left_w + lower_gap

    result_h = _estimate_card_target_height(
        result_text,
        inner_width=max(0.1, right_w - 0.20),
        min_font=12,
        max_font=16,
        min_h=float(layout.get("result_min_h", 0.46)),
        max_h=float(layout.get("result_max_h", 0.82)),
        max_lines=5,
        extra_pad=0.06,
    )
    takeaway_h = _estimate_card_target_height(
        takeaway_text,
        inner_width=max(0.1, right_w - 0.20),
        min_font=11,
        max_font=14,
        min_h=float(layout.get("takeaway_min_h", 0.38)),
        max_h=float(layout.get("takeaway_max_h", 0.68)),
        max_lines=4,
        extra_pad=0.05,
    )

    if result_h + takeaway_h + (block_gap if result_h and takeaway_h else 0.0) > lower_h:
        overflow = result_h + takeaway_h + (block_gap if result_h and takeaway_h else 0.0) - lower_h
        takeaway_cut = min(overflow, max(0.0, takeaway_h - 0.34))
        takeaway_h -= takeaway_cut
        overflow -= takeaway_cut
        if overflow > 0:
            result_h -= min(overflow, max(0.0, result_h - 0.42))

    return {
        "visual_box": Box(outer.x, outer.y, outer.w, visual_h),
        "explanation_box": None,
        "steps_box": Box(outer.x, lower_y, left_w, lower_h),
        "result_box": Box(right_x, lower_y, right_w, result_h) if result_h > 0 else None,
        "takeaway_box": Box(
            right_x,
            lower_y + result_h + (block_gap if result_h > 0 and takeaway_h > 0 else 0.0),
            right_w,
            max(0.0, lower_h - result_h - (block_gap if result_h > 0 and takeaway_h > 0 else 0.0)),
        ) if takeaway_text else None,
    }


# -----------------------------------------------------------------------------
# Builder
# -----------------------------------------------------------------------------


def build_worked_example_panel_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    """
    Builder for step-by-step math/example slides.

    Improvements over the initial draft:
      - right-column layout is content-driven, not box-first
      - steps are given flexible priority height
      - visual column shrinks when text demand is high
      - steps render in one adaptive text frame to prevent clipping
      - result / takeaway shrink before steps are starved
    """
    slide_theme_name = spec.get("theme", "concept")
    theme_obj = get_theme(slide_theme_name=slide_theme_name)

    bg = spec.get("background") or choose_background(slide_theme_name, counters)
    slide = new_slide(prs, bg)

    layout = dict(spec.get("layout", {}) or {})
    style = _resolve_worked_example_style(spec, theme_obj=theme_obj)

    explanation_text = _clean_text(spec.get("text_explanation") or spec.get("explanation"))
    mini_visual = _clean_text(spec.get("mini_visual"))
    visual_caption = _clean_text(spec.get("visual_caption"))
    steps = _normalize_steps(list(spec.get("steps", []) or []))
    fallback_formula_lines = _clean_lines(list(spec.get("formulas", []) or []))
    result_label, result_text = _normalize_result(spec.get("result"), fallback_formula_lines)
    takeaway_text = _clean_text(spec.get("takeaway"))

    header_result = render_header_from_spec(slide, spec, theme=theme_obj)

    fallback_outer = Box(
        float(layout.get("content_x", 0.88)),
        float(layout.get("content_y", header_result.content_top_y + float(layout.get("content_gap_from_header", 0.12)))),
        float(layout.get("content_w", 11.24)),
        float(layout.get("content_h", 5.12)),
    )
    outer_raw = layout.get("content_box")
    outer = _box_from_dict(outer_raw, fallback_outer) if isinstance(outer_raw, Mapping) else fallback_outer

    worked_layout_mode = str(layout.get("worked_layout_mode", spec.get("worked_layout_mode", "two_column"))).strip().lower()
    if worked_layout_mode == "top_visual":
        boxes = _compute_top_visual_layout(
            outer=outer,
            layout=layout,
            explanation_text=explanation_text,
            steps=steps,
            result_text=result_text,
            takeaway_text=takeaway_text,
        )
    else:
        boxes = _compute_two_column_layout(
            outer=outer,
            layout=layout,
            explanation_text=explanation_text,
            steps=steps,
            result_text=result_text,
            takeaway_text=takeaway_text,
        )

    visual_box = boxes["visual_box"]
    add_rounded_box(
        slide,
        visual_box.x,
        visual_box.y,
        visual_box.w,
        visual_box.h,
        line_color=style["surface_line_color"],
        fill_color=style["surface_fill_color"],
        line_width_pt=style["surface_line_width_pt"],
    )
    visual_label_h = _draw_card_label(
        slide,
        box=visual_box,
        text=_clean_text(spec.get("visual_label") or "Geometry"),
        color=style["label_color"],
    )
    visual_inner = Box(
        visual_box.x + 0.10,
        visual_box.y + 0.06 + visual_label_h,
        max(0.0, visual_box.w - 0.20),
        max(0.0, visual_box.h - visual_label_h - 0.12),
    )

    if visual_caption:
        caption_h = _clamp(
            _estimate_text_height(
                visual_caption,
                width=visual_inner.w,
                min_font=9,
                max_font=11,
                max_lines=2,
                extra_pad=0.01,
            ),
            0.16,
            0.30,
        )
        visual_image_box = Box(
            visual_inner.x,
            visual_inner.y,
            visual_inner.w,
            max(0.0, visual_inner.h - caption_h - 0.03),
        )
        caption_box = Box(
            visual_inner.x,
            visual_image_box.y + visual_image_box.h + 0.03,
            visual_inner.w,
            caption_h,
        )
    else:
        visual_image_box = visual_inner
        caption_box = None

    if mini_visual:
        add_mini_visual(
            slide,
            kind=mini_visual,
            x=visual_image_box.x,
            y=visual_image_box.y,
            w=visual_image_box.w,
            h=visual_image_box.h,
            suffix="_worked_example_panel",
            variant=style["visual_variant"],
        )
    if caption_box is not None:
        _add_fitted_text(
            slide,
            box=caption_box,
            text=visual_caption,
            font_name=BODY_FONT,
            color=style["body_color"],
            min_font=9,
            max_font=11,
            max_lines=2,
            align=PP_ALIGN.CENTER,
        )

    explanation_box = boxes.get("explanation_box")
    if isinstance(explanation_box, Box) and explanation_text:
        _draw_text_card(
            slide,
            box=explanation_box,
            label=_clean_text(spec.get("explanation_label") or "Idea"),
            text=explanation_text,
            style=style,
            font_name=BODY_FONT,
            color=style["body_color"],
            min_font=12,
            max_font=16,
            max_lines=4,
        )

    steps_box = boxes.get("steps_box")
    if isinstance(steps_box, Box):
        _draw_steps_card(
            slide,
            box=steps_box,
            label=_clean_text(spec.get("steps_label") or "Steps"),
            steps=steps,
            style=style,
        )

    result_box = boxes.get("result_box")
    if isinstance(result_box, Box) and result_text:
        _draw_text_card(
            slide,
            box=result_box,
            label=result_label,
            text=result_text,
            style=style,
            font_name=FORMULA_FONT,
            color=style["result_color"],
            min_font=12,
            max_font=17,
            max_lines=5,
            line_spacing=1.08,
            bold=False,
        )

    takeaway_box = boxes.get("takeaway_box")
    if isinstance(takeaway_box, Box) and takeaway_text:
        _draw_text_card(
            slide,
            box=takeaway_box,
            label=_clean_text(spec.get("takeaway_label") or "Takeaway"),
            text=takeaway_text,
            style=style,
            font_name=BODY_FONT,
            color=style["takeaway_color"],
            min_font=11,
            max_font=14,
            max_lines=4,
            bold=True,
        )

    add_footer(slide, dark=style["footer_dark"], color=style["footer_color"])

from __future__ import annotations

from typing import Any, Mapping

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, OFFWHITE
from slideforge.config.themes import SlideTheme, get_theme, resolve_color
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, fit_text
from slideforge.render.header import render_header_from_spec
from slideforge.render.primitives import add_footer, add_rounded_box, add_textbox


# -----------------------------------------------------------------------------
# Small utilities
# -----------------------------------------------------------------------------


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _clean_lines(items: list[Any]) -> list[str]:
    return [_clean_text(item) for item in items if _clean_text(item)]


def _join_lines(items: list[Any], *, separator: str = "\n") -> str:
    return separator.join(_clean_lines(items))


def _box_from_dict(raw: Mapping[str, Any], fallback: Box) -> Box:
    return Box(
        raw.get("x", fallback.x),
        raw.get("y", fallback.y),
        raw.get("w", fallback.w),
        raw.get("h", fallback.h),
    )


def _fit_font_size(
    text: str,
    box: Box,
    *,
    min_font: int,
    max_font: int,
    max_lines: int | None = None,
    prefer_single_line: bool = False,
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
        prefer_single_line=prefer_single_line,
    )
    return max(min_font, fitted.font_size)


def _estimate_text_height(
    text: str,
    *,
    width: float,
    min_font: int,
    max_font: int,
    max_lines: int | None,
    extra_pad: float = 0.05,
) -> float:
    if not text.strip() or width <= 0:
        return 0.0

    fitted = fit_text(
        text,
        width,
        10.0,
        min_font_size=min_font,
        max_font_size=max_font,
        max_lines=max_lines,
        prefer_single_line=False,
    )
    return max(0.16, fitted.estimated_height + extra_pad)


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
    bold: bool = False,
    align=PP_ALIGN.LEFT,
    prefer_single_line: bool = False,
) -> None:
    if not text.strip() or box.w <= 0 or box.h <= 0:
        return

    font_size = _fit_font_size(
        text,
        box,
        min_font=min_font,
        max_font=max_font,
        max_lines=max_lines,
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


# -----------------------------------------------------------------------------
# Spec normalization
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

    return {
        "title": title,
        "body": body,
        "formula": formula,
        "note": note,
    }


def _normalize_steps(steps_raw: list[Any]) -> list[dict[str, str]]:
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
        raw_text = _clean_text(result_raw)
        text = raw_text or _join_lines(fallback_formula_lines)

    return label, text


# -----------------------------------------------------------------------------
# Style / cards
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
        "surface_fill_color": resolve_color(
            worked_style.get("surface_fill_color"),
            card_fill_default,
        ),
        "surface_line_color": resolve_color(
            worked_style.get("surface_line_color"),
            theme_obj.box_line_color,
        ),
        "surface_line_width_pt": float(
            worked_style.get("surface_line_width_pt", 1.25)
        ),
        "label_color": resolve_color(
            worked_style.get("label_color"),
            theme_obj.box_title_color,
        ),
        "body_color": resolve_color(
            worked_style.get("body_color"),
            theme_obj.subtitle_color,
        ),
        "formula_color": resolve_color(
            worked_style.get("formula_color"),
            theme_obj.body_color,
        ),
        "result_color": resolve_color(
            worked_style.get("result_color"),
            theme_obj.body_color,
        ),
        "takeaway_color": resolve_color(
            worked_style.get("takeaway_color"),
            theme_obj.subtitle_color,
        ),
        "footer_color": resolve_color(
            worked_style.get("footer_color"),
            theme_obj.footer_color,
        ),
        "footer_dark": bool(
            worked_style.get("footer_dark", theme_obj.footer_dark)
        ),
        "visual_variant": str(
            worked_style.get("visual_variant", theme_obj.panel_visual_variant)
        ),
    }


def _draw_card_label(
    slide,
    *,
    box: Box,
    text: str,
    color,
    min_font: int = 11,
    max_font: int = 12,
) -> float:
    label_h = max(
        0.18,
        min(
            0.32,
            _estimate_text_height(
                text,
                width=max(0.1, box.w - 0.18),
                min_font=min_font,
                max_font=max_font,
                max_lines=2,
                extra_pad=0.02,
            ),
        ),
    )
    _add_fitted_text(
        slide,
        box=Box(box.x + 0.10, box.y + 0.06, max(0.0, box.w - 0.20), label_h),
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


def _draw_single_text_card(
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
    bold: bool = False,
) -> None:
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
    label_h = _draw_card_label(
        slide,
        box=box,
        text=label,
        color=style["label_color"],
    )
    body_box = Box(
        box.x + 0.12,
        box.y + 0.08 + label_h,
        max(0.0, box.w - 0.24),
        max(0.0, box.h - label_h - 0.16),
    )
    _add_fitted_text(
        slide,
        box=body_box,
        text=text,
        font_name=font_name,
        color=color,
        min_font=min_font,
        max_font=max_font,
        max_lines=max_lines,
        bold=bold,
        align=PP_ALIGN.LEFT,
    )


# -----------------------------------------------------------------------------
# Worked steps card
# -----------------------------------------------------------------------------


def _build_step_text(step: Mapping[str, str]) -> tuple[str, str, str]:
    title = _clean_text(step.get("title"))
    body = _clean_text(step.get("body"))
    formula = _clean_text(step.get("formula"))
    note = _clean_text(step.get("note"))
    body_text = _join_lines([body, note])
    return title, body_text, formula


def _measure_step_block(
    step: Mapping[str, str],
    *,
    width: float,
    title_max_font: int,
    body_max_font: int,
    formula_max_font: int,
) -> float:
    title, body_text, formula = _build_step_text(step)
    total = 0.0
    if title:
        total += _estimate_text_height(
            title,
            width=width,
            min_font=11,
            max_font=title_max_font,
            max_lines=2,
            extra_pad=0.01,
        )
    if body_text:
        total += _estimate_text_height(
            body_text,
            width=width,
            min_font=11,
            max_font=body_max_font,
            max_lines=4,
            extra_pad=0.02,
        )
    if formula:
        total += _estimate_text_height(
            formula,
            width=width,
            min_font=11,
            max_font=formula_max_font,
            max_lines=4,
            extra_pad=0.02,
        )
    if total > 0:
        total += 0.06
    return max(0.20, total)


def _choose_step_font_preset(
    steps: list[dict[str, str]],
    *,
    width: float,
    available_h: float,
    between_steps_gap: float,
) -> tuple[int, int, int]:
    presets = [
        (15, 14, 15),
        (14, 13, 14),
        (13, 12, 13),
        (12, 11, 12),
    ]
    for title_max, body_max, formula_max in presets:
        total_h = sum(
            _measure_step_block(
                step,
                width=width,
                title_max_font=title_max,
                body_max_font=body_max,
                formula_max_font=formula_max,
            )
            for step in steps
        )
        total_h += max(0, len(steps) - 1) * between_steps_gap
        if total_h <= available_h:
            return title_max, body_max, formula_max
    return presets[-1]


def _draw_steps_card(
    slide,
    *,
    box: Box,
    label: str,
    steps: list[dict[str, str]],
    style: Mapping[str, Any],
    layout: Mapping[str, Any],
) -> None:
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
    label_h = _draw_card_label(
        slide,
        box=box,
        text=label,
        color=style["label_color"],
    )

    inner = Box(
        box.x + 0.12,
        box.y + 0.08 + label_h,
        max(0.0, box.w - 0.24),
        max(0.0, box.h - label_h - 0.16),
    )
    if not steps or inner.w <= 0 or inner.h <= 0:
        return

    between_steps_gap = float(layout.get("steps_gap", 0.07))
    within_step_gap = float(layout.get("step_inner_gap", 0.02))
    title_max, body_max, formula_max = _choose_step_font_preset(
        steps,
        width=inner.w,
        available_h=inner.h,
        between_steps_gap=between_steps_gap,
    )

    y = inner.y
    for idx, step in enumerate(steps):
        title, body_text, formula = _build_step_text(step)

        title_h = _estimate_text_height(
            title,
            width=inner.w,
            min_font=11,
            max_font=title_max,
            max_lines=2,
            extra_pad=0.01,
        ) if title else 0.0
        body_h = _estimate_text_height(
            body_text,
            width=inner.w,
            min_font=11,
            max_font=body_max,
            max_lines=4,
            extra_pad=0.02,
        ) if body_text else 0.0
        formula_h = _estimate_text_height(
            formula,
            width=inner.w,
            min_font=11,
            max_font=formula_max,
            max_lines=4,
            extra_pad=0.02,
        ) if formula else 0.0

        block_h = title_h + body_h + formula_h
        if title_h and body_h:
            block_h += within_step_gap
        if (title_h or body_h) and formula_h:
            block_h += within_step_gap

        if y + block_h > inner.y + inner.h and idx < len(steps) - 1:
            remaining_steps = len(steps) - idx
            block_h = max(0.22, (inner.y + inner.h - y - between_steps_gap * max(0, remaining_steps - 1)) / remaining_steps)
            title_h = min(title_h, block_h * 0.26) if title_h else 0.0
            formula_h = min(formula_h, block_h * 0.34) if formula_h else 0.0
            body_h = max(0.0, block_h - title_h - formula_h - (within_step_gap if title_h and body_h else 0.0) - (within_step_gap if (title_h or body_h) and formula_h else 0.0))

        if title_h > 0:
            _add_fitted_text(
                slide,
                box=Box(inner.x, y, inner.w, title_h),
                text=title,
                font_name=BODY_FONT,
                color=style["body_color"],
                min_font=11,
                max_font=title_max,
                max_lines=2,
                bold=True,
                align=PP_ALIGN.LEFT,
            )
            y += title_h + (within_step_gap if body_h or formula_h else 0.0)

        if body_h > 0:
            _add_fitted_text(
                slide,
                box=Box(inner.x, y, inner.w, body_h),
                text=body_text,
                font_name=BODY_FONT,
                color=style["body_color"],
                min_font=11,
                max_font=body_max,
                max_lines=4,
                bold=False,
                align=PP_ALIGN.LEFT,
            )
            y += body_h + (within_step_gap if formula_h else 0.0)

        if formula_h > 0:
            _add_fitted_text(
                slide,
                box=Box(inner.x, y, inner.w, formula_h),
                text=formula,
                font_name=FORMULA_FONT,
                color=style["formula_color"],
                min_font=11,
                max_font=formula_max,
                max_lines=4,
                bold=False,
                align=PP_ALIGN.LEFT,
            )
            y += formula_h

        if idx < len(steps) - 1:
            y += between_steps_gap

        if y >= inner.y + inner.h:
            break


# -----------------------------------------------------------------------------
# Layout / build
# -----------------------------------------------------------------------------


def _layout_two_column(
    *,
    outer: Box,
    layout: Mapping[str, Any],
    explanation_text: str,
    result_text: str,
    takeaway_text: str,
) -> dict[str, Box]:
    col_gap = float(layout.get("column_gap", 0.22))
    visual_share = float(layout.get("visual_share", 0.42))
    visual_share = max(0.28, min(0.56, visual_share))

    visual_w = max(2.2, outer.w * visual_share - col_gap * 0.5)
    right_w = max(2.8, outer.w - visual_w - col_gap)

    visual_box = Box(outer.x, outer.y, visual_w, outer.h)
    right_x = visual_box.x + visual_box.w + col_gap

    explanation_h = 0.0
    if explanation_text:
        explanation_h = min(
            float(layout.get("explanation_max_h", 0.90)),
            max(
                float(layout.get("explanation_min_h", 0.48)),
                _estimate_text_height(
                    explanation_text,
                    width=right_w - 0.24,
                    min_font=12,
                    max_font=16,
                    max_lines=4,
                    extra_pad=0.06,
                ) + 0.16,
            ),
        )

    result_h = 0.0
    if result_text:
        result_h = min(
            float(layout.get("result_max_h", 1.05)),
            max(
                float(layout.get("result_min_h", 0.60)),
                _estimate_text_height(
                    result_text,
                    width=right_w - 0.24,
                    min_font=12,
                    max_font=16,
                    max_lines=5,
                    extra_pad=0.08,
                ) + 0.18,
            ),
        )

    takeaway_h = 0.0
    if takeaway_text:
        takeaway_h = min(
            float(layout.get("takeaway_max_h", 0.92)),
            max(
                float(layout.get("takeaway_min_h", 0.52)),
                _estimate_text_height(
                    takeaway_text,
                    width=right_w - 0.24,
                    min_font=11,
                    max_font=14,
                    max_lines=4,
                    extra_pad=0.06,
                ) + 0.16,
            ),
        )

    block_gap = float(layout.get("block_gap", 0.12))
    consumed = explanation_h + result_h + takeaway_h
    gaps = (1 if explanation_h > 0 else 0) + (1 if result_h > 0 and takeaway_h > 0 else 0)
    consumed += block_gap * gaps
    steps_h = max(float(layout.get("steps_min_h", 2.0)), outer.h - consumed)
    if steps_h + consumed > outer.h:
        overflow = steps_h + consumed - outer.h
        steps_h = max(float(layout.get("steps_min_h", 1.6)), steps_h - overflow)

    y = outer.y
    explanation_box = Box(right_x, y, right_w, explanation_h) if explanation_h > 0 else None
    if explanation_box is not None:
        y += explanation_h + block_gap

    steps_remaining_for_bottom = (result_h + (block_gap if result_h and takeaway_h else 0.0) + takeaway_h)
    steps_box = Box(right_x, y, right_w, max(0.0, outer.y + outer.h - y - steps_remaining_for_bottom))
    y = steps_box.y + steps_box.h
    if result_h > 0:
        y += block_gap
    result_box = Box(right_x, y, right_w, result_h) if result_h > 0 else None
    if result_box is not None:
        y += result_h
    if takeaway_h > 0:
        y += block_gap if result_box is not None else 0.0
    takeaway_box = Box(right_x, y, right_w, takeaway_h) if takeaway_h > 0 else None

    return {
        "visual_box": visual_box,
        "explanation_box": explanation_box,
        "steps_box": steps_box,
        "result_box": result_box,
        "takeaway_box": takeaway_box,
    }


def _layout_top_visual(
    *,
    outer: Box,
    layout: Mapping[str, Any],
    result_text: str,
    takeaway_text: str,
) -> dict[str, Box]:
    block_gap = float(layout.get("block_gap", 0.12))
    visual_h = float(layout.get("top_visual_h", 2.10))
    visual_h = max(1.60, min(2.80, visual_h))

    lower_y = outer.y + visual_h + block_gap
    lower_h = max(1.40, outer.h - visual_h - block_gap)

    col_gap = float(layout.get("column_gap", 0.22))
    right_share = float(layout.get("lower_right_share", 0.32))
    right_share = max(0.24, min(0.42, right_share))

    right_w = outer.w * right_share - col_gap * 0.5
    left_w = outer.w - right_w - col_gap

    steps_box = Box(outer.x, lower_y, left_w, lower_h)
    right_x = steps_box.x + steps_box.w + col_gap

    result_h = 0.0
    if result_text:
        result_h = min(
            float(layout.get("result_max_h", 1.20)),
            max(
                float(layout.get("result_min_h", 0.72)),
                _estimate_text_height(
                    result_text,
                    width=right_w - 0.24,
                    min_font=12,
                    max_font=16,
                    max_lines=5,
                    extra_pad=0.08,
                ) + 0.20,
            ),
        )

    takeaway_h = max(0.0, lower_h - result_h - (block_gap if result_h and takeaway_text else 0.0))
    if takeaway_text:
        takeaway_h = max(
            float(layout.get("takeaway_min_h", 0.72)),
            takeaway_h,
        )
        if takeaway_h > lower_h:
            takeaway_h = lower_h
            result_h = 0.0

    result_box = Box(right_x, lower_y, right_w, result_h) if result_h > 0 else None
    takeaway_y = lower_y + result_h + (block_gap if result_box is not None and takeaway_text else 0.0)
    takeaway_box = Box(right_x, takeaway_y, right_w, max(0.0, outer.y + outer.h - takeaway_y)) if takeaway_text else None

    return {
        "visual_box": Box(outer.x, outer.y, outer.w, visual_h),
        "explanation_box": None,
        "steps_box": steps_box,
        "result_box": result_box,
        "takeaway_box": takeaway_box,
    }


def build_worked_example_panel_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    """
    Builder for step-by-step math/example slides.

    Supported content keys:
      - mini_visual
      - explanation / text_explanation
      - steps: list[str | dict]
      - result: str | dict
      - formulas: list[str]  (fallback if result is omitted)
      - takeaway: str

    Supported layout modes:
      - worked_layout_mode="two_column"   (default)
      - worked_layout_mode="top_visual"
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

    header_result = render_header_from_spec(
        slide,
        spec,
        theme=theme_obj,
    )

    fallback_outer = Box(
        float(layout.get("content_x", 0.88)),
        float(
            layout.get(
                "content_y",
                header_result.content_top_y + float(layout.get("content_gap_from_header", 0.12)),
            )
        ),
        float(layout.get("content_w", 11.24)),
        float(layout.get("content_h", 5.12)),
    )
    outer_raw = layout.get("content_box")
    outer = _box_from_dict(outer_raw, fallback_outer) if isinstance(outer_raw, Mapping) else fallback_outer

    worked_layout_mode = str(layout.get("worked_layout_mode", spec.get("worked_layout_mode", "two_column"))).strip().lower()
    if worked_layout_mode == "top_visual":
        boxes = _layout_top_visual(
            outer=outer,
            layout=layout,
            result_text=result_text,
            takeaway_text=takeaway_text,
        )
    else:
        boxes = _layout_two_column(
            outer=outer,
            layout=layout,
            explanation_text=explanation_text,
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
        visual_box.x + 0.12,
        visual_box.y + 0.08 + visual_label_h,
        max(0.0, visual_box.w - 0.24),
        max(0.0, visual_box.h - visual_label_h - 0.16),
    )
    if visual_caption:
        caption_h = min(
            0.34,
            max(
                0.18,
                _estimate_text_height(
                    visual_caption,
                    width=visual_inner.w,
                    min_font=10,
                    max_font=11,
                    max_lines=2,
                    extra_pad=0.01,
                ),
            ),
        )
        visual_image_box = Box(
            visual_inner.x,
            visual_inner.y,
            visual_inner.w,
            max(0.0, visual_inner.h - caption_h - 0.04),
        )
        caption_box = Box(
            visual_inner.x,
            visual_image_box.y + visual_image_box.h + 0.04,
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
            min_font=10,
            max_font=11,
            max_lines=2,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    explanation_box = boxes.get("explanation_box")
    if isinstance(explanation_box, Box) and explanation_text:
        _draw_single_text_card(
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
            layout=layout,
        )

    result_box = boxes.get("result_box")
    if isinstance(result_box, Box) and result_text:
        _draw_single_text_card(
            slide,
            box=result_box,
            label=result_label,
            text=result_text,
            style=style,
            font_name=FORMULA_FONT,
            color=style["result_color"],
            min_font=12,
            max_font=16,
            max_lines=5,
            bold=False,
        )

    takeaway_box = boxes.get("takeaway_box")
    if isinstance(takeaway_box, Box) and takeaway_text:
        _draw_single_text_card(
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

    add_footer(
        slide,
        dark=style["footer_dark"],
        color=style["footer_color"],
    )

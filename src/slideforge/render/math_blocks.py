from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from slideforge.config.constants import BODY_FONT, FORMULA_FONT, LIGHT_BOX_FILL, NAVY, OFFWHITE, SLATE
from slideforge.layout.autofit import Box, fit_text
from slideforge.render.primitives import add_box_title, add_rounded_box, style_paragraph


@dataclass(frozen=True)
class MathBlockRenderResult:
    box: Box
    font_size: int
    line_count: int
    text: str


@dataclass(frozen=True)
class MathBlockStyle:
    body_font_name: str = BODY_FONT
    formula_font_name: str = FORMULA_FONT
    body_color: RGBColor = SLATE
    formula_color: RGBColor = NAVY
    result_color: RGBColor = NAVY
    label_color: RGBColor = SLATE
    card_fill_color: RGBColor | None = LIGHT_BOX_FILL
    card_line_color: RGBColor = RGBColor(173, 185, 220)
    final_answer_fill_color: RGBColor | None = OFFWHITE


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _clean_lines(items: Sequence[Any] | None) -> list[str]:
    return [_clean_text(item) for item in (items or []) if _clean_text(item)]


def _normalize_formula_lines(formulas: str | Sequence[Any]) -> list[str]:
    if isinstance(formulas, str):
        return [line.strip() for line in formulas.splitlines() if line.strip()]
    return _clean_lines(formulas)


def _normalize_step(step: Any, index: int) -> dict[str, str]:
    if isinstance(step, Mapping):
        return {
            "title": _clean_text(step.get("title") or step.get("label") or f"Step {index}"),
            "body": _clean_text(step.get("body") or step.get("text") or step.get("explanation")),
            "formula": _clean_text(step.get("formula") or step.get("equation") or step.get("result")),
            "note": _clean_text(step.get("note")),
        }
    return {
        "title": f"Step {index}",
        "body": _clean_text(step),
        "formula": "",
        "note": "",
    }


def _normalize_steps(steps: Sequence[Any] | None) -> list[dict[str, str]]:
    return [_normalize_step(step, idx + 1) for idx, step in enumerate(steps or [])]


def _shrink_box(box: Box, *, left: float = 0.0, top: float = 0.0, right: float = 0.0, bottom: float = 0.0) -> Box:
    x = box.x + left
    y = box.y + top
    w = max(0.0, box.w - left - right)
    h = max(0.0, box.h - top - bottom)
    return Box(x, y, w, h)


def _safe_fit_box(box: Box, *, pad_x: float = 0.02, pad_top: float = 0.02, pad_bottom: float = 0.05) -> Box:
    return _shrink_box(box, left=pad_x, right=pad_x, top=pad_top, bottom=pad_bottom)


def _fit_font_size(
    text: str,
    box: Box,
    *,
    min_font: int,
    max_font: int,
    max_lines: int | None,
    line_spacing: float = 1.12,
    prefer_single_line: bool = False,
    pad_x: float = 0.02,
    pad_top: float = 0.02,
    pad_bottom: float = 0.05,
    safety_height_ratio: float = 0.90,
    shrink_steps: int = 3,
) -> int:
    if not text.strip() or box.w <= 0 or box.h <= 0:
        return max_font

    safe_box = _safe_fit_box(box, pad_x=pad_x, pad_top=pad_top, pad_bottom=pad_bottom)
    if safe_box.w <= 0 or safe_box.h <= 0:
        return min_font

    fit_h = max(0.05, safe_box.h * safety_height_ratio)
    fitted = fit_text(
        text,
        safe_box.w,
        fit_h,
        min_font_size=min_font,
        max_font_size=max_font,
        max_lines=max_lines,
        line_spacing=line_spacing,
        prefer_single_line=prefer_single_line,
    )
    size = max(min_font, min(max_font, fitted.font_size))

    # Extra shrink loop to protect the bottom line from touching/leaving the box.
    for _ in range(max(0, shrink_steps)):
        trial = fit_text(
            text,
            safe_box.w,
            fit_h,
            min_font_size=min_font,
            max_font_size=size,
            max_lines=max_lines,
            line_spacing=line_spacing,
            prefer_single_line=prefer_single_line,
        )
        size = max(min_font, min(size, trial.font_size))
        if getattr(trial, 'estimated_height', 0.0) <= fit_h * 0.96:
            break
        if size <= min_font:
            break
        size -= 1

    return max(min_font, size)


def _add_text_frame(slide, *, box: Box, vertical_anchor=MSO_ANCHOR.TOP):
    shape = slide.shapes.add_textbox(Inches(box.x), Inches(box.y), Inches(box.w), Inches(box.h))
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.vertical_anchor = vertical_anchor
    tf.margin_left = Inches(0.0)
    tf.margin_right = Inches(0.0)
    tf.margin_top = Inches(0.0)
    tf.margin_bottom = Inches(0.0)
    return shape, tf


def _add_paragraph(
    tf,
    *,
    text: str,
    font_name: str,
    font_size: int,
    color: RGBColor,
    bold: bool = False,
    align=PP_ALIGN.LEFT,
    space_after_pt: int = 4,
    line_spacing: float = 1.12,
    first: bool = False,
):
    paragraph = tf.paragraphs[0] if first else tf.add_paragraph()
    paragraph.alignment = align
    paragraph.line_spacing = line_spacing
    paragraph.space_after = Pt(space_after_pt)
    run = paragraph.add_run()
    run.text = text
    style_paragraph(
        paragraph,
        font_name=font_name,
        font_size=font_size,
        color=color,
        bold=bold,
    )
    return paragraph


def estimate_multiline_formula_height(
    formulas: str | Sequence[Any],
    *,
    width: float,
    min_font: int = 14,
    max_font: int = 22,
    max_lines: int | None = 8,
    line_spacing: float = 1.10,
) -> float:
    text = "\n".join(_normalize_formula_lines(formulas))
    fit = fit_text(text, width, 10.0, min_font_size=min_font, max_font_size=max_font, max_lines=max_lines, line_spacing=line_spacing)
    return float(getattr(fit, 'estimated_height', 0.0)) + 0.06


def estimate_derivation_height(
    steps: Sequence[Any],
    *,
    width: float,
    min_body_font: int = 11,
    max_body_font: int = 15,
    line_spacing: float = 1.10,
) -> float:
    normalized = _normalize_steps(steps)
    lines: list[str] = []
    for step in normalized:
        lines.append(step['title'])
        if step['body']:
            lines.append(step['body'])
        if step['formula']:
            lines.append(step['formula'])
        if step['note']:
            lines.append(step['note'])
    text = "\n".join(lines)
    fit = fit_text(text, width, 10.0, min_font_size=min_body_font, max_font_size=max_body_font, max_lines=max(8, len(lines)+2), line_spacing=line_spacing)
    return float(getattr(fit, 'estimated_height', 0.0)) + 0.08


def estimate_result_callout_height(
    result_lines: str | Sequence[Any],
    *,
    width: float,
    min_font: int = 13,
    max_font: int = 18,
    line_spacing: float = 1.10,
) -> float:
    lines = _normalize_formula_lines(result_lines)
    text = "\n".join(lines)
    fit = fit_text(text, max(0.1, width - 0.36), 10.0, min_font_size=min_font, max_font_size=max_font, max_lines=max(3, len(lines)+1), line_spacing=line_spacing)
    return float(getattr(fit, 'estimated_height', 0.0)) + 0.46


def render_multiline_formulas(
    slide,
    *,
    box: Box,
    formulas: str | Sequence[Any],
    style: MathBlockStyle | None = None,
    min_font: int = 14,
    max_font: int = 22,
    max_lines: int | None = 8,
    align=PP_ALIGN.LEFT,
    line_spacing: float = 1.10,
) -> MathBlockRenderResult:
    style = style or MathBlockStyle()
    lines = _normalize_formula_lines(formulas)
    text = "\n".join(lines)
    font_size = _fit_font_size(
        text,
        box,
        min_font=min_font,
        max_font=max_font,
        max_lines=max_lines,
        line_spacing=line_spacing,
        pad_x=0.03,
        pad_top=0.02,
        pad_bottom=0.06,
    )
    inner = _safe_fit_box(box, pad_x=0.02, pad_top=0.02, pad_bottom=0.05)
    _, tf = _add_text_frame(slide, box=inner)
    for idx, line in enumerate(lines):
        _add_paragraph(
            tf,
            text=line,
            font_name=style.formula_font_name,
            font_size=font_size,
            color=style.formula_color,
            bold=False,
            align=align,
            space_after_pt=4,
            line_spacing=line_spacing,
            first=idx == 0,
        )
    return MathBlockRenderResult(box=box, font_size=font_size, line_count=len(lines), text=text)


def render_compact_derivation_stack(
    slide,
    *,
    box: Box,
    steps: Sequence[Any],
    style: MathBlockStyle | None = None,
    min_body_font: int = 11,
    max_body_font: int = 15,
    min_formula_font: int = 12,
    max_formula_font: int = 16,
    final_answer: str = "",
    emphasize_final_answer: bool = True,
    align=PP_ALIGN.LEFT,
) -> MathBlockRenderResult:
    style = style or MathBlockStyle()
    normalized_steps = _normalize_steps(steps)

    plain_lines: list[str] = []
    for step in normalized_steps:
        plain_lines.append(step['title'])
        if step['body']:
            plain_lines.append(step['body'])
        if step['formula']:
            plain_lines.append(step['formula'])
        if step['note']:
            plain_lines.append(step['note'])
    final_answer_text = _clean_text(final_answer)
    if final_answer_text:
        plain_lines.append(final_answer_text)

    text = "\n".join(plain_lines)
    # Stronger bottom-line safety for dense stacks.
    body_font = _fit_font_size(
        text,
        box,
        min_font=min_body_font,
        max_font=max_body_font,
        max_lines=max(8, len(plain_lines) + 2),
        line_spacing=1.08,
        pad_x=0.03,
        pad_top=0.02,
        pad_bottom=0.09,
        safety_height_ratio=0.88,
        shrink_steps=4,
    )
    formula_font = max(min_formula_font, min(max_formula_font, body_font + 1))
    result_font = max(formula_font, body_font + 1)

    inner = _safe_fit_box(box, pad_x=0.02, pad_top=0.02, pad_bottom=0.08)
    _, tf = _add_text_frame(slide, box=inner)
    first = True
    for step in normalized_steps:
        _add_paragraph(tf, text=step['title'], font_name=style.body_font_name, font_size=body_font, color=style.label_color, bold=True, align=align, space_after_pt=2, line_spacing=1.06, first=first)
        first = False
        if step['body']:
            _add_paragraph(tf, text=step['body'], font_name=style.body_font_name, font_size=body_font, color=style.body_color, align=align, space_after_pt=2, line_spacing=1.06)
        if step['formula']:
            _add_paragraph(tf, text=step['formula'], font_name=style.formula_font_name, font_size=formula_font, color=style.formula_color, align=align, space_after_pt=2, line_spacing=1.04)
        if step['note']:
            _add_paragraph(tf, text=step['note'], font_name=style.body_font_name, font_size=max(min_body_font, body_font - 1), color=style.body_color, align=align, space_after_pt=4, line_spacing=1.06)

    if final_answer_text:
        _add_paragraph(tf, text=final_answer_text, font_name=style.formula_font_name, font_size=result_font, color=style.result_color, bold=emphasize_final_answer, align=align, space_after_pt=0, line_spacing=1.02)

    return MathBlockRenderResult(box=box, font_size=body_font, line_count=len(plain_lines), text=text)


def render_result_callout(
    slide,
    *,
    box: Box,
    result_lines: str | Sequence[Any],
    label: str = 'Result',
    style: MathBlockStyle | None = None,
    min_font: int = 13,
    max_font: int = 18,
    emphasize_final_answer: bool = True,
    align=PP_ALIGN.LEFT,
    line_spacing: float = 1.10,
    draw_card: bool = True,
) -> MathBlockRenderResult:
    style = style or MathBlockStyle()
    lines = _normalize_formula_lines(result_lines) or ['']

    if draw_card:
        add_rounded_box(slide, box.x, box.y, box.w, box.h, line_color=style.card_line_color, fill_color=style.card_fill_color, line_width_pt=1.25)

    label_box = Box(box.x + 0.18, box.y + 0.10, max(0.0, box.w - 0.36), 0.20)
    add_box_title(slide, x=label_box.x, y=label_box.y, w=label_box.w, text=label, color=style.label_color, font_size=11, bold=True, align=PP_ALIGN.LEFT)

    body_box = Box(box.x + 0.18, box.y + 0.30, max(0.0, box.w - 0.36), max(0.0, box.h - 0.42))
    # Stronger safety for result boxes, especially last line.
    font_size = _fit_font_size(
        "\n".join(lines),
        body_box,
        min_font=min_font,
        max_font=max_font,
        max_lines=max(3, len(lines) + 1),
        line_spacing=line_spacing,
        pad_x=0.01,
        pad_top=0.01,
        pad_bottom=0.10,
        safety_height_ratio=0.86,
        shrink_steps=5,
    )

    inner = _safe_fit_box(body_box, pad_x=0.0, pad_top=0.0, pad_bottom=0.08)
    _, tf = _add_text_frame(slide, box=inner, vertical_anchor=MSO_ANCHOR.MIDDLE)
    for idx, line in enumerate(lines):
        is_last = idx == len(lines) - 1
        _add_paragraph(
            tf,
            text=line,
            font_name=style.formula_font_name,
            font_size=font_size + (1 if is_last and emphasize_final_answer else 0),
            color=style.result_color,
            bold=bool(is_last and emphasize_final_answer),
            align=align,
            space_after_pt=2 if not is_last else 0,
            line_spacing=1.06 if is_last else line_spacing,
            first=idx == 0,
        )

    return MathBlockRenderResult(box=box, font_size=font_size, line_count=len(lines), text="\n".join(lines))


def render_emphasized_final_answer(
    slide,
    *,
    box: Box,
    text: str,
    style: MathBlockStyle | None = None,
    min_font: int = 14,
    max_font: int = 20,
    align=PP_ALIGN.CENTER,
) -> MathBlockRenderResult:
    style = style or MathBlockStyle()
    add_rounded_box(slide, box.x, box.y, box.w, box.h, line_color=style.card_line_color, fill_color=style.final_answer_fill_color, line_width_pt=1.0)

    font_size = _fit_font_size(
        text,
        box,
        min_font=min_font,
        max_font=max_font,
        max_lines=2,
        line_spacing=1.05,
        pad_x=0.03,
        pad_top=0.02,
        pad_bottom=0.08,
        safety_height_ratio=0.88,
        shrink_steps=4,
    )
    inner = _safe_fit_box(box, pad_x=0.02, pad_top=0.02, pad_bottom=0.07)
    _, tf = _add_text_frame(slide, box=inner, vertical_anchor=MSO_ANCHOR.MIDDLE)
    _add_paragraph(tf, text=text, font_name=style.formula_font_name, font_size=font_size, color=style.result_color, bold=True, align=align, space_after_pt=0, line_spacing=1.04, first=True)
    return MathBlockRenderResult(box=box, font_size=font_size, line_count=1, text=text)


__all__ = [
    'MathBlockRenderResult',
    'MathBlockStyle',
    'estimate_multiline_formula_height',
    'estimate_derivation_height',
    'estimate_result_callout_height',
    'render_multiline_formulas',
    'render_compact_derivation_stack',
    'render_result_callout',
    'render_emphasized_final_answer',
]

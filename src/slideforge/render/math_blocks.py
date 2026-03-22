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
    return {"title": f"Step {index}", "body": _clean_text(step), "formula": "", "note": ""}


def _normalize_steps(steps: Sequence[Any] | None) -> list[dict[str, str]]:
    return [_normalize_step(step, idx + 1) for idx, step in enumerate(steps or [])]


def _fit_font_size(
    text: str,
    box: Box,
    *,
    min_font: int,
    max_font: int,
    max_lines: int | None,
    line_spacing: float = 1.08,
    safety_w: float = 0.96,
    safety_h: float = 0.90,
) -> int:
    if not text.strip() or box.w <= 0 or box.h <= 0:
        return max_font
    fitted = fit_text(
        text,
        box.w * safety_w,
        box.h * safety_h,
        min_font_size=min_font,
        max_font_size=max_font,
        max_lines=max_lines,
        line_spacing=line_spacing,
    )
    return max(min_font, fitted.font_size - 1)


def estimate_multiline_formula_height(
    formulas: str | Sequence[Any],
    *,
    width: float,
    min_font: int = 14,
    max_font: int = 22,
    max_lines: int | None = 8,
    line_spacing: float = 1.08,
) -> float:
    lines = _normalize_formula_lines(formulas)
    text = "\n".join(lines)
    if not text or width <= 0:
        return 0.0
    fitted = fit_text(text, width * 0.96, 10.0, min_font_size=min_font, max_font_size=max_font, max_lines=max_lines, line_spacing=line_spacing)
    return max(0.0, fitted.estimated_height + 0.04)


def estimate_derivation_height(
    steps: Sequence[Any],
    *,
    width: float,
    min_body_font: int = 10,
    max_body_font: int = 14,
) -> float:
    normalized = _normalize_steps(steps)
    text = "\n\n".join(
        "\n".join(v for v in [s["title"], s["body"], s["formula"], s["note"]] if v)
        for s in normalized
    )
    if not text or width <= 0:
        return 0.0
    fitted = fit_text(text, width * 0.96, 10.0, min_font_size=min_body_font, max_font_size=max_body_font, max_lines=None, line_spacing=1.06)
    return max(0.0, fitted.estimated_height + 0.10)


def estimate_result_callout_height(
    result_lines: str | Sequence[Any],
    *,
    width: float,
    min_font: int = 12,
    max_font: int = 17,
) -> float:
    text = "\n".join(_normalize_formula_lines(result_lines))
    if not text or width <= 0:
        return 0.0
    fitted = fit_text(text, width * 0.96, 10.0, min_font_size=min_font, max_font_size=max_font, max_lines=5, line_spacing=1.08)
    return max(0.0, fitted.estimated_height + 0.28)


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
    space_after_pt: int = 2,
    line_spacing: float = 1.05,
    first: bool = False,
):
    paragraph = tf.paragraphs[0] if first else tf.add_paragraph()
    paragraph.alignment = align
    paragraph.line_spacing = line_spacing
    paragraph.space_after = Pt(space_after_pt)
    run = paragraph.add_run()
    run.text = text
    style_paragraph(paragraph, font_name=font_name, font_size=font_size, color=color, bold=bold)
    return paragraph


def render_multiline_formulas(
    slide,
    *,
    box: Box,
    formulas: str | Sequence[Any],
    style: MathBlockStyle | None = None,
    min_font: int = 13,
    max_font: int = 20,
    max_lines: int | None = 8,
    align=PP_ALIGN.LEFT,
    line_spacing: float = 1.06,
) -> MathBlockRenderResult:
    style = style or MathBlockStyle()
    lines = _normalize_formula_lines(formulas)
    text = "\n".join(lines)
    font_size = _fit_font_size(text, box, min_font=min_font, max_font=max_font, max_lines=max_lines, line_spacing=line_spacing)
    _, tf = _add_text_frame(slide, box=box)
    for idx, line in enumerate(lines):
        _add_paragraph(tf, text=line, font_name=style.formula_font_name, font_size=font_size, color=style.formula_color, align=align, line_spacing=line_spacing, space_after_pt=2 if idx < len(lines) - 1 else 0, first=idx == 0)
    return MathBlockRenderResult(box=box, font_size=font_size, line_count=len(lines), text=text)


def render_compact_derivation_stack(
    slide,
    *,
    box: Box,
    steps: Sequence[Any],
    style: MathBlockStyle | None = None,
    min_body_font: int = 10,
    max_body_font: int = 13,
    min_formula_font: int = 11,
    max_formula_font: int = 14,
    final_answer: str = "",
    emphasize_final_answer: bool = True,
    align=PP_ALIGN.LEFT,
    final_answer_style: str = "inline",
) -> MathBlockRenderResult:
    style = style or MathBlockStyle()
    normalized_steps = _normalize_steps(steps)
    plain_lines: list[str] = []
    for step in normalized_steps:
        plain_lines.append(step["title"])
        if step["body"]:
            plain_lines.append(step["body"])
        if step["formula"]:
            plain_lines.append(step["formula"])
        if step["note"]:
            plain_lines.append(step["note"])
    final_answer_text = _clean_text(final_answer)
    if final_answer_text and final_answer_style == "inline":
        plain_lines.append(final_answer_text)

    serialized = "\n".join(plain_lines)
    body_font = _fit_font_size(serialized, box, min_font=min_body_font, max_font=max_body_font, max_lines=None, line_spacing=1.04)
    title_font = min(max_body_font, max(min_body_font, body_font + 1))
    formula_font = min(max_formula_font, max(min_formula_font, body_font + 1))
    note_font = max(min_body_font, body_font - 1)

    _, tf = _add_text_frame(slide, box=box)
    first = True
    for idx, step in enumerate(normalized_steps):
        _add_paragraph(tf, text=step["title"], font_name=style.body_font_name, font_size=title_font, color=style.label_color, bold=True, align=align, space_after_pt=1, line_spacing=1.02, first=first)
        first = False
        if step["body"]:
            _add_paragraph(tf, text=step["body"], font_name=style.body_font_name, font_size=body_font, color=style.body_color, align=align, space_after_pt=1, line_spacing=1.03)
        if step["formula"]:
            _add_paragraph(tf, text=step["formula"], font_name=style.formula_font_name, font_size=formula_font, color=style.formula_color, align=align, space_after_pt=1, line_spacing=1.02)
        if step["note"]:
            _add_paragraph(tf, text=step["note"], font_name=style.body_font_name, font_size=note_font, color=style.body_color, align=align, space_after_pt=2 if idx < len(normalized_steps) - 1 else 0, line_spacing=1.03)
        elif idx < len(normalized_steps) - 1:
            _add_paragraph(tf, text="", font_name=style.body_font_name, font_size=body_font, color=style.body_color, align=align, space_after_pt=1, line_spacing=0.95)

    if final_answer_text and final_answer_style == "inline":
        _add_paragraph(tf, text=final_answer_text, font_name=style.formula_font_name, font_size=min(max_formula_font + 1, formula_font + 1), color=style.result_color, bold=emphasize_final_answer, align=align, space_after_pt=0, line_spacing=1.02)

    return MathBlockRenderResult(box=box, font_size=body_font, line_count=len(plain_lines), text=serialized)


def render_result_callout(
    slide,
    *,
    box: Box,
    result_lines: str | Sequence[Any],
    label: str = "Result",
    style: MathBlockStyle | None = None,
    min_font: int = 12,
    max_font: int = 16,
    emphasize_final_answer: bool = True,
    align=PP_ALIGN.LEFT,
    line_spacing: float = 1.06,
    draw_card: bool = True,
) -> MathBlockRenderResult:
    style = style or MathBlockStyle()
    lines = _normalize_formula_lines(result_lines) or [""]

    if draw_card:
        add_rounded_box(slide, box.x, box.y, box.w, box.h, line_color=style.card_line_color, fill_color=style.card_fill_color, line_width_pt=1.2)

    label_box = Box(box.x + 0.14, box.y + 0.07, max(0.0, box.w - 0.28), 0.18)
    add_box_title(slide, x=label_box.x, y=label_box.y, w=label_box.w, text=label, color=style.label_color, font_size=11, bold=True, align=PP_ALIGN.LEFT)

    body_box = Box(box.x + 0.16, box.y + 0.30, max(0.0, box.w - 0.32), max(0.0, box.h - 0.40))
    font_size = _fit_font_size("\n".join(lines), body_box, min_font=min_font, max_font=max_font, max_lines=max(3, len(lines) + 1), line_spacing=line_spacing)

    _, tf = _add_text_frame(slide, box=body_box, vertical_anchor=MSO_ANCHOR.MIDDLE)
    for idx, line in enumerate(lines):
        is_last = idx == len(lines) - 1
        _add_paragraph(
            tf,
            text=line,
            font_name=style.formula_font_name if (is_last or len(lines) == 1) else style.body_font_name,
            font_size=font_size + (1 if is_last and emphasize_final_answer else 0),
            color=style.result_color if is_last else style.body_color,
            bold=bool(is_last and emphasize_final_answer),
            align=align,
            space_after_pt=1 if not is_last else 0,
            line_spacing=line_spacing,
            first=idx == 0,
        )
    return MathBlockRenderResult(box=box, font_size=font_size, line_count=len(lines), text="\n".join(lines))


def render_emphasized_final_answer(
    slide,
    *,
    box: Box,
    text: str,
    style: MathBlockStyle | None = None,
    min_font: int = 13,
    max_font: int = 18,
    align=PP_ALIGN.CENTER,
) -> MathBlockRenderResult:
    style = style or MathBlockStyle()
    add_rounded_box(slide, box.x, box.y, box.w, box.h, line_color=style.card_line_color, fill_color=style.final_answer_fill_color, line_width_pt=1.0)
    font_size = _fit_font_size(text, box, min_font=min_font, max_font=max_font, max_lines=2, line_spacing=1.03)
    _, tf = _add_text_frame(slide, box=box, vertical_anchor=MSO_ANCHOR.MIDDLE)
    _add_paragraph(tf, text=text, font_name=style.formula_font_name, font_size=font_size, color=style.result_color, bold=True, align=align, space_after_pt=0, line_spacing=1.03, first=True)
    return MathBlockRenderResult(box=box, font_size=font_size, line_count=1, text=text)


__all__ = [
    "MathBlockRenderResult",
    "MathBlockStyle",
    "estimate_multiline_formula_height",
    "estimate_derivation_height",
    "estimate_result_callout_height",
    "render_multiline_formulas",
    "render_compact_derivation_stack",
    "render_result_callout",
    "render_emphasized_final_answer",
]

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

from slideforge.config.constants import BODY_FONT, FORMULA_FONT, SLATE
from slideforge.layout.autofit import Box, fit_text
from slideforge.render.primitives import add_box_title, add_rounded_box, add_textbox

TEXT_BOX_SAFE_HEIGHT_RATIO = 0.86
TEXT_BOX_SAFE_WIDTH_RATIO = 0.96
PARAGRAPH_EXTRA_PAD = 0.03
RESULT_EXTRA_PAD = 0.05


@dataclass(frozen=True)
class MathBlockStyle:
    body_color: RGBColor
    formula_color: RGBColor
    result_color: RGBColor
    label_color: RGBColor
    card_fill_color: RGBColor | None = None
    card_line_color: RGBColor | None = None
    final_answer_fill_color: RGBColor | None = None
    final_answer_line_color: RGBColor | None = None


def _clean(value: object) -> str:
    return str(value or "").strip()


def _safe_fit_font(
    text: str,
    box: Box,
    *,
    min_font: int,
    max_font: int,
    max_lines: int | None,
    line_spacing: float,
    safe_height_ratio: float = TEXT_BOX_SAFE_HEIGHT_RATIO,
    safe_width_ratio: float = TEXT_BOX_SAFE_WIDTH_RATIO,
) -> int:
    text = _clean(text)
    if not text or box.w <= 0 or box.h <= 0:
        return max_font
    fitted = fit_text(
        text,
        box.w * safe_width_ratio,
        box.h * safe_height_ratio,
        min_font_size=min_font,
        max_font_size=max_font,
        max_lines=max_lines,
        line_spacing=line_spacing,
    )
    font = max(min_font, fitted.font_size)
    while font > min_font:
        probe = fit_text(
            text,
            box.w * safe_width_ratio,
            box.h * safe_height_ratio,
            min_font_size=font,
            max_font_size=font,
            max_lines=max_lines,
            line_spacing=line_spacing,
        )
        if probe.estimated_height <= box.h * safe_height_ratio:
            break
        font -= 1
    return max(min_font, font)


def _estimate_height(
    text: str,
    width: float,
    *,
    min_font: int,
    max_font: int,
    max_lines: int | None,
    line_spacing: float = 1.08,
    extra_pad: float = PARAGRAPH_EXTRA_PAD,
) -> float:
    text = _clean(text)
    if not text or width <= 0:
        return 0.0
    fitted = fit_text(
        text,
        width * TEXT_BOX_SAFE_WIDTH_RATIO,
        10.0,
        min_font_size=min_font,
        max_font_size=max_font,
        max_lines=max_lines,
        line_spacing=line_spacing,
    )
    return max(0.0, fitted.estimated_height + extra_pad)


def _draw_block_text(
    slide,
    *,
    box: Box,
    text: str,
    font_name: str,
    color,
    min_font: int,
    max_font: int,
    max_lines: int | None,
    align=PP_ALIGN.LEFT,
    line_spacing: float = 1.08,
    bold: bool = False,
) -> None:
    text = _clean(text)
    if not text or box.w <= 0 or box.h <= 0:
        return
    font_size = _safe_fit_font(
        text,
        box,
        min_font=min_font,
        max_font=max_font,
        max_lines=max_lines,
        line_spacing=line_spacing,
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


def render_compact_derivation_stack(
    slide,
    *,
    box: Box,
    steps: Sequence[Mapping[str, str]],
    style: MathBlockStyle,
    min_body_font: int = 10,
    max_body_font: int = 12,
    min_formula_font: int = 11,
    max_formula_font: int = 13,
    final_answer: str = "",
    emphasize_final_answer: bool = False,
    align=PP_ALIGN.LEFT,
) -> None:
    if box.w <= 0 or box.h <= 0 or not steps:
        return

    pieces: list[str] = []
    for step in steps:
        for key in ("title", "body", "formula", "note"):
            value = _clean(step.get(key))
            if value:
                pieces.append(value)
        pieces.append("")
    if final_answer:
        pieces.append(_clean(final_answer))
    text = "\n".join(pieces).strip()

    # Conservative single-frame render to avoid bottom spill.
    font_size = _safe_fit_font(
        text,
        Box(box.x, box.y, box.w, box.h - 0.02),
        min_font=min_body_font,
        max_font=max(max_body_font, max_formula_font),
        max_lines=None,
        line_spacing=1.07,
    )

    # Slightly reduce if formulas are numerous.
    formula_count = sum(1 for step in steps if _clean(step.get("formula")))
    if formula_count >= 3:
        font_size = max(min_body_font, font_size - 1)

    add_textbox(
        slide,
        x=box.x,
        y=box.y,
        w=box.w,
        h=box.h,
        text=text,
        font_name=BODY_FONT,
        font_size=font_size,
        color=style.body_color,
        bold=False,
        align=align,
    )


def render_result_callout(
    slide,
    *,
    box: Box,
    result_lines: Sequence[str],
    label: str = "Result",
    style: MathBlockStyle,
    min_font: int = 11,
    max_font: int = 15,
    emphasize_final_answer: bool = True,
    align=PP_ALIGN.LEFT,
    draw_card: bool = True,
) -> None:
    if box.w <= 0 or box.h <= 0:
        return
    lines = [_clean(line) for line in result_lines if _clean(line)]
    if not lines:
        return

    if draw_card:
        add_rounded_box(
            slide,
            box.x,
            box.y,
            box.w,
            box.h,
            line_color=style.card_line_color or style.label_color,
            fill_color=style.card_fill_color,
            line_width_pt=1.2,
        )

    add_box_title(
        slide,
        x=box.x + 0.12,
        y=box.y + 0.06,
        w=max(0.0, box.w - 0.24),
        text=label,
        color=style.label_color,
        font_size=11,
    )

    inner = Box(box.x + 0.16, box.y + 0.34, max(0.0, box.w - 0.32), max(0.0, box.h - 0.46))
    body = "\n".join(lines[:-1]).strip()
    final = lines[-1]

    if body:
        body_h = min(inner.h * 0.56, _estimate_height(body, inner.w, min_font=min_font, max_font=max_font, max_lines=4, extra_pad=RESULT_EXTRA_PAD))
        body_box = Box(inner.x, inner.y, inner.w, max(0.0, body_h))
        _draw_block_text(
            slide,
            box=body_box,
            text=body,
            font_name=BODY_FONT,
            color=style.body_color,
            min_font=min_font,
            max_font=max_font - 1,
            max_lines=4,
            align=align,
        )
        final_y = body_box.y + body_box.h + 0.03
        final_h = max(0.0, inner.h - body_box.h - 0.03)
    else:
        final_y = inner.y
        final_h = inner.h

    final_box = Box(inner.x, final_y, inner.w, final_h)
    final_font_min = max(min_font + 1, 12) if emphasize_final_answer else min_font
    final_font_max = max(max_font + 1, 16) if emphasize_final_answer else max_font
    _draw_block_text(
        slide,
        box=final_box,
        text=final,
        font_name=FORMULA_FONT,
        color=style.result_color,
        min_font=final_font_min,
        max_font=final_font_max,
        max_lines=2,
        align=align,
        line_spacing=1.02,
        bold=emphasize_final_answer,
    )


__all__ = [
    "MathBlockStyle",
    "render_compact_derivation_stack",
    "render_result_callout",
]

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from slideforge.layout.base import Box, Unit
from slideforge.layout.stack import TextBlockSpec, layout_vertical_stack
from slideforge.layout.text_fit import TextFit, clamp, fit_text, line_height_inches


@dataclass
class PosterLayoutResult:
    outer_box: Box
    visual_box: Box
    text_boxes: dict[str, Box]
    text_fits: dict[str, TextFit]
    visual_share: float


def _manual_line_count(text: str) -> int:
    if not text.strip():
        return 0
    return max(1, len([line for line in text.split("\n")]))


def _build_text_specs(
    *,
    explanation: str,
    bullets_text: str,
    formulas_text: str,
    note_text: str,
    takeaway_text: str,
    dense_math_mode: bool = False,
    reserve_formula_first: bool = False,
) -> list[TextBlockSpec]:
    specs: list[TextBlockSpec] = []

    explanation_max_lines = 4 if dense_math_mode else 3
    bullets_max_lines = 4 if dense_math_mode else 3
    formulas_max_lines = max(3, min(6 if dense_math_mode else 4, _manual_line_count(formulas_text) + 1))
    takeaway_max_lines = 3 if dense_math_mode else 2

    if explanation.strip():
        specs.append(
            TextBlockSpec(
                key="explanation",
                text=explanation,
                min_font_size=16 if dense_math_mode else 15,
                max_font_size=18,
                max_lines=explanation_max_lines,
            )
        )

    if bullets_text.strip():
        specs.append(
            TextBlockSpec(
                key="bullets",
                text=bullets_text,
                min_font_size=13,
                max_font_size=15,
                max_lines=bullets_max_lines,
            )
        )

    if formulas_text.strip():
        specs.append(
            TextBlockSpec(
                key="formulas",
                text=formulas_text,
                min_font_size=13 if reserve_formula_first or dense_math_mode else 12,
                max_font_size=16 if reserve_formula_first or dense_math_mode else 14,
                max_lines=formulas_max_lines,
                line_spacing=1.12 if dense_math_mode else 1.15,
            )
        )

    if note_text.strip():
        specs.append(
            TextBlockSpec(
                key="note",
                text=note_text,
                min_font_size=12,
                max_font_size=13 if dense_math_mode else 14,
                max_lines=2,
            )
        )

    if takeaway_text.strip():
        specs.append(
            TextBlockSpec(
                key="takeaway",
                text=takeaway_text,
                min_font_size=13 if dense_math_mode else 12,
                max_font_size=15 if dense_math_mode else 14,
                max_lines=takeaway_max_lines,
                bold=True,
            )
        )

    return specs


def _text_container(
    outer_box: Box,
    *,
    top_pad: Unit,
    bottom_pad: Unit,
    side_pad: Unit,
    visual_h: Unit,
    gap: Unit,
) -> Box:
    return Box(
        outer_box.x + side_pad,
        outer_box.y + top_pad + visual_h + gap,
        max(0.0, outer_box.w - 2 * side_pad),
        max(0.0, outer_box.h - top_pad - bottom_pad - visual_h - gap),
    )


def _empty_result(outer_box: Box, *, top_pad: Unit, side_pad: Unit) -> PosterLayoutResult:
    empty_visual = Box(
        outer_box.x + side_pad,
        outer_box.y + top_pad,
        max(0.0, outer_box.w - 2 * side_pad),
        0.0,
    )
    return PosterLayoutResult(
        outer_box=outer_box,
        visual_box=empty_visual,
        text_boxes={},
        text_fits={},
        visual_share=0.0,
    )


def _estimate_reserved_block_height(
    *,
    text: str,
    width: Unit,
    min_font_size: int,
    max_font_size: int,
    max_lines: int | None,
    line_spacing: float,
    prefer_single_line: bool = False,
    fallback_extra_pad: float = 0.05,
) -> float:
    if not text.strip() or width <= 0:
        return 0.0

    probe_fit = fit_text(
        text,
        width,
        100.0,
        min_font_size=min_font_size,
        max_font_size=max_font_size,
        line_spacing=line_spacing,
        prefer_single_line=prefer_single_line,
        max_lines=max_lines,
    )

    if probe_fit is None:
        return line_height_inches(min_font_size, line_spacing) + fallback_extra_pad
    return probe_fit.estimated_height + fallback_extra_pad


def _estimate_reserved_text_height(
    specs: Sequence[TextBlockSpec],
    *,
    width: Unit,
    gap: Unit,
    reserve_formula_first: bool,
    keep_readable_keys: Iterable[str],
) -> float:
    if not specs or width <= 0:
        return 0.0

    readable = set(keep_readable_keys)
    total = 0.0
    included = 0

    for spec in specs:
        if not spec.text.strip():
            continue

        reserve_this = reserve_formula_first and spec.key == "formulas"
        reserve_this = reserve_this or spec.key in readable

        if reserve_this:
            total += _estimate_reserved_block_height(
                text=spec.text,
                width=width,
                min_font_size=spec.min_font_size,
                max_font_size=spec.max_font_size,
                max_lines=spec.max_lines,
                line_spacing=spec.line_spacing,
                prefer_single_line=spec.prefer_single_line,
            )
            included += 1
        else:
            total += max(
                line_height_inches(spec.min_font_size, spec.line_spacing) + 0.04,
                0.16,
            )
            included += 1

    if included > 1:
        total += gap * (included - 1)
    return total


def _fit_text_stack(
    outer_box: Box,
    *,
    specs: Sequence[TextBlockSpec],
    top_pad: Unit,
    bottom_pad: Unit,
    side_pad: Unit,
    gap: Unit,
    preferred_visual_share: float,
    visual_min_share: float,
    visual_max_share: float,
    reserve_formula_first: bool,
    keep_readable_keys: Iterable[str],
) -> PosterLayoutResult:
    usable_h = max(0.0, outer_box.h - top_pad - bottom_pad)
    if usable_h <= 0:
        return _empty_result(outer_box, top_pad=top_pad, side_pad=side_pad)

    min_visual_h = usable_h * clamp(visual_min_share, 0.0, 1.0)
    max_visual_h = usable_h * clamp(visual_max_share, 0.0, 1.0)
    inner_w = max(0.0, outer_box.w - 2 * side_pad)

    visual_h = clamp(usable_h * preferred_visual_share, min_visual_h, max_visual_h)

    if reserve_formula_first:
        reserved_text_h = _estimate_reserved_text_height(
            specs,
            width=inner_w,
            gap=gap,
            reserve_formula_first=True,
            keep_readable_keys=keep_readable_keys,
        )
        text_first_visual_h = usable_h - reserved_text_h - gap
        visual_h = clamp(text_first_visual_h, min_visual_h, max_visual_h)

    best_layout = None
    best_visual_h = visual_h
    best_penalty = float("inf")

    for _ in range(6):
        text_box = _text_container(
            outer_box,
            top_pad=top_pad,
            bottom_pad=bottom_pad,
            side_pad=side_pad,
            visual_h=visual_h,
            gap=gap,
        )
        text_layout = layout_vertical_stack(
            text_box,
            list(specs),
            gap=gap,
            top_pad=0.0,
            bottom_pad=0.0,
        )

        readable_failures = 0
        for key in keep_readable_keys:
            fit = text_layout.text_fits.get(key)
            if fit is not None and not fit.fits:
                readable_failures += 1

        overflow = max(0.0, text_layout.used_height - text_box.h)
        penalty = overflow + readable_failures * 0.12

        if penalty < best_penalty:
            best_penalty = penalty
            best_layout = text_layout
            best_visual_h = visual_h

        if penalty <= 0.02:
            best_layout = text_layout
            best_visual_h = visual_h
            break

        next_visual_h = max(min_visual_h, visual_h - max(0.08, penalty))
        if abs(next_visual_h - visual_h) < 1e-6:
            break
        visual_h = next_visual_h

    final_visual_box = Box(
        outer_box.x + side_pad + 0.06,
        outer_box.y + top_pad,
        max(0.0, outer_box.w - 2 * side_pad - 0.12),
        max(0.0, best_visual_h),
    )

    final_text_box = Box(
        outer_box.x + side_pad,
        final_visual_box.bottom + gap,
        max(0.0, outer_box.w - 2 * side_pad),
        max(0.0, outer_box.bottom - bottom_pad - (final_visual_box.bottom + gap)),
    )
    final_layout = layout_vertical_stack(
        final_text_box,
        list(specs),
        gap=gap,
        top_pad=0.0,
        bottom_pad=0.0,
    )

    return PosterLayoutResult(
        outer_box=outer_box,
        visual_box=final_visual_box,
        text_boxes=final_layout.boxes,
        text_fits=final_layout.text_fits,
        visual_share=final_visual_box.h / max(outer_box.h, 1e-6),
    )


def layout_worked_math_poster(
    outer_box: Box,
    *,
    explanation: str = "",
    bullets_text: str = "",
    formulas_text: str = "",
    note_text: str = "",
    takeaway_text: str = "",
    top_pad: Unit = 0.18,
    bottom_pad: Unit = 0.14,
    gap: Unit = 0.08,
    side_pad: Unit = 0.22,
    visual_min_share: float = 0.34,
    visual_max_share: float = 0.62,
    preferred_visual_share: float = 0.46,
) -> PosterLayoutResult:
    """
    Text-first poster layout for worked mathematics or homework-style slides.

    Design goals:
    - reserve readable space for formulas first
    - keep explanation and takeaway legible
    - allow the visual to shrink when the derivation stack is dense
    """
    specs = _build_text_specs(
        explanation=explanation,
        bullets_text=bullets_text,
        formulas_text=formulas_text,
        note_text=note_text,
        takeaway_text=takeaway_text,
        dense_math_mode=True,
        reserve_formula_first=True,
    )
    return _fit_text_stack(
        outer_box,
        specs=specs,
        top_pad=top_pad,
        bottom_pad=bottom_pad,
        side_pad=side_pad,
        gap=gap,
        preferred_visual_share=preferred_visual_share,
        visual_min_share=visual_min_share,
        visual_max_share=visual_max_share,
        reserve_formula_first=True,
        keep_readable_keys=("explanation", "formulas", "takeaway"),
    )


def layout_concept_poster(
    outer_box: Box,
    *,
    explanation: str = "",
    bullets_text: str = "",
    formulas_text: str = "",
    note_text: str = "",
    takeaway_text: str = "",
    top_pad: Unit = 0.18,
    bottom_pad: Unit = 0.14,
    gap: Unit = 0.08,
    side_pad: Unit = 0.22,
    visual_min_share: float = 0.58,
    visual_max_share: float = 0.80,
    preferred_visual_share: float = 0.73,
    layout_mode: str = "concept",
    dense_math_mode: bool = False,
    prioritize_text_over_visual: bool = False,
    reserve_formula_first: bool | None = None,
) -> PosterLayoutResult:
    """
    Default poster layout for concept slides.

    Backward compatible with the previous API, but now also supports a text-first
    balancing mode for dense mathematical slides.

    Use either:
    - layout_mode="worked_math"
    - dense_math_mode=True
    - prioritize_text_over_visual=True
    """
    mode = (layout_mode or "concept").strip().lower()
    text_first = prioritize_text_over_visual or dense_math_mode or mode in {"worked_math", "dense_math", "text_first"}
    reserve_formula_first = text_first if reserve_formula_first is None else reserve_formula_first

    if text_first:
        worked_min_share = min(visual_min_share, 0.62)
        worked_max_share = min(max(visual_max_share, worked_min_share + 0.08), 0.68)
        worked_preferred_share = min(max(preferred_visual_share, worked_min_share), worked_max_share)
        return layout_worked_math_poster(
            outer_box,
            explanation=explanation,
            bullets_text=bullets_text,
            formulas_text=formulas_text,
            note_text=note_text,
            takeaway_text=takeaway_text,
            top_pad=top_pad,
            bottom_pad=bottom_pad,
            gap=gap,
            side_pad=side_pad,
            visual_min_share=worked_min_share,
            visual_max_share=worked_max_share,
            preferred_visual_share=worked_preferred_share,
        )

    specs = _build_text_specs(
        explanation=explanation,
        bullets_text=bullets_text,
        formulas_text=formulas_text,
        note_text=note_text,
        takeaway_text=takeaway_text,
        dense_math_mode=False,
        reserve_formula_first=False,
    )
    return _fit_text_stack(
        outer_box,
        specs=specs,
        top_pad=top_pad,
        bottom_pad=bottom_pad,
        side_pad=side_pad,
        gap=gap,
        preferred_visual_share=preferred_visual_share,
        visual_min_share=visual_min_share,
        visual_max_share=visual_max_share,
        reserve_formula_first=False,
        keep_readable_keys=("explanation", "takeaway"),
    )

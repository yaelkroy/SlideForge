from __future__ import annotations

from dataclasses import dataclass

from slideforge.layout.base import Box, Unit
from slideforge.layout.text_fit import TextFit, clamp, fit_text


@dataclass
class WorkedExampleLayoutResult:
    outer_box: Box
    diagram_box: Box
    steps_box: Box
    result_box: Box
    takeaway_box: Box
    explanation_box: Box
    text_fits: dict[str, TextFit]
    mode: str
    diagram_share: float


def _zero_box(x: Unit, y: Unit, w: Unit = 0.0) -> Box:
    return Box(x, y, max(0.0, w), 0.0)


def _clean_text(text: str | None) -> str:
    return str(text or "").strip()


def _estimate_text_fit(
    text: str,
    *,
    width: Unit,
    min_font_size: int,
    max_font_size: int,
    max_lines: int | None,
    line_spacing: float = 1.15,
    prefer_single_line: bool = False,
) -> TextFit | None:
    text = _clean_text(text)
    if not text or width <= 0:
        return None
    return fit_text(
        text,
        width,
        10.0,
        min_font_size=min_font_size,
        max_font_size=max_font_size,
        line_spacing=line_spacing,
        prefer_single_line=prefer_single_line,
        max_lines=max_lines,
    )


def _reserve_text_height(
    text: str,
    *,
    width: Unit,
    min_font_size: int,
    max_font_size: int,
    max_lines: int | None,
    min_h: Unit,
    max_h: Unit | None,
    line_spacing: float = 1.15,
    prefer_single_line: bool = False,
    extra_pad: Unit = 0.04,
) -> tuple[Unit, TextFit | None]:
    fit = _estimate_text_fit(
        text,
        width=width,
        min_font_size=min_font_size,
        max_font_size=max_font_size,
        max_lines=max_lines,
        line_spacing=line_spacing,
        prefer_single_line=prefer_single_line,
    )
    if fit is None:
        return 0.0, None

    height = max(min_h, fit.estimated_height + extra_pad)
    if max_h is not None:
        height = min(height, max_h)
    return max(0.0, height), fit


def _weighted_reduce(heights: dict[str, Unit], reducible: dict[str, Unit], overflow: Unit) -> dict[str, Unit]:
    """Reduce box heights proportionally, but only down to each box's minimum."""
    if overflow <= 0:
        return heights

    adjusted = dict(heights)
    remaining = float(overflow)
    # A few passes avoids one box exhausting early and leaves a stable distribution.
    for _ in range(4):
        if remaining <= 1e-6:
            break
        available_total = sum(max(0.0, adjusted[name] - reducible.get(name, adjusted[name])) for name in adjusted)
        if available_total <= 1e-6:
            break
        for name in list(adjusted.keys()):
            room = max(0.0, adjusted[name] - reducible.get(name, adjusted[name]))
            if room <= 0:
                continue
            cut = min(room, remaining * (room / available_total))
            adjusted[name] -= cut
        remaining = sum(max(0.0, adjusted[name] - reducible.get(name, adjusted[name])) for name in adjusted) - max(
            0.0,
            available_total - overflow,
        )
        # recompute actual overflow left after reductions
        current_total = sum(adjusted.values())
        min_total = sum(reducible.get(name, adjusted[name]) for name in adjusted)
        if current_total <= min_total + 1e-6:
            break

    # Final deterministic trim in priority order to absorb tiny residual overflow.
    residual = max(0.0, sum(adjusted.values()) - (sum(heights.values()) - overflow))
    if residual > 1e-6:
        for name in ("takeaway", "result", "explanation"):
            if residual <= 1e-6:
                break
            room = max(0.0, adjusted.get(name, 0.0) - reducible.get(name, adjusted.get(name, 0.0)))
            cut = min(room, residual)
            adjusted[name] = adjusted.get(name, 0.0) - cut
            residual -= cut

    return adjusted


def _step_height_for_width(
    steps_text: str,
    *,
    width: Unit,
    min_font_size: int,
    max_font_size: int,
    min_h: Unit,
    max_h: Unit | None,
    line_spacing: float = 1.14,
    extra_pad: Unit = 0.06,
) -> tuple[Unit, TextFit | None]:
    fit = _estimate_text_fit(
        steps_text,
        width=width,
        min_font_size=min_font_size,
        max_font_size=max_font_size,
        max_lines=None,
        line_spacing=line_spacing,
    )
    if fit is None:
        return 0.0, None
    height = max(min_h, fit.estimated_height + extra_pad)
    if max_h is not None:
        height = min(height, max_h)
    return max(0.0, height), fit


def _pick_two_column_widths(
    usable: Box,
    *,
    steps_text: str,
    explanation_text: str,
    result_text: str,
    takeaway_text: str,
    col_gap: Unit,
    diagram_min_share: float,
    diagram_max_share: float,
    diagram_preferred_share: float,
    min_steps_h: Unit,
) -> tuple[Unit, Unit, dict[str, TextFit], dict[str, Unit], float]:
    """Choose diagram width by looking at actual text demand, not only a fixed share."""
    diagram_min_share = clamp(diagram_min_share, 0.0, 1.0)
    diagram_max_share = clamp(diagram_max_share, diagram_min_share, 1.0)
    preferred_share = clamp(diagram_preferred_share, diagram_min_share, diagram_max_share)

    candidates = []
    # Prefer smaller diagram widths first when text is dense.
    for share in (diagram_min_share, (diagram_min_share + preferred_share) / 2.0, preferred_share, diagram_max_share):
        d_w = usable.w * share
        r_w = max(0.0, usable.w - d_w - col_gap)
        if r_w <= 0.6:
            continue

        exp_h, exp_fit = _reserve_text_height(
            explanation_text,
            width=r_w,
            min_font_size=14,
            max_font_size=18,
            max_lines=4,
            min_h=0.30,
            max_h=0.78,
            line_spacing=1.14,
        )
        result_h, result_fit = _reserve_text_height(
            result_text,
            width=r_w,
            min_font_size=13,
            max_font_size=18,
            max_lines=5,
            min_h=0.28,
            max_h=0.74,
            line_spacing=1.12,
        )
        takeaway_h, takeaway_fit = _reserve_text_height(
            takeaway_text,
            width=r_w,
            min_font_size=12,
            max_font_size=15,
            max_lines=4,
            min_h=0.24,
            max_h=0.58,
            line_spacing=1.12,
        )
        steps_h, steps_fit = _step_height_for_width(
            steps_text,
            width=r_w,
            min_font_size=11,
            max_font_size=15,
            min_h=min_steps_h,
            max_h=None,
        )
        fits = {
            name: fit
            for name, fit in {
                "explanation": exp_fit,
                "result": result_fit,
                "takeaway": takeaway_fit,
                "steps": steps_fit,
            }.items()
            if fit is not None
        }
        heights = {
            "explanation": exp_h,
            "result": result_h,
            "takeaway": takeaway_h,
            "steps": steps_h,
        }
        # Score: prefer meeting steps height first, then smaller diagram when text is dense.
        vertical_need = exp_h + result_h + takeaway_h + steps_h
        gap_count = int(exp_h > 0) + int(result_h > 0) + int(takeaway_h > 0) + int(steps_h > 0) - 1
        total_need = vertical_need + max(0, gap_count) * 0.08
        shortage = max(0.0, total_need - usable.h)
        score = shortage * 10.0 + share
        candidates.append((score, d_w, r_w, fits, heights, share))

    if not candidates:
        fallback_d_w = usable.w * preferred_share
        fallback_r_w = max(0.0, usable.w - fallback_d_w - col_gap)
        return fallback_d_w, fallback_r_w, {}, {}, preferred_share

    _, d_w, r_w, fits, heights, share = min(candidates, key=lambda item: item[0])
    return d_w, r_w, fits, heights, share


def layout_worked_example_two_column(
    outer_box: Box,
    *,
    explanation_text: str = "",
    steps_text: str = "",
    result_text: str = "",
    takeaway_text: str = "",
    top_pad: Unit = 0.16,
    bottom_pad: Unit = 0.14,
    side_pad: Unit = 0.20,
    col_gap: Unit = 0.16,
    gap: Unit = 0.08,
    diagram_min_share: float = 0.28,
    diagram_max_share: float = 0.46,
    diagram_preferred_share: float = 0.38,
    min_steps_h: Unit = 1.35,
    explanation_min_h: Unit = 0.28,
    explanation_max_h: Unit = 0.78,
    result_min_h: Unit = 0.26,
    result_max_h: Unit = 0.72,
    takeaway_min_h: Unit = 0.22,
    takeaway_max_h: Unit = 0.56,
    min_diagram_h_share: float = 0.62,
) -> WorkedExampleLayoutResult:
    usable = Box(
        outer_box.x + side_pad,
        outer_box.y + top_pad,
        max(0.0, outer_box.w - 2 * side_pad),
        max(0.0, outer_box.h - top_pad - bottom_pad),
    )
    if usable.w <= 0 or usable.h <= 0:
        empty = _zero_box(outer_box.x, outer_box.y, 0.0)
        return WorkedExampleLayoutResult(
            outer_box=outer_box,
            diagram_box=empty,
            steps_box=empty,
            result_box=empty,
            takeaway_box=empty,
            explanation_box=empty,
            text_fits={},
            mode="two_column",
            diagram_share=0.0,
        )

    diagram_w, right_w, text_fits, initial_heights, chosen_share = _pick_two_column_widths(
        usable,
        steps_text=steps_text,
        explanation_text=explanation_text,
        result_text=result_text,
        takeaway_text=takeaway_text,
        col_gap=col_gap,
        diagram_min_share=diagram_min_share,
        diagram_max_share=diagram_max_share,
        diagram_preferred_share=diagram_preferred_share,
        min_steps_h=min_steps_h,
    )

    diagram_box = Box(usable.x, usable.y, diagram_w, usable.h)
    right_x = diagram_box.right + col_gap

    exp_h = initial_heights.get("explanation", 0.0)
    steps_h = initial_heights.get("steps", 0.0)
    result_h = initial_heights.get("result", 0.0)
    takeaway_h = initial_heights.get("takeaway", 0.0)

    present_names = [name for name, h in (("explanation", exp_h), ("steps", steps_h), ("result", result_h), ("takeaway", takeaway_h)) if h > 0]
    gaps_total = max(0, len(present_names) - 1) * gap
    total_needed = exp_h + steps_h + result_h + takeaway_h + gaps_total

    min_heights = {
        "explanation": explanation_min_h if exp_h > 0 else 0.0,
        "result": result_min_h if result_h > 0 else 0.0,
        "takeaway": takeaway_min_h if takeaway_h > 0 else 0.0,
        "steps": min_steps_h if steps_h > 0 else 0.0,
    }

    # Keep steps as the priority box. Compress result/takeaway/explanation first.
    overflow = max(0.0, total_needed - usable.h)
    if overflow > 0:
        reduced = _weighted_reduce(
            {
                "explanation": exp_h,
                "result": result_h,
                "takeaway": takeaway_h,
            },
            {
                "explanation": min_heights["explanation"],
                "result": min_heights["result"],
                "takeaway": min_heights["takeaway"],
            },
            overflow,
        )
        exp_h = reduced.get("explanation", exp_h)
        result_h = reduced.get("result", result_h)
        takeaway_h = reduced.get("takeaway", takeaway_h)
        total_needed = exp_h + steps_h + result_h + takeaway_h + gaps_total

    overflow = max(0.0, total_needed - usable.h)
    if overflow > 0 and steps_h > min_heights["steps"]:
        cut = min(overflow, steps_h - min_heights["steps"])
        steps_h -= cut
        total_needed -= cut

    # If there is spare room, reward the steps box first, then the diagram height is just full-column.
    slack = max(0.0, usable.h - total_needed)
    if steps_h > 0 and slack > 0.02:
        steps_h += slack
        total_needed += slack
        slack = 0.0

    # Build the right column top-down.
    current_y = usable.y

    explanation_box = _zero_box(right_x, current_y, right_w)
    if exp_h > 0:
        explanation_box = Box(right_x, current_y, right_w, exp_h)
        current_y = explanation_box.bottom + gap

    steps_box = _zero_box(right_x, current_y, right_w)
    if steps_h > 0:
        steps_box = Box(right_x, current_y, right_w, max(0.0, steps_h))
        current_y = steps_box.bottom + (gap if result_h > 0 or takeaway_h > 0 else 0.0)

    result_box = _zero_box(right_x, current_y, right_w)
    if result_h > 0:
        result_box = Box(right_x, current_y, right_w, result_h)
        current_y = result_box.bottom + (gap if takeaway_h > 0 else 0.0)

    takeaway_box = _zero_box(right_x, current_y, right_w)
    if takeaway_h > 0:
        takeaway_box = Box(right_x, current_y, right_w, takeaway_h)

    # Keep the diagram from feeling absurdly tall when right-column content is modest.
    min_diagram_h = usable.h * clamp(min_diagram_h_share, 0.0, 1.0)
    diagram_h = max(min_diagram_h, max(explanation_box.bottom, steps_box.bottom, result_box.bottom, takeaway_box.bottom) - usable.y)
    diagram_h = min(usable.h, diagram_h)
    diagram_box = Box(usable.x, usable.y, diagram_w, diagram_h)

    diagram_share = diagram_box.w / max(outer_box.w, 1e-6)
    return WorkedExampleLayoutResult(
        outer_box=outer_box,
        diagram_box=diagram_box,
        steps_box=steps_box,
        result_box=result_box,
        takeaway_box=takeaway_box,
        explanation_box=explanation_box,
        text_fits=text_fits,
        mode="two_column",
        diagram_share=diagram_share,
    )


def layout_worked_example_top_visual(
    outer_box: Box,
    *,
    explanation_text: str = "",
    steps_text: str = "",
    result_text: str = "",
    takeaway_text: str = "",
    top_pad: Unit = 0.16,
    bottom_pad: Unit = 0.14,
    side_pad: Unit = 0.20,
    gap: Unit = 0.08,
    diagram_min_share: float = 0.26,
    diagram_max_share: float = 0.52,
    diagram_preferred_share: float = 0.34,
    min_steps_h: Unit = 1.25,
    explanation_min_h: Unit = 0.24,
    explanation_max_h: Unit = 0.62,
    result_min_h: Unit = 0.24,
    result_max_h: Unit = 0.62,
    takeaway_min_h: Unit = 0.20,
    takeaway_max_h: Unit = 0.50,
) -> WorkedExampleLayoutResult:
    usable = Box(
        outer_box.x + side_pad,
        outer_box.y + top_pad,
        max(0.0, outer_box.w - 2 * side_pad),
        max(0.0, outer_box.h - top_pad - bottom_pad),
    )
    if usable.w <= 0 or usable.h <= 0:
        empty = _zero_box(outer_box.x, outer_box.y, 0.0)
        return WorkedExampleLayoutResult(
            outer_box=outer_box,
            diagram_box=empty,
            steps_box=empty,
            result_box=empty,
            takeaway_box=empty,
            explanation_box=empty,
            text_fits={},
            mode="top_visual",
            diagram_share=0.0,
        )

    text_fits: dict[str, TextFit] = {}

    exp_h, exp_fit = _reserve_text_height(
        explanation_text,
        width=usable.w,
        min_font_size=14,
        max_font_size=18,
        max_lines=4,
        min_h=explanation_min_h,
        max_h=explanation_max_h,
        line_spacing=1.14,
    )
    result_h, result_fit = _reserve_text_height(
        result_text,
        width=usable.w,
        min_font_size=13,
        max_font_size=18,
        max_lines=5,
        min_h=result_min_h,
        max_h=result_max_h,
        line_spacing=1.12,
    )
    takeaway_h, takeaway_fit = _reserve_text_height(
        takeaway_text,
        width=usable.w,
        min_font_size=12,
        max_font_size=15,
        max_lines=4,
        min_h=takeaway_min_h,
        max_h=takeaway_max_h,
        line_spacing=1.12,
    )
    steps_h, steps_fit = _step_height_for_width(
        steps_text,
        width=usable.w,
        min_font_size=11,
        max_font_size=15,
        min_h=min_steps_h,
        max_h=None,
        line_spacing=1.14,
    )

    for name, fit in (("explanation", exp_fit), ("result", result_fit), ("takeaway", takeaway_fit), ("steps", steps_fit)):
        if fit is not None:
            text_fits[name] = fit

    present = [name for name, h in (("diagram", 1.0), ("explanation", exp_h), ("steps", steps_h), ("result", result_h), ("takeaway", takeaway_h)) if h > 0]
    gap_total = max(0, len(present) - 1) * gap

    min_diagram_h = usable.h * clamp(diagram_min_share, 0.0, 1.0)
    max_diagram_h = usable.h * clamp(diagram_max_share, diagram_min_share, 1.0)
    preferred_diagram_h = usable.h * clamp(diagram_preferred_share, diagram_min_share, diagram_max_share)

    non_diagram_h = exp_h + steps_h + result_h + takeaway_h + gap_total
    diagram_h = min(max_diagram_h, max(min_diagram_h, usable.h - (non_diagram_h - preferred_diagram_h)))

    total_needed = diagram_h + exp_h + steps_h + result_h + takeaway_h + gap_total
    overflow = max(0.0, total_needed - usable.h)
    if overflow > 0:
        reducible = {
            "diagram": min_diagram_h,
            "explanation": explanation_min_h if exp_h > 0 else 0.0,
            "result": result_min_h if result_h > 0 else 0.0,
            "takeaway": takeaway_min_h if takeaway_h > 0 else 0.0,
        }
        reduced = _weighted_reduce(
            {
                "diagram": diagram_h,
                "explanation": exp_h,
                "result": result_h,
                "takeaway": takeaway_h,
            },
            reducible,
            overflow,
        )
        diagram_h = reduced.get("diagram", diagram_h)
        exp_h = reduced.get("explanation", exp_h)
        result_h = reduced.get("result", result_h)
        takeaway_h = reduced.get("takeaway", takeaway_h)
        total_needed = diagram_h + exp_h + steps_h + result_h + takeaway_h + gap_total

    overflow = max(0.0, total_needed - usable.h)
    if overflow > 0 and steps_h > min_steps_h:
        cut = min(overflow, steps_h - min_steps_h)
        steps_h -= cut
        total_needed -= cut

    slack = max(0.0, usable.h - total_needed)
    if steps_h > 0 and slack > 0.02:
        steps_h += slack

    current_y = usable.y
    diagram_box = Box(usable.x, current_y, usable.w, max(0.0, diagram_h))
    current_y = diagram_box.bottom + gap

    explanation_box = _zero_box(usable.x, current_y, usable.w)
    if exp_h > 0:
        explanation_box = Box(usable.x, current_y, usable.w, exp_h)
        current_y = explanation_box.bottom + gap

    steps_box = _zero_box(usable.x, current_y, usable.w)
    if steps_h > 0:
        steps_box = Box(usable.x, current_y, usable.w, steps_h)
        current_y = steps_box.bottom + (gap if result_h > 0 or takeaway_h > 0 else 0.0)

    result_box = _zero_box(usable.x, current_y, usable.w)
    if result_h > 0:
        result_box = Box(usable.x, current_y, usable.w, result_h)
        current_y = result_box.bottom + (gap if takeaway_h > 0 else 0.0)

    takeaway_box = _zero_box(usable.x, current_y, usable.w)
    if takeaway_h > 0:
        takeaway_box = Box(usable.x, current_y, usable.w, takeaway_h)

    diagram_share = diagram_box.h / max(outer_box.h, 1e-6)
    return WorkedExampleLayoutResult(
        outer_box=outer_box,
        diagram_box=diagram_box,
        steps_box=steps_box,
        result_box=result_box,
        takeaway_box=takeaway_box,
        explanation_box=explanation_box,
        text_fits=text_fits,
        mode="top_visual",
        diagram_share=diagram_share,
    )


def layout_worked_example(
    outer_box: Box,
    *,
    explanation_text: str = "",
    steps_text: str = "",
    result_text: str = "",
    takeaway_text: str = "",
    layout_mode: str = "two_column",
    **kwargs,
) -> WorkedExampleLayoutResult:
    """Compute reusable boxes for worked-example slides.

    Modes:
    - ``two_column``: left diagram, right explanation/steps/result/takeaway stack
    - ``top_visual``: wide diagram at top, text stack below
    """
    mode = str(layout_mode or "two_column").strip().lower()
    if mode == "top_visual":
        return layout_worked_example_top_visual(
            outer_box,
            explanation_text=explanation_text,
            steps_text=steps_text,
            result_text=result_text,
            takeaway_text=takeaway_text,
            **kwargs,
        )

    return layout_worked_example_two_column(
        outer_box,
        explanation_text=explanation_text,
        steps_text=steps_text,
        result_text=result_text,
        takeaway_text=takeaway_text,
        **kwargs,
    )

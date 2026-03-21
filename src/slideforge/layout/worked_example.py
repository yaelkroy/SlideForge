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


def _zero_box(x: Unit, y: Unit, w: Unit) -> Box:
    return Box(x, y, max(0.0, w), 0.0)


def _estimate_text_block(
    text: str,
    *,
    width: Unit,
    min_font_size: int,
    max_font_size: int,
    max_lines: int | None,
    line_spacing: float = 1.15,
    prefer_single_line: bool = False,
) -> TextFit | None:
    text = (text or "").strip()
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


def _reserve_text_box(
    x: Unit,
    y: Unit,
    w: Unit,
    text: str,
    *,
    min_font_size: int,
    max_font_size: int,
    max_lines: int | None,
    min_h: Unit,
    max_h: Unit | None,
    line_spacing: float = 1.15,
    prefer_single_line: bool = False,
) -> tuple[Box, TextFit | None]:
    fit = _estimate_text_block(
        text,
        width=w,
        min_font_size=min_font_size,
        max_font_size=max_font_size,
        max_lines=max_lines,
        line_spacing=line_spacing,
        prefer_single_line=prefer_single_line,
    )
    if fit is None:
        return _zero_box(x, y, w), None

    h = max(min_h, fit.estimated_height)
    if max_h is not None:
        h = min(h, max_h)
    return Box(x, y, max(0.0, w), max(0.0, h)), fit


def layout_worked_example_two_column(
    outer_box: Box,
    *,
    explanation_text: str = "",
    steps_text: str = "",
    result_text: str = "",
    takeaway_text: str = "",
    top_pad: Unit = 0.18,
    bottom_pad: Unit = 0.14,
    side_pad: Unit = 0.22,
    col_gap: Unit = 0.18,
    gap: Unit = 0.08,
    diagram_min_share: float = 0.34,
    diagram_max_share: float = 0.50,
    diagram_preferred_share: float = 0.42,
    explanation_min_h: Unit = 0.28,
    explanation_max_h: Unit = 0.78,
    result_min_h: Unit = 0.34,
    result_max_h: Unit = 0.90,
    takeaway_min_h: Unit = 0.26,
    takeaway_max_h: Unit = 0.72,
) -> WorkedExampleLayoutResult:
    usable = Box(
        outer_box.x + side_pad,
        outer_box.y + top_pad,
        max(0.0, outer_box.w - 2 * side_pad),
        max(0.0, outer_box.h - top_pad - bottom_pad),
    )
    if usable.w <= 0 or usable.h <= 0:
        empty = _zero_box(usable.x, usable.y, usable.w)
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

    diagram_w = usable.w * clamp(diagram_preferred_share, diagram_min_share, diagram_max_share)
    diagram_w = clamp(diagram_w, usable.w * clamp(diagram_min_share, 0.0, 1.0), usable.w * clamp(diagram_max_share, 0.0, 1.0))
    right_w = max(0.0, usable.w - diagram_w - col_gap)

    diagram_box = Box(usable.x, usable.y, diagram_w, usable.h)
    right_x = diagram_box.right + col_gap

    text_fits: dict[str, TextFit] = {}

    explanation_box, explanation_fit = _reserve_text_box(
        right_x,
        usable.y,
        right_w,
        explanation_text,
        min_font_size=14,
        max_font_size=18,
        max_lines=4,
        min_h=explanation_min_h,
        max_h=explanation_max_h,
    )
    if explanation_fit is not None:
        text_fits["explanation"] = explanation_fit

    current_y = usable.y + explanation_box.h + (gap if explanation_box.h > 0 else 0.0)

    takeaway_box, takeaway_fit = _reserve_text_box(
        right_x,
        usable.bottom,
        right_w,
        takeaway_text,
        min_font_size=12,
        max_font_size=15,
        max_lines=3,
        min_h=takeaway_min_h,
        max_h=takeaway_max_h,
    )
    if takeaway_fit is not None:
        text_fits["takeaway"] = takeaway_fit

    result_box, result_fit = _reserve_text_box(
        right_x,
        usable.bottom,
        right_w,
        result_text,
        min_font_size=13,
        max_font_size=16,
        max_lines=4,
        min_h=result_min_h,
        max_h=result_max_h,
        line_spacing=1.12,
    )
    if result_fit is not None:
        text_fits["result"] = result_fit

    reserved_bottom_h = 0.0
    if takeaway_box.h > 0:
        reserved_bottom_h += takeaway_box.h
    if result_box.h > 0:
        reserved_bottom_h += result_box.h
    if takeaway_box.h > 0 and result_box.h > 0:
        reserved_bottom_h += gap

    remaining_h = max(0.0, usable.bottom - current_y - reserved_bottom_h - (gap if reserved_bottom_h > 0 and current_y < usable.bottom else 0.0))
    steps_box = Box(right_x, current_y, right_w, remaining_h)

    steps_fit = _estimate_text_block(
        steps_text,
        width=right_w,
        min_font_size=12,
        max_font_size=15,
        max_lines=None,
        line_spacing=1.14,
    )
    if steps_fit is not None:
        text_fits["steps"] = steps_fit

    bottom_y = steps_box.bottom + (gap if reserved_bottom_h > 0 and steps_box.h > 0 else 0.0)
    if result_box.h > 0:
        result_box = result_box.with_y(bottom_y)
        bottom_y = result_box.bottom + (gap if takeaway_box.h > 0 else 0.0)
    else:
        result_box = _zero_box(right_x, bottom_y, right_w)

    if takeaway_box.h > 0:
        takeaway_box = takeaway_box.with_y(bottom_y)
    else:
        takeaway_box = _zero_box(right_x, bottom_y, right_w)

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
    top_pad: Unit = 0.18,
    bottom_pad: Unit = 0.14,
    side_pad: Unit = 0.22,
    gap: Unit = 0.08,
    diagram_min_share: float = 0.34,
    diagram_max_share: float = 0.62,
    diagram_preferred_share: float = 0.46,
    explanation_min_h: Unit = 0.26,
    explanation_max_h: Unit = 0.70,
    result_min_h: Unit = 0.30,
    result_max_h: Unit = 0.84,
    takeaway_min_h: Unit = 0.24,
    takeaway_max_h: Unit = 0.68,
) -> WorkedExampleLayoutResult:
    usable = Box(
        outer_box.x + side_pad,
        outer_box.y + top_pad,
        max(0.0, outer_box.w - 2 * side_pad),
        max(0.0, outer_box.h - top_pad - bottom_pad),
    )
    if usable.w <= 0 or usable.h <= 0:
        empty = _zero_box(usable.x, usable.y, usable.w)
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

    explanation_box, explanation_fit = _reserve_text_box(
        usable.x,
        usable.y,
        usable.w,
        explanation_text,
        min_font_size=14,
        max_font_size=18,
        max_lines=4,
        min_h=explanation_min_h,
        max_h=explanation_max_h,
    )
    if explanation_fit is not None:
        text_fits["explanation"] = explanation_fit

    result_box, result_fit = _reserve_text_box(
        usable.x,
        usable.bottom,
        usable.w,
        result_text,
        min_font_size=13,
        max_font_size=16,
        max_lines=4,
        min_h=result_min_h,
        max_h=result_max_h,
        line_spacing=1.12,
    )
    if result_fit is not None:
        text_fits["result"] = result_fit

    takeaway_box, takeaway_fit = _reserve_text_box(
        usable.x,
        usable.bottom,
        usable.w,
        takeaway_text,
        min_font_size=12,
        max_font_size=15,
        max_lines=3,
        min_h=takeaway_min_h,
        max_h=takeaway_max_h,
    )
    if takeaway_fit is not None:
        text_fits["takeaway"] = takeaway_fit

    bottom_stack_h = 0.0
    if result_box.h > 0:
        bottom_stack_h += result_box.h
    if takeaway_box.h > 0:
        bottom_stack_h += takeaway_box.h
    if result_box.h > 0 and takeaway_box.h > 0:
        bottom_stack_h += gap

    text_reserve_h = explanation_box.h + bottom_stack_h
    if explanation_box.h > 0 and bottom_stack_h > 0:
        text_reserve_h += gap

    min_diagram_h = usable.h * clamp(diagram_min_share, 0.0, 1.0)
    max_diagram_h = usable.h * clamp(diagram_max_share, 0.0, 1.0)
    preferred_diagram_h = usable.h * clamp(diagram_preferred_share, 0.0, 1.0)

    diagram_h = min(preferred_diagram_h, max(0.0, usable.h - text_reserve_h - gap))
    diagram_h = clamp(diagram_h, min_diagram_h, max_diagram_h)

    # If reserved text is too tall, let the diagram shrink below preferred size first,
    # but do not collapse it below the configured minimum share.
    free_for_steps = usable.h - diagram_h - text_reserve_h
    if free_for_steps < gap:
        diagram_h = max(min_diagram_h, diagram_h - (gap - free_for_steps))

    diagram_box = Box(usable.x, usable.y, usable.w, max(0.0, diagram_h))
    current_y = diagram_box.bottom + (gap if diagram_box.h > 0 else 0.0)

    if explanation_box.h > 0:
        explanation_box = explanation_box.with_y(current_y)
        current_y = explanation_box.bottom + gap
    else:
        explanation_box = _zero_box(usable.x, current_y, usable.w)

    reserved_bottom_h = 0.0
    if result_box.h > 0:
        reserved_bottom_h += result_box.h
    if takeaway_box.h > 0:
        reserved_bottom_h += takeaway_box.h
    if result_box.h > 0 and takeaway_box.h > 0:
        reserved_bottom_h += gap

    steps_h = max(0.0, usable.bottom - current_y - reserved_bottom_h)
    steps_box = Box(usable.x, current_y, usable.w, steps_h)

    steps_fit = _estimate_text_block(
        steps_text,
        width=usable.w,
        min_font_size=12,
        max_font_size=15,
        max_lines=None,
        line_spacing=1.14,
    )
    if steps_fit is not None:
        text_fits["steps"] = steps_fit

    bottom_y = steps_box.bottom + (gap if reserved_bottom_h > 0 and steps_box.h > 0 else 0.0)
    if result_box.h > 0:
        result_box = result_box.with_y(bottom_y)
        bottom_y = result_box.bottom + (gap if takeaway_box.h > 0 else 0.0)
    else:
        result_box = _zero_box(usable.x, bottom_y, usable.w)

    if takeaway_box.h > 0:
        takeaway_box = takeaway_box.with_y(bottom_y)
    else:
        takeaway_box = _zero_box(usable.x, bottom_y, usable.w)

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
    """
    Compute reusable layout boxes for worked-example slides.

    Supported modes:
    - "two_column": left diagram, right derivation stack
    - "top_visual": top diagram, lower derivation stack
    """
    if layout_mode == "top_visual":
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

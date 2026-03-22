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


@dataclass(frozen=True)
class _SectionSpec:
    key: str
    text: str
    min_font: int
    max_font: int
    max_lines: int | None
    min_h: Unit
    max_h: Unit | None
    line_spacing: float = 1.14
    extra_pad: Unit = 0.04
    priority: int = 0  # lower means shrink later


def _clean(text: str | None) -> str:
    return str(text or "").strip()


def _zero_box(x: Unit, y: Unit, w: Unit = 0.0) -> Box:
    return Box(x, y, max(0.0, w), 0.0)


def _usable_box(outer: Box, *, top_pad: Unit, bottom_pad: Unit, side_pad: Unit) -> Box:
    return Box(
        outer.x + side_pad,
        outer.y + top_pad,
        max(0.0, outer.w - 2 * side_pad),
        max(0.0, outer.h - top_pad - bottom_pad),
    )


def _fit(text: str, *, width: Unit, min_font: int, max_font: int, max_lines: int | None, line_spacing: float) -> TextFit | None:
    text = _clean(text)
    if not text or width <= 0:
        return None
    return fit_text(
        text,
        width,
        10.0,
        min_font_size=min_font,
        max_font_size=max_font,
        max_lines=max_lines,
        line_spacing=line_spacing,
    )


def _measure(spec: _SectionSpec, *, width: Unit) -> tuple[Unit, TextFit | None]:
    fit = _fit(
        spec.text,
        width=width,
        min_font=spec.min_font,
        max_font=spec.max_font,
        max_lines=spec.max_lines,
        line_spacing=spec.line_spacing,
    )
    if fit is None:
        return 0.0, None
    height = max(spec.min_h, fit.estimated_height + spec.extra_pad)
    if spec.max_h is not None:
        height = min(height, spec.max_h)
    return max(0.0, height), fit


def _reduce_to_fit(
    heights: dict[str, Unit],
    mins: dict[str, Unit],
    *,
    overflow: Unit,
    priority: dict[str, int],
) -> dict[str, Unit]:
    if overflow <= 0:
        return dict(heights)

    adjusted = dict(heights)
    remaining = float(overflow)
    # Higher priority value shrinks first.
    keys = sorted(adjusted, key=lambda key: priority.get(key, 0), reverse=True)
    while remaining > 1e-6:
        changed = False
        for key in keys:
            room = max(0.0, adjusted.get(key, 0.0) - mins.get(key, 0.0))
            if room <= 0:
                continue
            cut = min(room, remaining)
            adjusted[key] -= cut
            remaining -= cut
            changed = True
            if remaining <= 1e-6:
                break
        if not changed:
            break
    return adjusted


def _assemble_vertical_boxes(
    x: Unit,
    y: Unit,
    w: Unit,
    gap: Unit,
    heights: dict[str, Unit],
) -> dict[str, Box]:
    boxes: dict[str, Box] = {}
    current_y = y
    order = ["explanation", "steps", "result", "takeaway"]
    for idx, key in enumerate(order):
        h = max(0.0, heights.get(key, 0.0))
        boxes[key] = _zero_box(x, current_y, w)
        if h > 0:
            boxes[key] = Box(x, current_y, w, h)
            current_y = boxes[key].bottom
            if any(max(0.0, heights.get(next_key, 0.0)) > 0 for next_key in order[idx + 1 :]):
                current_y += gap
    return boxes


def _content_specs(
    *,
    explanation_text: str,
    steps_text: str,
    result_text: str,
    takeaway_text: str,
    explanation_min_h: Unit,
    explanation_max_h: Unit,
    result_min_h: Unit,
    result_max_h: Unit,
    takeaway_min_h: Unit,
    takeaway_max_h: Unit,
    min_steps_h: Unit,
) -> list[_SectionSpec]:
    return [
        _SectionSpec("explanation", explanation_text, 14, 18, 4, explanation_min_h, explanation_max_h, 1.14, 0.04, 2),
        _SectionSpec("steps", steps_text, 11, 15, None, min_steps_h, None, 1.14, 0.06, 0),
        _SectionSpec("result", result_text, 13, 18, 5, result_min_h, result_max_h, 1.12, 0.04, 3),
        _SectionSpec("takeaway", takeaway_text, 12, 15, 4, takeaway_min_h, takeaway_max_h, 1.12, 0.04, 4),
    ]


def _evaluate_column(
    *,
    width: Unit,
    specs: list[_SectionSpec],
    available_h: Unit,
    gap: Unit,
) -> tuple[dict[str, Unit], dict[str, TextFit]]:
    heights: dict[str, Unit] = {}
    fits: dict[str, TextFit] = {}
    present = 0
    for spec in specs:
        h, fit = _measure(spec, width=width)
        heights[spec.key] = h
        if fit is not None:
            fits[spec.key] = fit
            present += 1
    gaps_total = max(0, present - 1) * gap
    total = sum(heights.values()) + gaps_total
    mins = {spec.key: (spec.min_h if heights.get(spec.key, 0.0) > 0 else 0.0) for spec in specs}
    priorities = {spec.key: spec.priority for spec in specs}
    if total > available_h:
        heights = _reduce_to_fit(heights, mins, overflow=total - available_h, priority=priorities)
        total = sum(heights.values()) + gaps_total
    slack = max(0.0, available_h - total)
    if heights.get("steps", 0.0) > 0 and slack > 0.02:
        heights["steps"] += slack
    return heights, fits


def _choose_two_column_share(
    *,
    usable: Box,
    col_gap: Unit,
    gap: Unit,
    specs: list[_SectionSpec],
    diagram_min_share: float,
    diagram_max_share: float,
    diagram_preferred_share: float,
) -> tuple[float, Unit, Unit, dict[str, Unit], dict[str, TextFit]]:
    min_share = clamp(diagram_min_share, 0.0, 1.0)
    max_share = clamp(diagram_max_share, min_share, 1.0)
    pref_share = clamp(diagram_preferred_share, min_share, max_share)

    step = 0.02
    candidates: list[float] = []
    probe = min_share
    while probe <= max_share + 1e-9:
        candidates.append(round(probe, 4))
        probe += step
    for extra in (min_share, pref_share, max_share, (min_share + pref_share) / 2.0, (pref_share + max_share) / 2.0):
        candidates.append(round(clamp(extra, min_share, max_share), 4))
    candidates = sorted(set(candidates))

    best: tuple[float, float, Unit, Unit, dict[str, Unit], dict[str, TextFit]] | None = None
    for share in candidates:
        diagram_w = usable.w * share
        right_w = max(0.0, usable.w - diagram_w - col_gap)
        if right_w <= 0.8:
            continue
        heights, fits = _evaluate_column(width=right_w, specs=specs, available_h=usable.h, gap=gap)
        natural_total = 0.0
        present = 0
        for spec in specs:
            h, _ = _measure(spec, width=right_w)
            natural_total += h
            if h > 0:
                present += 1
        natural_total += max(0, present - 1) * gap
        shortage = max(0.0, natural_total - usable.h)

        steps_fit = fits.get("steps")
        steps_font_penalty = 0.0
        steps_height_penalty = 0.0
        if steps_fit is not None:
            max_steps_font = next((spec.max_font for spec in specs if spec.key == "steps"), steps_fit.font_size)
            steps_font_penalty = max(0.0, float(max_steps_font - steps_fit.font_size)) * 16.0
            steps_ratio = steps_fit.estimated_height / max(usable.h, 1e-6)
            if steps_ratio < 0.54:
                steps_height_penalty += (0.54 - steps_ratio) * 22.0
            elif steps_ratio > 0.93:
                steps_height_penalty += (steps_ratio - 0.93) * 70.0

        share_reward = share * 18.0
        pref_penalty = abs(share - pref_share) * 6.0
        score = shortage * 1200.0 + steps_font_penalty + steps_height_penalty + pref_penalty - share_reward
        candidate = (score, share, diagram_w, right_w, heights, fits)
        if best is None or candidate[0] < best[0]:
            best = candidate
    if best is None:
        right_w = max(0.0, usable.w - usable.w * pref_share - col_gap)
        return pref_share, usable.w * pref_share, right_w, {}, {}
    _, share, diagram_w, right_w, heights, fits = best
    return share, diagram_w, right_w, heights, fits


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
    usable = _usable_box(outer_box, top_pad=top_pad, bottom_pad=bottom_pad, side_pad=side_pad)
    if usable.w <= 0 or usable.h <= 0:
        empty = _zero_box(outer_box.x, outer_box.y)
        return WorkedExampleLayoutResult(outer_box, empty, empty, empty, empty, empty, {}, "two_column", 0.0)

    specs = _content_specs(
        explanation_text=explanation_text,
        steps_text=steps_text,
        result_text=result_text,
        takeaway_text=takeaway_text,
        explanation_min_h=explanation_min_h,
        explanation_max_h=explanation_max_h,
        result_min_h=result_min_h,
        result_max_h=result_max_h,
        takeaway_min_h=takeaway_min_h,
        takeaway_max_h=takeaway_max_h,
        min_steps_h=min_steps_h,
    )
    share, diagram_w, right_w, heights, fits = _choose_two_column_share(
        usable=usable,
        col_gap=col_gap,
        gap=gap,
        specs=specs,
        diagram_min_share=diagram_min_share,
        diagram_max_share=diagram_max_share,
        diagram_preferred_share=diagram_preferred_share,
    )
    right_x = usable.x + diagram_w + col_gap
    boxes = _assemble_vertical_boxes(right_x, usable.y, right_w, gap, heights)

    content_bottom = max([usable.y] + [box.bottom for box in boxes.values() if box.h > 0])
    min_diagram_h = usable.h * clamp(min_diagram_h_share, 0.0, 1.0)
    diagram_h = min(usable.h, max(min_diagram_h, content_bottom - usable.y))
    diagram_box = Box(usable.x, usable.y, diagram_w, diagram_h)

    return WorkedExampleLayoutResult(
        outer_box=outer_box,
        diagram_box=diagram_box,
        steps_box=boxes["steps"],
        result_box=boxes["result"],
        takeaway_box=boxes["takeaway"],
        explanation_box=boxes["explanation"],
        text_fits=fits,
        mode="two_column",
        diagram_share=share,
    )


def layout_worked_example_two_column_bottom_result(
    outer_box: Box,
    *,
    explanation_text: str = "",
    steps_text: str = "",
    result_text: str = "",
    takeaway_text: str = "",
    top_pad: Unit = 0.16,
    bottom_pad: Unit = 0.14,
    side_pad: Unit = 0.20,
    col_gap: Unit = 0.18,
    gap: Unit = 0.10,
    diagram_min_share: float = 0.32,
    diagram_max_share: float = 0.56,
    diagram_preferred_share: float = 0.42,
    min_steps_h: Unit = 1.35,
    explanation_min_h: Unit = 0.28,
    explanation_max_h: Unit = 0.78,
    result_min_h: Unit = 0.26,
    result_max_h: Unit = 0.72,
    takeaway_min_h: Unit = 0.22,
    takeaway_max_h: Unit = 0.56,
    steps_min_font: int = 11,
    steps_max_font: int = 15,
    result_min_font: int = 13,
    result_max_font: int = 18,
) -> WorkedExampleLayoutResult:
    usable = _usable_box(outer_box, top_pad=top_pad, bottom_pad=bottom_pad, side_pad=side_pad)
    if usable.w <= 0 or usable.h <= 0:
        empty = _zero_box(outer_box.x, outer_box.y)
        return WorkedExampleLayoutResult(outer_box, empty, empty, empty, empty, empty, {}, "two_column_bottom_result", 0.0)

    specs = _content_specs(
        explanation_text=explanation_text,
        steps_text=steps_text,
        result_text=result_text,
        takeaway_text=takeaway_text,
        explanation_min_h=explanation_min_h,
        explanation_max_h=explanation_max_h,
        result_min_h=result_min_h,
        result_max_h=result_max_h,
        takeaway_min_h=takeaway_min_h,
        takeaway_max_h=takeaway_max_h,
        min_steps_h=min_steps_h,
        steps_min_font=steps_min_font,
        steps_max_font=steps_max_font,
        result_min_font=result_min_font,
        result_max_font=result_max_font,
    )
    spec_map = {spec.key: spec for spec in specs}

    result_h = 0.0
    result_fit = None
    if _clean(result_text):
        result_h, result_fit = _measure(spec_map["result"], width=usable.w)
    takeaway_h = 0.0
    takeaway_fit = None
    if _clean(takeaway_text):
        takeaway_h, takeaway_fit = _measure(spec_map["takeaway"], width=usable.w)

    reserved_bottom = 0.0
    if result_h > 0:
        reserved_bottom += result_h
    if takeaway_h > 0:
        reserved_bottom += takeaway_h
        if result_h > 0:
            reserved_bottom += gap
    if reserved_bottom > 0:
        reserved_bottom += gap

    top_h = max(min_steps_h, usable.h - reserved_bottom)
    if top_h > usable.h:
        top_h = usable.h
        result_h = 0.0
        takeaway_h = 0.0
        result_fit = None
        takeaway_fit = None

    top_specs = [spec_map["explanation"], spec_map["steps"]]
    top_usable = Box(usable.x, usable.y, usable.w, top_h)
    share, diagram_w, right_w, heights, fits = _choose_two_column_share(
        usable=top_usable,
        col_gap=col_gap,
        gap=gap,
        specs=top_specs,
        diagram_min_share=diagram_min_share,
        diagram_max_share=diagram_max_share,
        diagram_preferred_share=diagram_preferred_share,
    )

    right_x = usable.x + diagram_w + col_gap
    top_boxes = _assemble_vertical_boxes(right_x, usable.y, right_w, gap, heights)
    diagram_box = Box(usable.x, usable.y, diagram_w, top_h)

    current_y = usable.y + top_h
    if result_h > 0 or takeaway_h > 0:
        current_y += gap
    result_box = _zero_box(usable.x, current_y, usable.w)
    if result_h > 0:
        result_box = Box(usable.x, current_y, usable.w, result_h)
        current_y = result_box.bottom
    if takeaway_h > 0 and result_h > 0:
        current_y += gap
    takeaway_box = _zero_box(usable.x, current_y, usable.w)
    if takeaway_h > 0:
        takeaway_box = Box(usable.x, current_y, usable.w, takeaway_h)

    text_fits: dict[str, TextFit] = dict(fits)
    if result_fit is not None:
        text_fits["result"] = result_fit
    if takeaway_fit is not None:
        text_fits["takeaway"] = takeaway_fit

    return WorkedExampleLayoutResult(
        outer_box=outer_box,
        diagram_box=diagram_box,
        steps_box=top_boxes["steps"],
        result_box=result_box,
        takeaway_box=takeaway_box,
        explanation_box=top_boxes["explanation"],
        text_fits=text_fits,
        mode="two_column_bottom_result",
        diagram_share=share,
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
    usable = _usable_box(outer_box, top_pad=top_pad, bottom_pad=bottom_pad, side_pad=side_pad)
    if usable.w <= 0 or usable.h <= 0:
        empty = _zero_box(outer_box.x, outer_box.y)
        return WorkedExampleLayoutResult(outer_box, empty, empty, empty, empty, empty, {}, "top_visual", 0.0)

    specs = _content_specs(
        explanation_text=explanation_text,
        steps_text=steps_text,
        result_text=result_text,
        takeaway_text=takeaway_text,
        explanation_min_h=explanation_min_h,
        explanation_max_h=explanation_max_h,
        result_min_h=result_min_h,
        result_max_h=result_max_h,
        takeaway_min_h=takeaway_min_h,
        takeaway_max_h=takeaway_max_h,
        min_steps_h=min_steps_h,
    )

    content_heights, fits = _evaluate_column(width=usable.w, specs=specs, available_h=usable.h, gap=gap)
    text_total = sum(content_heights.values()) + max(0, sum(1 for v in content_heights.values() if v > 0) - 1) * gap

    min_diagram_h = usable.h * clamp(diagram_min_share, 0.0, 1.0)
    max_diagram_h = usable.h * clamp(diagram_max_share, clamp(diagram_min_share, 0.0, 1.0), 1.0)
    pref_diagram_h = usable.h * clamp(diagram_preferred_share, clamp(diagram_min_share, 0.0, 1.0), clamp(diagram_max_share, clamp(diagram_min_share, 0.0, 1.0), 1.0))
    available_for_diagram = max(0.0, usable.h - text_total - gap)
    diagram_h = max(min_diagram_h, min(max_diagram_h, max(available_for_diagram, pref_diagram_h)))

    total = diagram_h + (gap if text_total > 0 and diagram_h > 0 else 0.0) + text_total
    if total > usable.h:
        overflow = total - usable.h
        mins = {
            "diagram": min_diagram_h,
            "explanation": explanation_min_h if content_heights.get("explanation", 0.0) > 0 else 0.0,
            "result": result_min_h if content_heights.get("result", 0.0) > 0 else 0.0,
            "takeaway": takeaway_min_h if content_heights.get("takeaway", 0.0) > 0 else 0.0,
        }
        priorities = {"diagram": 3, "explanation": 2, "result": 4, "takeaway": 5}
        reduced = _reduce_to_fit(
            {
                "diagram": diagram_h,
                "explanation": content_heights.get("explanation", 0.0),
                "result": content_heights.get("result", 0.0),
                "takeaway": content_heights.get("takeaway", 0.0),
            },
            mins,
            overflow=overflow,
            priority=priorities,
        )
        diagram_h = reduced["diagram"]
        content_heights["explanation"] = reduced["explanation"]
        content_heights["result"] = reduced["result"]
        content_heights["takeaway"] = reduced["takeaway"]
        text_total = sum(content_heights.values()) + max(0, sum(1 for v in content_heights.values() if v > 0) - 1) * gap

    text_start_y = usable.y + diagram_h + (gap if text_total > 0 and diagram_h > 0 else 0.0)
    boxes = _assemble_vertical_boxes(usable.x, text_start_y, usable.w, gap, content_heights)
    diagram_box = Box(usable.x, usable.y, usable.w, max(0.0, diagram_h))

    return WorkedExampleLayoutResult(
        outer_box=outer_box,
        diagram_box=diagram_box,
        steps_box=boxes["steps"],
        result_box=boxes["result"],
        takeaway_box=boxes["takeaway"],
        explanation_box=boxes["explanation"],
        text_fits=fits,
        mode="top_visual",
        diagram_share=diagram_box.h / max(outer_box.h, 1e-6),
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
    if mode == "two_column_bottom_result":
        return layout_worked_example_two_column_bottom_result(
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


__all__ = [
    "WorkedExampleLayoutResult",
    "layout_worked_example",
    "layout_worked_example_two_column",
    "layout_worked_example_two_column_bottom_result",
    "layout_worked_example_top_visual",
]

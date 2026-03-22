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
    steps_min_font: int = 11,
    steps_max_font: int = 15,
    result_min_font: int = 13,
    result_max_font: int = 18,
) -> list[_SectionSpec]:
    return [
        _SectionSpec("explanation", explanation_text, 14, 18, 4, explanation_min_h, explanation_max_h, 1.14, 0.04, 2),
        _SectionSpec("steps", steps_text, steps_min_font, steps_max_font, None, min_steps_h, None, 1.14, 0.06, 0),
        _SectionSpec("result", result_text, result_min_font, result_max_font, 5, result_min_h, result_max_h, 1.12, 0.04, 3),
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




def _minimal_width_for_target_font(
    text: str,
    *,
    target_font: int,
    height: Unit,
    min_width: Unit,
    max_width: Unit,
    max_lines: int | None,
    line_spacing: float,
) -> Unit:
    text = _clean(text)
    if not text:
        return max(0.0, min_width)

    lo = max(0.10, min_width)
    hi = max(lo, max_width)
    height = max(0.10, height)

    trial = fit_text(
        text,
        hi,
        height,
        min_font_size=target_font,
        max_font_size=target_font,
        max_lines=max_lines,
        line_spacing=line_spacing,
    )
    if not trial.fits:
        return hi

    for _ in range(18):
        mid = (lo + hi) / 2.0
        probe = fit_text(
            text,
            mid,
            height,
            min_font_size=target_font,
            max_font_size=target_font,
            max_lines=max_lines,
            line_spacing=line_spacing,
        )
        if probe.fits:
            hi = mid
        else:
            lo = mid
    return hi

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
    candidates = [min_share, (min_share + pref_share) / 2.0, pref_share, max_share]

    best: tuple[float, float, Unit, Unit, dict[str, Unit], dict[str, TextFit]] | None = None
    for share in candidates:
        diagram_w = usable.w * share
        right_w = max(0.0, usable.w - diagram_w - col_gap)
        if right_w <= 0.6:
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
        score = shortage * 100.0 + abs(share - pref_share) * 10.0 + share
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
    steps_min_font: int = 11,
    steps_max_font: int = 15,
    result_min_font: int = 13,
    result_max_font: int = 18,
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
        steps_min_font=steps_min_font,
        steps_max_font=steps_max_font,
        result_min_font=result_min_font,
        result_max_font=result_max_font,
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
    col_gap: Unit = 0.16,
    gap: Unit = 0.08,
    diagram_min_share: float = 0.30,
    diagram_max_share: float = 0.56,
    diagram_preferred_share: float = 0.40,
    min_steps_h: Unit = 1.35,
    explanation_min_h: Unit = 0.28,
    explanation_max_h: Unit = 0.78,
    result_min_h: Unit = 0.30,
    result_max_h: Unit = 0.88,
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
    if result_text.strip():
        result_h, result_fit = _measure(spec_map['result'], width=usable.w)
    result_gap = gap if result_h > 0 else 0.0
    top_h = max(0.0, usable.h - result_h - result_gap)

    top_specs = [spec_map['explanation'], spec_map['steps'], spec_map['takeaway']]

    min_share = clamp(diagram_min_share, 0.0, 1.0)
    max_share = clamp(diagram_max_share, min_share, 1.0)
    pref_share = clamp(diagram_preferred_share, min_share, max_share)

    right_min_width = 3.05
    if explanation_text.strip():
        right_min_width = max(
            right_min_width,
            _minimal_width_for_target_font(
                explanation_text,
                target_font=min(18, max(15, spec_map['explanation'].max_font)),
                height=max(0.20, explanation_max_h),
                min_width=2.80,
                max_width=max(2.80, usable.w - usable.w * min_share - col_gap),
                max_lines=4,
                line_spacing=spec_map['explanation'].line_spacing,
            ),
        )
    if steps_text.strip():
        right_min_width = max(
            right_min_width,
            _minimal_width_for_target_font(
                steps_text,
                target_font=max(steps_min_font, min(steps_max_font, steps_max_font)),
                height=max(min_steps_h, top_h),
                min_width=3.10,
                max_width=max(3.10, usable.w - usable.w * min_share - col_gap),
                max_lines=None,
                line_spacing=spec_map['steps'].line_spacing,
            ),
        )
    if takeaway_text.strip():
        right_min_width = max(
            right_min_width,
            _minimal_width_for_target_font(
                takeaway_text,
                target_font=14,
                height=max(0.20, takeaway_max_h),
                min_width=2.80,
                max_width=max(2.80, usable.w - usable.w * min_share - col_gap),
                max_lines=4,
                line_spacing=spec_map['takeaway'].line_spacing,
            ),
        )

    max_right_w = max(3.10, usable.w - usable.w * min_share - col_gap)
    min_right_w = min(max_right_w, max(3.70, right_min_width + 0.04))
    preferred_right_w = min(max_right_w, max(min_right_w, usable.w * (1.0 - pref_share) - col_gap))

    candidate_right_ws = [
        min_right_w,
        min(max_right_w, min_right_w + 0.18),
        preferred_right_w,
        min(max_right_w, usable.w * (1.0 - ((min_share + pref_share) / 2.0)) - col_gap),
        min(max_right_w, usable.w * (1.0 - max_share) - col_gap),
    ]

    unique_candidates: list[Unit] = []
    seen: set[int] = set()
    for width in candidate_right_ws:
        clamped = max(min_right_w, min(max_right_w, width))
        key = int(round(clamped * 1000))
        if key in seen:
            continue
        seen.add(key)
        unique_candidates.append(clamped)

    best = None
    for right_w in unique_candidates:
        diagram_w = max(0.0, usable.w - right_w - col_gap)
        if diagram_w <= 2.40:
            continue
        heights, fits = _evaluate_column(width=right_w, specs=top_specs, available_h=top_h, gap=gap)
        natural_total = 0.0
        present = 0
        for spec in top_specs:
            h, _ = _measure(spec, width=right_w)
            natural_total += h
            if h > 0:
                present += 1
        natural_total += max(0, present - 1) * gap
        shortage = max(0.0, natural_total - top_h)
        diagram_share = diagram_w / max(usable.w, 1e-6)
        width_excess = max(0.0, right_w - min_right_w)
        score = shortage * 100.0 + abs(right_w - preferred_right_w) * 6.0 + width_excess * 0.8 + abs(diagram_share - pref_share) * 16.0
        candidate = (score, diagram_w, right_w, heights, fits)
        if best is None or candidate[0] < best[0]:
            best = candidate

    if best is None:
        right_w = max_right_w
        diagram_w = max(0.0, usable.w - right_w - col_gap)
        heights, fits = _evaluate_column(width=right_w, specs=top_specs, available_h=top_h, gap=gap)
    else:
        _, diagram_w, right_w, heights, fits = best

    right_x = usable.x + diagram_w + col_gap
    boxes = _assemble_vertical_boxes(right_x, usable.y, right_w, gap, heights)
    result_box = _zero_box(usable.x, usable.y + top_h + result_gap, usable.w)
    if result_h > 0:
        result_box = Box(usable.x, usable.y + top_h + result_gap, usable.w, result_h)
        if result_fit is not None:
            fits['result'] = result_fit

    return WorkedExampleLayoutResult(
        outer_box=outer_box,
        diagram_box=Box(usable.x, usable.y, diagram_w, top_h),
        steps_box=boxes['steps'],
        result_box=result_box,
        takeaway_box=boxes['takeaway'],
        explanation_box=boxes['explanation'],
        text_fits=fits,
        mode='two_column_bottom_result',
        diagram_share=diagram_w / max(outer_box.w, 1e-6),
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
    steps_min_font: int = 11,
    steps_max_font: int = 15,
    result_min_font: int = 13,
    result_max_font: int = 18,
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
        steps_min_font=steps_min_font,
        steps_max_font=steps_max_font,
        result_min_font=result_min_font,
        result_max_font=result_max_font,
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

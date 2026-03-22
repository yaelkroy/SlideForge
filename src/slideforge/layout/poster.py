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


@dataclass(frozen=True)
class _PosterModeConfig:
    dense_math: bool = False
    compact_concept: bool = False
    reserve_formula_first: bool = False
    formulas_before_bullets: bool = False
    keep_readable_keys: tuple[str, ...] = ("explanation", "takeaway")
    visual_inset_x: float = 0.06
    visual_width_inset: float = 0.12
    band_gap: float = 0.08


def _clean(text: str) -> str:
    return str(text or "").strip()


def _line_count(text: str) -> int:
    text = _clean(text)
    if not text:
        return 0
    return max(1, len(text.splitlines()))


def _make_text_specs(
    *,
    explanation: str,
    bullets_text: str,
    formulas_text: str,
    note_text: str,
    takeaway_text: str,
    cfg: _PosterModeConfig,
) -> list[TextBlockSpec]:
    if cfg.compact_concept:
        explanation_max = 2
        bullets_max = 2
        formulas_max = max(2, min(3, _line_count(formulas_text) + 1))
        takeaway_max = 2
    else:
        explanation_max = 4 if cfg.dense_math else 3
        bullets_max = 4 if cfg.dense_math else 3
        formulas_max = max(3, min(6 if cfg.dense_math else 4, _line_count(formulas_text) + 1))
        takeaway_max = 3 if cfg.dense_math else 2

    specs: list[TextBlockSpec] = []

    def add_if_text(key: str, text: str, **kwargs) -> None:
        text = _clean(text)
        if text:
            specs.append(TextBlockSpec(key=key, text=text, **kwargs))

    add_if_text(
        "explanation",
        explanation,
        min_font_size=16 if (cfg.dense_math or cfg.compact_concept) else 15,
        max_font_size=19 if cfg.compact_concept else 18,
        max_lines=explanation_max,
    )

    secondary_specs: list[TextBlockSpec] = []
    if _clean(bullets_text):
        secondary_specs.append(
            TextBlockSpec(
                key="bullets",
                text=_clean(bullets_text),
                min_font_size=13,
                max_font_size=15,
                max_lines=bullets_max,
            )
        )
    if _clean(formulas_text):
        secondary_specs.append(
            TextBlockSpec(
                key="formulas",
                text=_clean(formulas_text),
                min_font_size=13 if (cfg.reserve_formula_first or cfg.dense_math or cfg.compact_concept) else 12,
                max_font_size=16 if (cfg.reserve_formula_first or cfg.dense_math) else (15 if cfg.compact_concept else 14),
                max_lines=formulas_max,
                line_spacing=1.10 if (cfg.dense_math or cfg.compact_concept) else 1.14,
            )
        )

    if cfg.formulas_before_bullets:
        secondary_specs.sort(key=lambda s: 0 if s.key == "formulas" else 1)
    specs.extend(secondary_specs)

    add_if_text(
        "takeaway",
        takeaway_text,
        min_font_size=13 if (cfg.dense_math or cfg.compact_concept) else 12,
        max_font_size=15 if (cfg.dense_math or cfg.compact_concept) else 14,
        max_lines=takeaway_max,
        bold=True,
    )
    add_if_text(
        "note",
        note_text,
        min_font_size=12,
        max_font_size=13 if cfg.dense_math else 14,
        max_lines=1 if cfg.compact_concept else 2,
    )
    return specs


def _estimate_block_height(spec: TextBlockSpec, width: Unit, extra_pad: float = 0.05) -> float:
    if not _clean(spec.text) or width <= 0:
        return 0.0
    probe = fit_text(
        spec.text,
        width,
        100.0,
        min_font_size=spec.min_font_size,
        max_font_size=spec.max_font_size,
        line_spacing=spec.line_spacing,
        prefer_single_line=spec.prefer_single_line,
        max_lines=spec.max_lines,
    )
    if probe is None:
        return line_height_inches(spec.min_font_size, spec.line_spacing) + extra_pad
    return probe.estimated_height + extra_pad


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
    heights: list[float] = []
    for spec in specs:
        if not _clean(spec.text):
            continue
        if (reserve_formula_first and spec.key == "formulas") or spec.key in readable:
            heights.append(_estimate_block_height(spec, width))
        else:
            heights.append(max(line_height_inches(spec.min_font_size, spec.line_spacing) + 0.04, 0.16))
    if not heights:
        return 0.0
    return sum(heights) + gap * max(0, len(heights) - 1)


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
    visual_box = Box(outer_box.x + side_pad, outer_box.y + top_pad, max(0.0, outer_box.w - 2 * side_pad), 0.0)
    return PosterLayoutResult(outer_box=outer_box, visual_box=visual_box, text_boxes={}, text_fits={}, visual_share=0.0)


def _layout_poster(
    outer_box: Box,
    *,
    specs: Sequence[TextBlockSpec],
    top_pad: Unit,
    bottom_pad: Unit,
    side_pad: Unit,
    gap: Unit,
    visual_min_share: float,
    visual_max_share: float,
    preferred_visual_share: float,
    cfg: _PosterModeConfig,
) -> PosterLayoutResult:
    usable_h = max(0.0, outer_box.h - top_pad - bottom_pad)
    if usable_h <= 0:
        return _empty_result(outer_box, top_pad=top_pad, side_pad=side_pad)

    inner_w = max(0.0, outer_box.w - 2 * side_pad)
    min_visual_h = usable_h * clamp(visual_min_share, 0.0, 1.0)
    max_visual_h = usable_h * clamp(visual_max_share, 0.0, 1.0)
    visual_h = clamp(usable_h * preferred_visual_share, min_visual_h, max_visual_h)

    if cfg.reserve_formula_first:
        reserved = _estimate_reserved_text_height(
            specs,
            width=inner_w,
            gap=gap,
            reserve_formula_first=True,
            keep_readable_keys=cfg.keep_readable_keys,
        )
        visual_h = clamp(usable_h - reserved - gap, min_visual_h, max_visual_h)

    best_penalty = float("inf")
    best_visual_h = visual_h
    best_stack = None

    for _ in range(7):
        text_box = _text_container(
            outer_box,
            top_pad=top_pad,
            bottom_pad=bottom_pad,
            side_pad=side_pad,
            visual_h=visual_h,
            gap=gap,
        )
        stack = layout_vertical_stack(text_box, list(specs), gap=gap, top_pad=0.0, bottom_pad=0.0)
        readable_failures = sum(
            1
            for key in cfg.keep_readable_keys
            if stack.text_fits.get(key) is not None and not stack.text_fits[key].fits
        )
        overflow = max(0.0, stack.used_height - text_box.h)
        underfill = max(0.0, text_box.h - stack.used_height)
        penalty = overflow + readable_failures * 0.12

        if underfill > 0.42 and visual_h < max_visual_h:
            visual_h = min(max_visual_h, visual_h + min(underfill * 0.22, 0.16))
            continue

        if penalty < best_penalty:
            best_penalty = penalty
            best_visual_h = visual_h
            best_stack = stack

        if penalty <= 0.02:
            break

        next_visual_h = max(min_visual_h, visual_h - max(0.08, penalty))
        if abs(next_visual_h - visual_h) < 1e-6:
            break
        visual_h = next_visual_h

    if best_stack is None:
        final_text_box = _text_container(
            outer_box,
            top_pad=top_pad,
            bottom_pad=bottom_pad,
            side_pad=side_pad,
            visual_h=best_visual_h,
            gap=gap,
        )
        best_stack = layout_vertical_stack(final_text_box, list(specs), gap=gap, top_pad=0.0, bottom_pad=0.0)

    visual_box = Box(
        outer_box.x + side_pad + cfg.visual_inset_x,
        outer_box.y + top_pad,
        max(0.0, outer_box.w - 2 * side_pad - cfg.visual_width_inset),
        max(0.0, best_visual_h),
    )
    final_text_box = Box(
        outer_box.x + side_pad,
        visual_box.bottom + gap,
        max(0.0, outer_box.w - 2 * side_pad),
        max(0.0, outer_box.bottom - bottom_pad - (visual_box.bottom + gap)),
    )
    final_stack = layout_vertical_stack(final_text_box, list(specs), gap=gap, top_pad=0.0, bottom_pad=0.0)
    return PosterLayoutResult(
        outer_box=outer_box,
        visual_box=visual_box,
        text_boxes=final_stack.boxes,
        text_fits=final_stack.text_fits,
        visual_share=visual_box.h / max(usable_h, 1e-6),
    )


def _compact_specs(
    *,
    explanation: str,
    bullets_text: str,
    formulas_text: str,
    note_text: str,
    takeaway_text: str,
) -> list[TextBlockSpec]:
    specs: list[TextBlockSpec] = []
    if _clean(explanation):
        specs.append(TextBlockSpec("explanation", _clean(explanation), min_font_size=15, max_font_size=18, max_lines=2, line_spacing=1.12))
    if _clean(formulas_text):
        max_lines = 3 if "\n" in formulas_text else 1
        specs.append(TextBlockSpec("formulas", _clean(formulas_text), min_font_size=12, max_font_size=15, max_lines=max_lines, line_spacing=1.08))
    if _clean(bullets_text):
        specs.append(TextBlockSpec("bullets", _clean(bullets_text), min_font_size=12, max_font_size=14, max_lines=2, line_spacing=1.10))
    if _clean(note_text):
        specs.append(TextBlockSpec("note", _clean(note_text), min_font_size=11, max_font_size=13, max_lines=1, line_spacing=1.08))
    if _clean(takeaway_text):
        specs.append(TextBlockSpec("takeaway", _clean(takeaway_text), min_font_size=12, max_font_size=14, max_lines=2, line_spacing=1.10, bold=True))
    return specs


def _layout_compact_bands(
    outer_box: Box,
    *,
    explanation: str,
    bullets_text: str,
    formulas_text: str,
    note_text: str,
    takeaway_text: str,
    top_pad: Unit,
    bottom_pad: Unit,
    gap: Unit,
    side_pad: Unit,
    visual_min_share: float,
    visual_max_share: float,
    preferred_visual_share: float,
) -> PosterLayoutResult:
    usable_h = max(0.0, outer_box.h - top_pad - bottom_pad)
    if usable_h <= 0:
        return _empty_result(outer_box, top_pad=top_pad, side_pad=side_pad)

    specs = _compact_specs(
        explanation=explanation,
        bullets_text=bullets_text,
        formulas_text=formulas_text,
        note_text=note_text,
        takeaway_text=takeaway_text,
    )
    inner_w = max(0.0, outer_box.w - 2 * side_pad)
    compact_gap = min(gap, 0.055)
    reserved = _estimate_reserved_text_height(
        specs,
        width=inner_w,
        gap=compact_gap,
        reserve_formula_first=True,
        keep_readable_keys=("explanation", "formulas", "takeaway"),
    )

    min_visual_h = usable_h * clamp(visual_min_share, 0.0, 1.0)
    max_visual_h = usable_h * clamp(visual_max_share, 0.0, 1.0)
    preferred = usable_h * preferred_visual_share
    visual_h = clamp(usable_h - reserved - compact_gap, min_visual_h, max_visual_h)
    visual_h = clamp((visual_h * 0.7) + (preferred * 0.3), min_visual_h, max_visual_h)

    text_box = Box(
        outer_box.x + side_pad,
        outer_box.y + top_pad + visual_h + compact_gap,
        inner_w,
        max(0.0, usable_h - visual_h - compact_gap),
    )
    stack = layout_vertical_stack(text_box, specs, gap=compact_gap, top_pad=0.0, bottom_pad=0.0)

    # If formulas did not fit, protect them by trimming the visual more aggressively.
    if stack.text_fits.get("formulas") is not None and not stack.text_fits["formulas"].fits:
        protected_reserved = _estimate_reserved_text_height(
            specs,
            width=inner_w,
            gap=compact_gap,
            reserve_formula_first=True,
            keep_readable_keys=("explanation", "formulas", "bullets", "takeaway"),
        )
        visual_h = clamp(usable_h - protected_reserved - compact_gap, min_visual_h * 0.92, max_visual_h)
        text_box = Box(
            outer_box.x + side_pad,
            outer_box.y + top_pad + visual_h + compact_gap,
            inner_w,
            max(0.0, usable_h - visual_h - compact_gap),
        )
        stack = layout_vertical_stack(text_box, specs, gap=compact_gap, top_pad=0.0, bottom_pad=0.0)

    visual_box = Box(
        outer_box.x + side_pad,
        outer_box.y + top_pad,
        inner_w,
        visual_h,
    )
    return PosterLayoutResult(
        outer_box=outer_box,
        visual_box=visual_box,
        text_boxes=stack.boxes,
        text_fits=stack.text_fits,
        visual_share=visual_box.h / max(usable_h, 1e-6),
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
    cfg = _PosterModeConfig(
        dense_math=True,
        reserve_formula_first=True,
        formulas_before_bullets=True,
        keep_readable_keys=("explanation", "formulas", "takeaway"),
    )
    specs = _make_text_specs(
        explanation=explanation,
        bullets_text=bullets_text,
        formulas_text=formulas_text,
        note_text=note_text,
        takeaway_text=takeaway_text,
        cfg=cfg,
    )
    return _layout_poster(
        outer_box,
        specs=specs,
        top_pad=top_pad,
        bottom_pad=bottom_pad,
        side_pad=side_pad,
        gap=gap,
        visual_min_share=visual_min_share,
        visual_max_share=visual_max_share,
        preferred_visual_share=preferred_visual_share,
        cfg=cfg,
    )


def layout_compact_concept_poster(
    outer_box: Box,
    *,
    explanation: str = "",
    bullets_text: str = "",
    formulas_text: str = "",
    note_text: str = "",
    takeaway_text: str = "",
    top_pad: Unit = 0.14,
    bottom_pad: Unit = 0.11,
    gap: Unit = 0.055,
    side_pad: Unit = 0.18,
    visual_min_share: float = 0.60,
    visual_max_share: float = 0.80,
    preferred_visual_share: float = 0.69,
) -> PosterLayoutResult:
    return _layout_compact_bands(
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
        visual_min_share=visual_min_share,
        visual_max_share=visual_max_share,
        preferred_visual_share=preferred_visual_share,
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
    compact_concept_mode: bool = False,
) -> PosterLayoutResult:
    mode = str(layout_mode or "concept").strip().lower()
    text_first = prioritize_text_over_visual or dense_math_mode or mode in {"worked_math", "dense_math", "text_first"}
    compact_mode = compact_concept_mode or mode in {"compact", "compact_concept", "concept_compact"}

    if text_first:
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
            visual_min_share=min(visual_min_share, 0.62),
            visual_max_share=min(max(visual_max_share, min(visual_min_share, 0.62) + 0.08), 0.68),
            preferred_visual_share=min(
                max(preferred_visual_share, min(visual_min_share, 0.62)),
                min(max(visual_max_share, min(visual_min_share, 0.62) + 0.08), 0.68),
            ),
        )

    if compact_mode:
        compact_min = max(0.58, min(visual_min_share, 0.72))
        compact_max = min(0.82, max(compact_min + 0.08, visual_max_share))
        return layout_compact_concept_poster(
            outer_box,
            explanation=explanation,
            bullets_text=bullets_text,
            formulas_text=formulas_text,
            note_text=note_text,
            takeaway_text=takeaway_text,
            top_pad=min(top_pad, 0.14),
            bottom_pad=min(bottom_pad, 0.11),
            gap=min(gap, 0.06),
            side_pad=min(side_pad, 0.18),
            visual_min_share=compact_min,
            visual_max_share=compact_max,
            preferred_visual_share=min(max(preferred_visual_share, compact_min), compact_max),
        )

    cfg = _PosterModeConfig(
        reserve_formula_first=bool(reserve_formula_first) if reserve_formula_first is not None else False,
        keep_readable_keys=("explanation", "takeaway"),
    )
    specs = _make_text_specs(
        explanation=explanation,
        bullets_text=bullets_text,
        formulas_text=formulas_text,
        note_text=note_text,
        takeaway_text=takeaway_text,
        cfg=cfg,
    )
    return _layout_poster(
        outer_box,
        specs=specs,
        top_pad=top_pad,
        bottom_pad=bottom_pad,
        side_pad=side_pad,
        gap=gap,
        visual_min_share=visual_min_share,
        visual_max_share=visual_max_share,
        preferred_visual_share=preferred_visual_share,
        cfg=cfg,
    )

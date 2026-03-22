from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from slideforge.layout.autofit import Box, clamp, distribute_columns, fit_text


@dataclass(frozen=True)
class TextBlockSizing:
    preferred_h: float
    floor_h: float
    fitted_font: int


@dataclass(frozen=True)
class PanelContentHeights:
    title_h: float
    visual_h: float
    caption_h: float
    formula_h: float
    title_gap: float
    caption_gap: float
    formula_gap: float


@dataclass(frozen=True)
class BandSpec:
    key: str
    text: str
    font_name: str
    color: Any
    min_font: int
    max_font: int
    max_lines: int
    bold: bool
    align: Any
    floor_h: float
    grow_weight: float
    shrink_weight: float


@dataclass(frozen=True)
class BandPlacement:
    spec: BandSpec
    box: Box
    font_size: int


@dataclass(frozen=True)
class MultiPanelSummaryLayout:
    panel_region: Box
    panel_boxes: list[Box]
    bottom_start_y: float
    band_x: float
    band_w: float
    footer_clearance_top: float


def _measure_text_block(
    text: str,
    *,
    box_w: float,
    min_font: int,
    max_font: int,
    max_lines: int | None,
    floor_h: float,
    cap_h: float | None,
    prefer_single_line: bool = False,
    pad_h: float = 0.03,
) -> TextBlockSizing:
    if not text.strip() or box_w <= 0:
        return TextBlockSizing(preferred_h=0.0, floor_h=0.0, fitted_font=max_font)

    fitted_max = fit_text(
        text,
        box_w,
        10.0,
        min_font_size=min_font,
        max_font_size=max_font,
        max_lines=max_lines,
        prefer_single_line=prefer_single_line,
    )
    preferred_h = max(floor_h, fitted_max.estimated_height + pad_h)
    if cap_h is not None and cap_h > 0:
        preferred_h = min(preferred_h, cap_h)

    fitted_min = fit_text(
        text,
        box_w,
        10.0,
        min_font_size=min_font,
        max_font_size=min_font,
        max_lines=max_lines,
        prefer_single_line=prefer_single_line,
    )
    floor_h = max(floor_h, fitted_min.estimated_height + pad_h)
    if cap_h is not None and cap_h > 0:
        floor_h = min(floor_h, cap_h)

    return TextBlockSizing(preferred_h=preferred_h, floor_h=floor_h, fitted_font=max(min_font, fitted_max.font_size))


def _shrink_with_priority(values: list[float], floors: list[float], priorities: list[float], shrink_needed: float) -> list[float]:
    if shrink_needed <= 0:
        return values
    current = list(values)
    remaining = shrink_needed
    while remaining > 1e-6:
        flexes = [max(0.0, value - floor) for value, floor in zip(current, floors)]
        weighted_flexes = [flex * max(0.0, priority) for flex, priority in zip(flexes, priorities)]
        total = sum(weighted_flexes)
        if total <= 1e-6:
            break
        reduced = False
        for idx, weighted_flex in enumerate(weighted_flexes):
            if weighted_flex <= 0:
                continue
            share = remaining * (weighted_flex / total)
            reducible = current[idx] - floors[idx]
            reduction = min(reducible, share)
            if reduction > 0:
                current[idx] -= reduction
                reduced = True
        new_remaining = max(0.0, sum(current) - max(sum(floors), sum(values) - shrink_needed))
        if not reduced or abs(new_remaining - remaining) < 1e-6:
            break
        remaining = new_remaining
    return [max(floor, value) for value, floor in zip(current, floors)]


def allocate_multi_panel_content_heights(*, inner_w: float, content_h: float, title_text: str, caption_text: str, formula_text: str, layout: Mapping[str, Any]) -> PanelContentHeights:
    title_gap = float(layout.get("title_to_visual_gap", 0.05)) if title_text else 0.0
    caption_gap = float(layout.get("visual_to_caption_gap", 0.06)) if caption_text else 0.0
    formula_gap = float(layout.get("caption_to_formula_gap", 0.05)) if formula_text else 0.0

    title_block = _measure_text_block(title_text, box_w=inner_w, min_font=int(layout.get("panel_title_min_font", 12)), max_font=int(layout.get("panel_title_max_font", 16)), max_lines=2, floor_h=float(layout.get("panel_title_h", 0.24)), cap_h=float(layout.get("panel_title_max_h", 0.52)))
    caption_block = _measure_text_block(caption_text, box_w=inner_w, min_font=int(layout.get("panel_caption_min_font", 11)), max_font=int(layout.get("panel_caption_max_font", 13)), max_lines=2, floor_h=float(layout.get("panel_caption_h", 0.28)), cap_h=float(layout.get("panel_caption_max_h", 0.46)))
    formula_block = _measure_text_block(formula_text, box_w=inner_w, min_font=int(layout.get("panel_formula_min_font", 11)), max_font=int(layout.get("panel_formula_max_font", 13)), max_lines=int(layout.get("panel_formula_max_lines", 2)), floor_h=float(layout.get("panel_formula_h", 0.26)), cap_h=float(layout.get("panel_formula_max_h", 0.54)))

    total_gaps = title_gap + caption_gap + formula_gap
    preferred_text_h = title_block.preferred_h + caption_block.preferred_h + formula_block.preferred_h

    adaptive_visual = bool(layout.get("adaptive_panel_visual", True))
    if not adaptive_visual:
        fixed_visual_h = max(0.0, min(float(layout.get("panel_visual_h", 1.14)), content_h - preferred_text_h - total_gaps))
        formula_h = max(formula_block.floor_h, content_h - (title_block.preferred_h + caption_block.preferred_h + fixed_visual_h + total_gaps))
        return PanelContentHeights(title_h=title_block.preferred_h, visual_h=fixed_visual_h, caption_h=caption_block.preferred_h, formula_h=max(0.0, formula_h), title_gap=title_gap, caption_gap=caption_gap, formula_gap=formula_gap)

    visual_min_share = float(layout.get("panel_visual_min_share", 0.34))
    visual_max_share = float(layout.get("panel_visual_max_share", 0.62))
    visual_pref_share = float(layout.get("panel_visual_preferred_share", 0.46))
    visual_min_h = min(max(0.0, float(layout.get("panel_visual_min_h", content_h * visual_min_share))), max(0.0, content_h - total_gaps))
    visual_max_h = max(visual_min_h, min(float(layout.get("panel_visual_max_h", content_h * visual_max_share)), max(0.0, content_h - total_gaps)))
    visual_pref_h = clamp(float(layout.get("panel_visual_h", content_h * visual_pref_share)), visual_min_h, visual_max_h)

    prioritize_text = bool(layout.get("prioritize_text_over_visual", True))
    title_h = title_block.preferred_h
    caption_h = caption_block.preferred_h
    formula_pref_h = formula_block.preferred_h
    shrink_needed = max(0.0, preferred_text_h + total_gaps + visual_min_h - content_h)
    if shrink_needed > 0:
        priorities = [0.5, 1.2, 1.8] if prioritize_text else [0.9, 1.1, 1.2]
        title_h, caption_h, formula_pref_h = _shrink_with_priority([title_h, caption_h, formula_pref_h], [title_block.floor_h, caption_block.floor_h, formula_block.floor_h], priorities, shrink_needed)
    remaining_after_text = max(0.0, content_h - (title_h + caption_h + formula_pref_h + total_gaps))
    visual_h = clamp(remaining_after_text, visual_min_h, visual_max_h)
    if remaining_after_text < visual_min_h:
        visual_h = max(0.22, remaining_after_text)
    formula_h = max(formula_block.floor_h if formula_text else 0.0, content_h - (title_h + visual_h + caption_h + total_gaps))
    return PanelContentHeights(title_h=max(0.0, title_h), visual_h=max(0.0, visual_h), caption_h=max(0.0, caption_h), formula_h=max(0.0, formula_h), title_gap=title_gap, caption_gap=caption_gap, formula_gap=formula_gap)


def layout_multi_panel_summary(panel_region: Box, *, panel_count: int, layout: Mapping[str, Any]) -> MultiPanelSummaryLayout:
    panel_gap = float(layout.get("panel_gap", 0.24))
    panel_boxes = distribute_columns(panel_region, max(1, panel_count), gap=panel_gap)[: max(0, panel_count)]
    occupied_bottom = panel_region.bottom
    left_pad = float(layout.get("bottom_text_side_pad", 0.48))
    return MultiPanelSummaryLayout(
        panel_region=panel_region,
        panel_boxes=panel_boxes,
        bottom_start_y=float(layout.get("bottom_text_start_y", occupied_bottom + 0.18)),
        band_x=float(layout.get("bottom_text_x", panel_region.x + left_pad)),
        band_w=float(layout.get("bottom_text_w", panel_region.w - 2 * left_pad)),
        footer_clearance_top=float(layout.get("footer_clearance_top", 6.58)),
    )


def build_multi_panel_band_specs(*, bullets_text: str, formulas_text: str, takeaway: str, style: Mapping[str, Any], layout: Mapping[str, Any], body_font: str, formula_font: str) -> list[list[BandSpec]]:
    bullets_spec = BandSpec("bullets", bullets_text, body_font, style["bullets_color"], int(layout.get("bullets_min_font", 12)), int(layout.get("bullets_max_font", 13)), int(layout.get("bullets_max_lines", 2)), bool(layout.get("bullets_bold", False)), layout.get("bullets_align"), float(layout.get("bullets_h", 0.28)), float(layout.get("bullets_grow_weight", 1.0)), float(layout.get("bullets_shrink_weight", 1.5)))
    formulas_spec = BandSpec("formulas", formulas_text, formula_font, style["formulas_color"], int(layout.get("formula_min_font", 11)), int(layout.get("formula_max_font", 13)), int(layout.get("formula_max_lines", 2)), False, layout.get("formula_align"), float(layout.get("formula_h", 0.28)), float(layout.get("formula_grow_weight", 0.9)), float(layout.get("formula_shrink_weight", 1.8)))
    takeaway_spec = BandSpec("takeaway", takeaway, body_font, style["takeaway_color"], int(layout.get("takeaway_min_font", 12)), int(layout.get("takeaway_max_font", 13)), int(layout.get("takeaway_max_lines", 2)), True, layout.get("takeaway_align"), float(layout.get("takeaway_h", 0.30)), float(layout.get("takeaway_grow_weight", 1.8)), float(layout.get("takeaway_shrink_weight", 0.8)))
    full = [s for s in (bullets_spec, formulas_spec, takeaway_spec) if s.text.strip()]
    no_formulas = [s for s in (bullets_spec, takeaway_spec) if s.text.strip()]
    takeaway_only = [takeaway_spec] if takeaway_spec.text.strip() else []
    bullets_only = [bullets_spec] if bullets_spec.text.strip() else []
    variants = [full, no_formulas, takeaway_only]
    if bullets_only:
        variants.append(bullets_only)
    variants.append([])
    return variants


def _measure_band(spec: BandSpec, *, band_w: float, pad_h: float) -> tuple[float, float]:
    fitted_max = fit_text(spec.text, band_w, 10.0, min_font_size=spec.min_font, max_font_size=spec.max_font, max_lines=spec.max_lines)
    fitted_min = fit_text(spec.text, band_w, 10.0, min_font_size=spec.min_font, max_font_size=spec.min_font, max_lines=spec.max_lines)
    floor_h = max(spec.floor_h, fitted_min.estimated_height + pad_h)
    pref_h = max(floor_h, fitted_max.estimated_height + pad_h)
    return floor_h, pref_h


def _shrink_heights(preferred: list[float], floors: list[float], shrink_weights: list[float], target_total: float) -> list[float]:
    current = list(preferred)
    excess = max(0.0, sum(current) - target_total)
    if excess <= 1e-6:
        return current
    while excess > 1e-6:
        flexes = [max(0.0, cur - floor) for cur, floor in zip(current, floors)]
        weighted = [flex * max(0.0, weight) for flex, weight in zip(flexes, shrink_weights)]
        total = sum(weighted)
        if total <= 1e-6:
            break
        reduced = False
        for idx, weight in enumerate(weighted):
            if weight <= 0:
                continue
            share = excess * (weight / total)
            reducible = current[idx] - floors[idx]
            reduction = min(reducible, share)
            if reduction > 0:
                current[idx] -= reduction
                reduced = True
        new_excess = max(0.0, sum(current) - target_total)
        if not reduced or abs(new_excess - excess) < 1e-6:
            break
        excess = new_excess
    return [max(floor, cur) for cur, floor in zip(current, floors)]


def _distribute_growth(current: list[float], grow_weights: list[float], extra_space: float) -> list[float]:
    if extra_space <= 1e-6:
        return current
    total_weight = sum(max(0.0, w) for w in grow_weights)
    if total_weight <= 1e-6:
        return current
    return [value + extra_space * (max(0.0, weight) / total_weight) for value, weight in zip(current, grow_weights)]


def _final_font_size(spec: BandSpec, box: Box) -> int:
    if not spec.text.strip() or box.w <= 0 or box.h <= 0:
        return spec.max_font
    fitted = fit_text(spec.text, box.w, box.h, min_font_size=spec.min_font, max_font_size=spec.max_font, max_lines=spec.max_lines)
    return max(spec.min_font, fitted.font_size)


def layout_multi_panel_bands(*, layout_result: MultiPanelSummaryLayout, variants: list[list[BandSpec]], layout: Mapping[str, Any]) -> list[BandPlacement]:
    available_h = max(0.0, layout_result.footer_clearance_top - layout_result.bottom_start_y)
    if available_h <= 0:
        return []
    gap = float(layout.get("bottom_text_gap", 0.10))
    pad_h = float(layout.get("bottom_band_vertical_pad", 0.03))
    for specs in variants:
        if not specs:
            return []
        metrics = [(_measure_band(spec, band_w=layout_result.band_w, pad_h=pad_h), spec) for spec in specs]
        gap_total = gap * max(0, len(metrics) - 1)
        budget = available_h - gap_total
        if budget <= 0:
            continue
        floors = [m[0][0] for m in metrics]
        preferred = [m[0][1] for m in metrics]
        if sum(floors) - budget > 1e-6:
            continue
        heights = _shrink_heights(preferred, floors, [m[1].shrink_weight for m in metrics], budget) if sum(preferred) > budget else _distribute_growth(list(preferred), [m[1].grow_weight for m in metrics], budget - sum(preferred))
        y = layout_result.bottom_start_y
        placements: list[BandPlacement] = []
        for (_, spec), h in zip(metrics, heights):
            box = Box(layout_result.band_x, y, layout_result.band_w, h)
            placements.append(BandPlacement(spec=spec, box=box, font_size=_final_font_size(spec, box)))
            y = box.bottom + gap
        if placements and placements[-1].box.bottom <= layout_result.footer_clearance_top + 1e-6:
            return placements
    return []

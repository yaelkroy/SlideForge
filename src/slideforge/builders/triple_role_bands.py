from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from slideforge.config.constants import BODY_FONT, FORMULA_FONT
from slideforge.layout.autofit import Box, fit_text
from slideforge.render.primitives import add_rounded_box, add_textbox


@dataclass(frozen=True)
class BandRenderSpec:
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
class BandMetrics:
    spec: BandRenderSpec
    floor_h: float
    preferred_h: float


@dataclass(frozen=True)
class BandRenderPlacement:
    spec: BandRenderSpec
    box: Box
    font_size: int


def _measure_band(
    spec: BandRenderSpec,
    *,
    band_w: float,
    pad_h: float,
) -> BandMetrics:
    fitted_max = fit_text(
        spec.text,
        band_w,
        10.0,
        min_font_size=spec.min_font,
        max_font_size=spec.max_font,
        max_lines=spec.max_lines,
    )
    fitted_min = fit_text(
        spec.text,
        band_w,
        10.0,
        min_font_size=spec.min_font,
        max_font_size=spec.min_font,
        max_lines=spec.max_lines,
    )
    floor_h = max(spec.floor_h, fitted_min.estimated_height + pad_h)
    preferred_h = max(floor_h, fitted_max.estimated_height + pad_h)
    return BandMetrics(spec=spec, floor_h=floor_h, preferred_h=preferred_h)


def _build_bottom_band_variants(
    *,
    bullets_text: str,
    formulas_text: str,
    takeaway: str,
    style: Mapping[str, Any],
    layout: Mapping[str, Any],
) -> list[list[BandRenderSpec]]:
    bullets_spec = BandRenderSpec(
        key="bullets",
        text=bullets_text,
        font_name=BODY_FONT,
        color=style["bullets_color"],
        min_font=int(layout.get("bullets_min_font", 12)),
        max_font=int(layout.get("bullets_max_font", 13)),
        max_lines=int(layout.get("bullets_max_lines", 2)),
        bold=bool(layout.get("bullets_bold", False)),
        align=layout.get("bullets_align"),
        floor_h=float(layout.get("bullets_h", 0.28)),
        grow_weight=float(layout.get("bullets_grow_weight", 1.0)),
        shrink_weight=float(layout.get("bullets_shrink_weight", 1.5)),
    )
    formulas_spec = BandRenderSpec(
        key="formulas",
        text=formulas_text,
        font_name=FORMULA_FONT,
        color=style["formulas_color"],
        min_font=int(layout.get("formula_min_font", 11)),
        max_font=int(layout.get("formula_max_font", 13)),
        max_lines=int(layout.get("formula_max_lines", 2)),
        bold=False,
        align=layout.get("formula_align"),
        floor_h=float(layout.get("formula_h", 0.28)),
        grow_weight=float(layout.get("formula_grow_weight", 0.9)),
        shrink_weight=float(layout.get("formula_shrink_weight", 1.8)),
    )
    takeaway_spec = BandRenderSpec(
        key="takeaway",
        text=takeaway,
        font_name=BODY_FONT,
        color=style["takeaway_color"],
        min_font=int(layout.get("takeaway_min_font", 12)),
        max_font=int(layout.get("takeaway_max_font", 13)),
        max_lines=int(layout.get("takeaway_max_lines", 2)),
        bold=True,
        align=layout.get("takeaway_align"),
        floor_h=float(layout.get("takeaway_h", 0.30)),
        grow_weight=float(layout.get("takeaway_grow_weight", 1.8)),
        shrink_weight=float(layout.get("takeaway_shrink_weight", 0.8)),
    )

    full = [
        spec
        for spec in (bullets_spec, formulas_spec, takeaway_spec)
        if spec.text.strip()
    ]
    no_formulas = [
        spec for spec in (bullets_spec, takeaway_spec) if spec.text.strip()
    ]
    takeaway_only = [takeaway_spec] if takeaway_spec.text.strip() else []
    bullets_only = [bullets_spec] if bullets_spec.text.strip() else []

    variants = [full, no_formulas, takeaway_only]
    if bullets_only:
        variants.append(bullets_only)
    variants.append([])
    return variants


def _shrink_heights(
    preferred: list[float],
    floors: list[float],
    shrink_weights: list[float],
    target_total: float,
) -> list[float]:
    current = list(preferred)
    excess = max(0.0, sum(current) - target_total)
    if excess <= 1e-6:
        return current

    while excess > 1e-6:
        flexes = [max(0.0, cur - floor) for cur, floor in zip(current, floors)]
        weighted_flex = [
            flex * max(0.0, weight) for flex, weight in zip(flexes, shrink_weights)
        ]
        total_weighted_flex = sum(weighted_flex)
        if total_weighted_flex <= 1e-6:
            break

        reduced_any = False
        for idx, weight in enumerate(weighted_flex):
            if weight <= 0:
                continue
            share = excess * (weight / total_weighted_flex)
            reducible = current[idx] - floors[idx]
            reduction = min(reducible, share)
            if reduction > 0:
                current[idx] -= reduction
                reduced_any = True

        new_excess = max(0.0, sum(current) - target_total)
        if not reduced_any or abs(new_excess - excess) < 1e-6:
            break
        excess = new_excess

    return [max(floor, cur) for cur, floor in zip(current, floors)]


def _distribute_growth(
    current: list[float],
    grow_weights: list[float],
    extra_space: float,
) -> list[float]:
    if extra_space <= 1e-6:
        return current
    total_weight = sum(max(0.0, weight) for weight in grow_weights)
    if total_weight <= 1e-6:
        return current
    grown = list(current)
    for idx, weight in enumerate(grow_weights):
        positive_weight = max(0.0, weight)
        if positive_weight <= 0:
            continue
        grown[idx] += extra_space * (positive_weight / total_weight)
    return grown


def _final_font_size(spec: BandRenderSpec, box: Box) -> int:
    if not spec.text.strip() or box.w <= 0 or box.h <= 0:
        return spec.max_font
    fitted = fit_text(
        spec.text,
        box.w,
        box.h,
        min_font_size=spec.min_font,
        max_font_size=spec.max_font,
        max_lines=spec.max_lines,
    )
    return max(spec.min_font, fitted.font_size)


def _layout_bottom_bands(
    *,
    start_y: float,
    footer_clearance_top: float,
    band_x: float,
    band_w: float,
    gap: float,
    variants: list[list[BandRenderSpec]],
    layout: Mapping[str, Any],
) -> list[BandRenderPlacement]:
    available_h = max(0.0, footer_clearance_top - start_y)
    if available_h <= 0:
        return []

    pad_h = float(layout.get("bottom_band_vertical_pad", 0.03))

    for specs in variants:
        if not specs:
            return []

        metrics = [_measure_band(spec, band_w=band_w, pad_h=pad_h) for spec in specs]
        gap_total = gap * max(0, len(metrics) - 1)
        budget = available_h - gap_total
        if budget <= 0:
            continue

        floors = [metric.floor_h for metric in metrics]
        preferred = [metric.preferred_h for metric in metrics]
        if sum(floors) - budget > 1e-6:
            continue

        heights = list(preferred)
        if sum(preferred) > budget:
            heights = _shrink_heights(
                preferred,
                floors,
                [metric.spec.shrink_weight for metric in metrics],
                budget,
            )
        else:
            heights = _distribute_growth(
                heights,
                [metric.spec.grow_weight for metric in metrics],
                budget - sum(preferred),
            )

        y = start_y
        placements: list[BandRenderPlacement] = []
        for metric, band_h in zip(metrics, heights):
            box = Box(band_x, y, band_w, band_h)
            placements.append(
                BandRenderPlacement(
                    spec=metric.spec,
                    box=box,
                    font_size=_final_font_size(metric.spec, box),
                )
            )
            y = box.bottom + gap

        if placements and placements[-1].box.bottom <= footer_clearance_top + 1e-6:
            return placements

    return []


def _render_summary_surface(slide, placements: list[BandRenderPlacement], *, layout, style) -> None:
    if not placements:
        return
    if not bool(layout.get("use_bottom_summary_card", False)):
        return

    side_pad = float(layout.get("bottom_summary_card_side_pad", 0.16))
    top_pad = float(layout.get("bottom_summary_card_top_pad", 0.10))
    bottom_pad = float(layout.get("bottom_summary_card_bottom_pad", 0.10))
    stack_left = min(placement.box.x for placement in placements)
    stack_right = max(placement.box.x + placement.box.w for placement in placements)
    stack_top = min(placement.box.y for placement in placements)
    stack_bottom = max(placement.box.bottom for placement in placements)

    add_rounded_box(
        slide,
        x=stack_left - side_pad,
        y=stack_top - top_pad,
        w=(stack_right - stack_left) + 2 * side_pad,
        h=(stack_bottom - stack_top) + top_pad + bottom_pad,
        line_color=style["panel_line_color"],
        fill_color=style["panel_fill_color"],
        line_width_pt=float(layout.get("bottom_summary_card_line_width_pt", style["panel_line_width_pt"])),
    )


def render_triple_role_bottom_bands(
    slide,
    *,
    panel_region: Box,
    bullets_text: str,
    formulas_text: str,
    takeaway: str,
    layout: Mapping[str, Any],
    style: Mapping[str, Any],
) -> None:
    occupied_bottom = panel_region.bottom
    bottom_gap = float(layout.get("bottom_text_gap", 0.10))
    left_pad = float(layout.get("bottom_text_side_pad", 0.48))
    band_x = float(layout.get("bottom_text_x", panel_region.x + left_pad))
    band_w = float(layout.get("bottom_text_w", panel_region.w - 2 * left_pad))
    start_y = float(layout.get("bottom_text_start_y", occupied_bottom + 0.18))
    footer_clearance_top = float(layout.get("footer_clearance_top", 6.58))

    if not bool(layout.get("use_manual_bottom_bands", False)):
        variants = _build_bottom_band_variants(
            bullets_text=bullets_text,
            formulas_text=formulas_text,
            takeaway=takeaway,
            style=style,
            layout=layout,
        )
        placements = _layout_bottom_bands(
            start_y=start_y,
            footer_clearance_top=footer_clearance_top,
            band_x=band_x,
            band_w=band_w,
            gap=bottom_gap,
            variants=variants,
            layout=layout,
        )
        _render_summary_surface(slide, placements, layout=layout, style=style)
        for placement in placements:
            add_textbox(
                slide,
                x=placement.box.x,
                y=placement.box.y,
                w=placement.box.w,
                h=placement.box.h,
                text=placement.spec.text,
                font_name=placement.spec.font_name,
                font_size=placement.font_size,
                color=placement.spec.color,
                bold=placement.spec.bold,
                align=placement.spec.align,
            )
        return

    if bullets_text:
        bullets_box = Box(
            band_x,
            float(layout.get("bullets_y", occupied_bottom + 0.18)),
            band_w,
            float(layout.get("bullets_h", 0.28)),
        )
        add_textbox(
            slide,
            x=bullets_box.x,
            y=bullets_box.y,
            w=bullets_box.w,
            h=bullets_box.h,
            text=bullets_text,
            font_name=BODY_FONT,
            font_size=int(layout.get("bullets_max_font", 13)),
            color=style["bullets_color"],
            bold=bool(layout.get("bullets_bold", False)),
            align=layout.get("bullets_align"),
        )

    if formulas_text:
        formula_box = Box(
            band_x,
            float(layout.get("formula_y", occupied_bottom + 0.56)),
            band_w,
            float(layout.get("formula_h", 0.28)),
        )
        add_textbox(
            slide,
            x=formula_box.x,
            y=formula_box.y,
            w=formula_box.w,
            h=formula_box.h,
            text=formulas_text,
            font_name=FORMULA_FONT,
            font_size=int(layout.get("formula_max_font", 13)),
            color=style["formulas_color"],
            bold=False,
            align=layout.get("formula_align"),
        )

    if takeaway:
        takeaway_box = Box(
            band_x,
            float(layout.get("takeaway_y", occupied_bottom + 0.92)),
            band_w,
            float(layout.get("takeaway_h", 0.30)),
        )
        add_textbox(
            slide,
            x=takeaway_box.x,
            y=takeaway_box.y,
            w=takeaway_box.w,
            h=takeaway_box.h,
            text=takeaway,
            font_name=BODY_FONT,
            font_size=int(layout.get("takeaway_max_font", 13)),
            color=style["takeaway_color"],
            bold=True,
            align=layout.get("takeaway_align"),
        )

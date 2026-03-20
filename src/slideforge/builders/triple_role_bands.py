from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from slideforge.config.constants import BODY_FONT, FORMULA_FONT
from slideforge.layout.autofit import Box, fit_text
from slideforge.render.primitives import add_textbox


@dataclass
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


@dataclass
class BandRenderPlacement:
    spec: BandRenderSpec
    box: Box
    font_size: int


def _estimate_band_height(
    text: str,
    box_w: float,
    *,
    min_font: int,
    max_font: int,
    max_lines: int,
    floor_h: float,
) -> tuple[float, int]:
    probe_box = Box(0.0, 0.0, box_w, 10.0)
    fitted = fit_text(
        text,
        probe_box.w,
        probe_box.h,
        min_font_size=min_font,
        max_font_size=max_font,
        max_lines=max_lines,
    )
    font_size = max(min_font, fitted.font_size)
    estimated_h = max(floor_h, fitted.estimated_height)
    return estimated_h, font_size


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
    )

    full = [
        spec
        for spec in (bullets_spec, formulas_spec, takeaway_spec)
        if spec.text.strip()
    ]
    no_formulas = [
        spec
        for spec in (bullets_spec, takeaway_spec)
        if spec.text.strip()
    ]
    takeaway_only = [takeaway_spec] if takeaway_spec.text.strip() else []
    bullets_only = [bullets_spec] if bullets_spec.text.strip() else []

    variants = [full, no_formulas, takeaway_only]
    if bullets_only:
        variants.append(bullets_only)
    variants.append([])

    return variants


def _place_bottom_bands(
    *,
    start_y: float,
    footer_clearance_top: float,
    band_x: float,
    band_w: float,
    gap: float,
    layout: Mapping[str, Any],
    variants: list[list[BandRenderSpec]],
) -> list[BandRenderPlacement]:
    for specs in variants:
        y = start_y
        placements: list[BandRenderPlacement] = []
        overflow = False

        for spec in specs:
            floor_h = float(layout.get(f"{spec.key}_h", 0.28))
            band_h, font_size = _estimate_band_height(
                spec.text,
                band_w,
                min_font=spec.min_font,
                max_font=spec.max_font,
                max_lines=spec.max_lines,
                floor_h=floor_h,
            )
            box = Box(band_x, y, band_w, band_h)
            placements.append(
                BandRenderPlacement(
                    spec=spec,
                    box=box,
                    font_size=font_size,
                )
            )
            y = box.bottom + gap

        if placements and placements[-1].box.bottom > footer_clearance_top:
            overflow = True

        if not overflow:
            return placements

    return []


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
        placements = _place_bottom_bands(
            start_y=start_y,
            footer_clearance_top=footer_clearance_top,
            band_x=band_x,
            band_w=band_w,
            gap=bottom_gap,
            layout=layout,
            variants=variants,
        )
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
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, OFFWHITE, TITLE_FONT
from slideforge.config.themes import SlideTheme, get_theme, resolve_color
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, distribute_columns, fit_text
from slideforge.render.header import render_header_from_spec
from slideforge.render.primitives import add_footer, add_rounded_box, add_textbox


@dataclass
class _BandRenderSpec:
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
class _BandRenderPlacement:
    spec: _BandRenderSpec
    box: Box
    font_size: int


def _join_items(items: list[str]) -> str:
    cleaned = [item.strip() for item in items if item and item.strip()]
    return "   •   ".join(cleaned)


def _fit_font_size(
    text: str,
    box: Box,
    *,
    min_font: int,
    max_font: int,
    max_lines: int | None = None,
    prefer_single_line: bool = False,
) -> int:
    if not text.strip() or box.w <= 0 or box.h <= 0:
        return max_font

    fitted = fit_text(
        text,
        box.w,
        box.h,
        min_font_size=min_font,
        max_font_size=max_font,
        max_lines=max_lines,
        prefer_single_line=prefer_single_line,
    )
    return max(min_font, fitted.font_size)


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


def _box_from_dict(raw: Mapping[str, Any], fallback: Box) -> Box:
    return Box(
        raw.get("x", fallback.x),
        raw.get("y", fallback.y),
        raw.get("w", fallback.w),
        raw.get("h", fallback.h),
    )


def _resolve_triple_role_style(
    spec: Mapping[str, Any],
    *,
    theme_obj: SlideTheme,
) -> dict[str, Any]:
    role_style = dict(spec.get("triple_role_style", {}) or {})

    panel_fill_default = theme_obj.box_fill_color
    if panel_fill_default is None:
        panel_fill_default = theme_obj.panel_fill_color
    if panel_fill_default is None:
        panel_fill_default = OFFWHITE

    panel_line_default = theme_obj.box_line_color
    if panel_line_default is None:
        panel_line_default = theme_obj.panel_line_color

    return {
        "panel_fill_color": resolve_color(
            role_style.get("panel_fill_color"),
            panel_fill_default,
        ),
        "panel_line_color": resolve_color(
            role_style.get("panel_line_color"),
            panel_line_default,
        ),
        "panel_title_color": resolve_color(
            role_style.get("panel_title_color"),
            theme_obj.box_title_color,
        ),
        "panel_caption_color": resolve_color(
            role_style.get("panel_caption_color"),
            theme_obj.subtitle_color,
        ),
        "panel_formula_color": resolve_color(
            role_style.get("panel_formula_color"),
            theme_obj.body_color,
        ),
        "bullets_color": resolve_color(
            role_style.get("bullets_color"),
            theme_obj.subtitle_color,
        ),
        "formulas_color": resolve_color(
            role_style.get("formulas_color"),
            theme_obj.body_color,
        ),
        "takeaway_color": resolve_color(
            role_style.get("takeaway_color"),
            theme_obj.subtitle_color,
        ),
        "footer_color": resolve_color(
            role_style.get("footer_color"),
            theme_obj.footer_color,
        ),
        "footer_dark": bool(
            role_style.get("footer_dark", theme_obj.footer_dark)
        ),
        "visual_variant": str(
            role_style.get("visual_variant", theme_obj.panel_visual_variant)
        ),
        "panel_line_width_pt": float(
            role_style.get("panel_line_width_pt", 1.2)
        ),
    }


def _add_fitted_text(
    slide,
    *,
    box: Box,
    text: str,
    font_name: str,
    color,
    min_font: int,
    max_font: int,
    max_lines: int | None = None,
    bold: bool = False,
    align=PP_ALIGN.CENTER,
    prefer_single_line: bool = False,
) -> None:
    if not text.strip() or box.w <= 0 or box.h <= 0:
        return

    font_size = _fit_font_size(
        text,
        box,
        min_font=min_font,
        max_font=max_font,
        max_lines=max_lines,
        prefer_single_line=prefer_single_line,
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


def _build_bottom_band_variants(
    *,
    bullets_text: str,
    formulas_text: str,
    takeaway: str,
    style: Mapping[str, Any],
    layout: Mapping[str, Any],
) -> list[list[_BandRenderSpec]]:
    bullets_spec = _BandRenderSpec(
        key="bullets",
        text=bullets_text,
        font_name=BODY_FONT,
        color=style["bullets_color"],
        min_font=int(layout.get("bullets_min_font", 12)),
        max_font=int(layout.get("bullets_max_font", 13)),
        max_lines=int(layout.get("bullets_max_lines", 2)),
        bold=bool(layout.get("bullets_bold", False)),
        align=layout.get("bullets_align", PP_ALIGN.CENTER),
    )
    formulas_spec = _BandRenderSpec(
        key="formulas",
        text=formulas_text,
        font_name=FORMULA_FONT,
        color=style["formulas_color"],
        min_font=int(layout.get("formula_min_font", 11)),
        max_font=int(layout.get("formula_max_font", 13)),
        max_lines=int(layout.get("formula_max_lines", 2)),
        bold=False,
        align=layout.get("formula_align", PP_ALIGN.CENTER),
    )
    takeaway_spec = _BandRenderSpec(
        key="takeaway",
        text=takeaway,
        font_name=BODY_FONT,
        color=style["takeaway_color"],
        min_font=int(layout.get("takeaway_min_font", 12)),
        max_font=int(layout.get("takeaway_max_font", 13)),
        max_lines=int(layout.get("takeaway_max_lines", 2)),
        bold=True,
        align=layout.get("takeaway_align", PP_ALIGN.CENTER),
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
    variants: list[list[_BandRenderSpec]],
) -> list[_BandRenderPlacement]:
    for specs in variants:
        y = start_y
        placements: list[_BandRenderPlacement] = []
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
                _BandRenderPlacement(
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


def build_triple_role_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    slide_theme_name = spec.get("theme", "concept")
    theme_obj = get_theme(slide_theme_name=slide_theme_name)

    bg = spec.get("background") or choose_background(slide_theme_name, counters)
    slide = new_slide(prs, bg)

    layout = dict(spec.get("layout", {}) or {})
    style = _resolve_triple_role_style(spec, theme_obj=theme_obj)

    panels = list(spec.get("panels", []) or [])
    bullets = list(spec.get("bullets", []) or [])
    bullets_text = _join_items(bullets)

    formulas = list(spec.get("formulas", []) or [])
    formulas_text = _join_items(formulas)

    takeaway = str(spec.get("takeaway", "")).strip()

    header_result = render_header_from_spec(
        slide,
        spec,
        theme=theme_obj,
    )

    panel_region_fallback = Box(
        float(layout.get("panel_x", 0.88)),
        float(
            layout.get(
                "panel_y",
                header_result.content_top_y
                + float(layout.get("content_to_panel_gap", 0.14)),
            )
        ),
        float(layout.get("panel_w", 11.24)),
        float(layout.get("panel_h", 3.05)),
    )
    panel_region_raw = layout.get("panel_region")
    panel_region = (
        _box_from_dict(panel_region_raw, panel_region_fallback)
        if isinstance(panel_region_raw, Mapping)
        else panel_region_fallback
    )

    panel_gap = float(layout.get("panel_gap", 0.24))
    default_cols = max(1, len(panels))
    panel_boxes = distribute_columns(
        panel_region,
        default_cols,
        gap=panel_gap,
    )

    visible_panels = min(len(panels), len(panel_boxes))
    panel_boxes = panel_boxes[:visible_panels]

    panel_inner_pad_x = float(layout.get("panel_inner_pad_x", 0.12))
    panel_inner_pad_top = float(layout.get("panel_inner_pad_top", 0.10))
    visual_h = float(layout.get("panel_visual_h", 1.14))
    title_h = float(layout.get("panel_title_h", 0.24))
    caption_h = float(layout.get("panel_caption_h", 0.28))
    title_to_visual_gap = float(layout.get("title_to_visual_gap", 0.05))
    visual_to_caption_gap = float(layout.get("visual_to_caption_gap", 0.06))
    caption_to_formula_gap = float(layout.get("caption_to_formula_gap", 0.05))
    formula_bottom_pad = float(layout.get("formula_bottom_pad", 0.08))

    for panel, panel_box in zip(panels, panel_boxes):
        add_rounded_box(
            slide,
            panel_box.x,
            panel_box.y,
            panel_box.w,
            panel_box.h,
            line_color=resolve_color(
                panel.get("line_color"),
                style["panel_line_color"],
            ),
            fill_color=resolve_color(
                panel.get("fill_color"),
                style["panel_fill_color"],
            ),
            line_width_pt=float(
                panel.get("line_width_pt", style["panel_line_width_pt"])
            ),
        )

        inner_x = panel_box.x + panel_inner_pad_x
        inner_w = panel_box.w - 2 * panel_inner_pad_x

        panel_title = str(panel.get("title", "")).strip()
        title_box = Box(inner_x, panel_box.y + panel_inner_pad_top, inner_w, title_h)
        _add_fitted_text(
            slide,
            box=title_box,
            text=panel_title,
            font_name=TITLE_FONT,
            color=style["panel_title_color"],
            min_font=int(layout.get("panel_title_min_font", 12)),
            max_font=int(
                panel.get(
                    "title_font_size",
                    layout.get("panel_title_max_font", 16),
                )
            ),
            max_lines=2,
            bold=True,
            align=PP_ALIGN.CENTER,
        )

        visual_box = Box(
            inner_x,
            title_box.bottom + title_to_visual_gap,
            inner_w,
            visual_h,
        )
        mini_visual = str(panel.get("mini_visual", "")).strip()
        if mini_visual:
            add_mini_visual(
                slide,
                kind=mini_visual,
                x=visual_box.x,
                y=visual_box.y,
                w=visual_box.w,
                h=visual_box.h,
                suffix="_triple_role",
                variant=str(panel.get("visual_variant", style["visual_variant"])),
            )

        caption_text = str(panel.get("caption", "")).strip()
        caption_box = Box(
            inner_x,
            visual_box.bottom + visual_to_caption_gap,
            inner_w,
            caption_h,
        )
        _add_fitted_text(
            slide,
            box=caption_box,
            text=caption_text,
            font_name=BODY_FONT,
            color=style["panel_caption_color"],
            min_font=int(layout.get("panel_caption_min_font", 11)),
            max_font=int(
                panel.get(
                    "caption_font_size",
                    layout.get("panel_caption_max_font", 13),
                )
            ),
            max_lines=2,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

        formula_text = str(panel.get("formula", "")).strip()
        formula_box = Box(
            inner_x,
            caption_box.bottom + caption_to_formula_gap,
            inner_w,
            max(
                0.0,
                panel_box.bottom
                - (caption_box.bottom + caption_to_formula_gap)
                - formula_bottom_pad,
            ),
        )
        _add_fitted_text(
            slide,
            box=formula_box,
            text=formula_text,
            font_name=FORMULA_FONT,
            color=style["panel_formula_color"],
            min_font=int(layout.get("panel_formula_min_font", 11)),
            max_font=int(
                panel.get(
                    "formula_font_size",
                    layout.get("panel_formula_max_font", 13),
                )
            ),
            max_lines=int(layout.get("panel_formula_max_lines", 2)),
            bold=False,
            align=PP_ALIGN.CENTER,
        )

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
    else:
        if bullets_text:
            bullets_box = Box(
                band_x,
                float(layout.get("bullets_y", occupied_bottom + 0.18)),
                band_w,
                float(layout.get("bullets_h", 0.28)),
            )
            _add_fitted_text(
                slide,
                box=bullets_box,
                text=bullets_text,
                font_name=BODY_FONT,
                color=style["bullets_color"],
                min_font=int(layout.get("bullets_min_font", 12)),
                max_font=int(layout.get("bullets_max_font", 13)),
                max_lines=int(layout.get("bullets_max_lines", 2)),
                bold=bool(layout.get("bullets_bold", False)),
                align=layout.get("bullets_align", PP_ALIGN.CENTER),
            )

        if formulas_text:
            formula_box = Box(
                band_x,
                float(layout.get("formula_y", occupied_bottom + 0.56)),
                band_w,
                float(layout.get("formula_h", 0.28)),
            )
            _add_fitted_text(
                slide,
                box=formula_box,
                text=formulas_text,
                font_name=FORMULA_FONT,
                color=style["formulas_color"],
                min_font=int(layout.get("formula_min_font", 11)),
                max_font=int(layout.get("formula_max_font", 13)),
                max_lines=int(layout.get("formula_max_lines", 2)),
                bold=False,
                align=layout.get("formula_align", PP_ALIGN.CENTER),
            )

        if takeaway:
            takeaway_box = Box(
                band_x,
                float(layout.get("takeaway_y", occupied_bottom + 0.92)),
                band_w,
                float(layout.get("takeaway_h", 0.30)),
            )
            _add_fitted_text(
                slide,
                box=takeaway_box,
                text=takeaway,
                font_name=BODY_FONT,
                color=style["takeaway_color"],
                min_font=int(layout.get("takeaway_min_font", 12)),
                max_font=int(layout.get("takeaway_max_font", 13)),
                max_lines=int(layout.get("takeaway_max_lines", 2)),
                bold=True,
                align=layout.get("takeaway_align", PP_ALIGN.CENTER),
            )

    add_footer(
        slide,
        dark=style["footer_dark"],
        color=style["footer_color"],
    )
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, TITLE_FONT
from slideforge.layout.autofit import Box, clamp, distribute_columns, fit_text
from slideforge.render.primitives import add_rounded_box, add_textbox


@dataclass(frozen=True)
class _TextBlockSizing:
    preferred_h: float
    floor_h: float
    fitted_font: int


@dataclass(frozen=True)
class _PanelHeights:
    title_h: float
    visual_h: float
    caption_h: float
    formula_h: float
    title_gap: float
    caption_gap: float
    formula_gap: float


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
) -> _TextBlockSizing:
    if not text.strip() or box_w <= 0:
        return _TextBlockSizing(preferred_h=0.0, floor_h=0.0, fitted_font=max_font)

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

    return _TextBlockSizing(
        preferred_h=preferred_h,
        floor_h=floor_h,
        fitted_font=max(min_font, fitted_max.font_size),
    )


def _shrink_with_priority(
    values: list[float],
    floors: list[float],
    priorities: list[float],
    shrink_needed: float,
) -> list[float]:
    if shrink_needed <= 0:
        return values

    current = list(values)
    remaining = shrink_needed

    while remaining > 1e-6:
        flexes = [max(0.0, value - floor) for value, floor in zip(current, floors)]
        weighted_flexes = [
            flex * max(0.0, priority) for flex, priority in zip(flexes, priorities)
        ]
        total_weighted_flex = sum(weighted_flexes)
        if total_weighted_flex <= 1e-6:
            break

        for idx, weighted_flex in enumerate(weighted_flexes):
            if weighted_flex <= 0:
                continue
            share = remaining * (weighted_flex / total_weighted_flex)
            reducible = current[idx] - floors[idx]
            reduction = min(reducible, share)
            current[idx] -= reduction

        new_remaining = max(0.0, sum(current) - max(sum(floors), sum(values) - shrink_needed))
        if abs(new_remaining - remaining) < 1e-6:
            break
        remaining = new_remaining

    return [max(floor, value) for value, floor in zip(current, floors)]


def _allocate_panel_heights(
    *,
    inner_w: float,
    content_h: float,
    title_text: str,
    caption_text: str,
    formula_text: str,
    layout: Mapping[str, Any],
) -> _PanelHeights:
    title_gap = float(layout.get("title_to_visual_gap", 0.05)) if title_text else 0.0
    caption_gap = float(layout.get("visual_to_caption_gap", 0.06)) if caption_text else 0.0
    formula_gap = float(layout.get("caption_to_formula_gap", 0.05)) if formula_text else 0.0

    title_block = _measure_text_block(
        title_text,
        box_w=inner_w,
        min_font=int(layout.get("panel_title_min_font", 12)),
        max_font=int(layout.get("panel_title_max_font", 16)),
        max_lines=2,
        floor_h=float(layout.get("panel_title_h", 0.24)),
        cap_h=float(layout.get("panel_title_max_h", 0.52)),
    )
    caption_block = _measure_text_block(
        caption_text,
        box_w=inner_w,
        min_font=int(layout.get("panel_caption_min_font", 11)),
        max_font=int(layout.get("panel_caption_max_font", 13)),
        max_lines=2,
        floor_h=float(layout.get("panel_caption_h", 0.28)),
        cap_h=float(layout.get("panel_caption_max_h", 0.46)),
    )
    formula_block = _measure_text_block(
        formula_text,
        box_w=inner_w,
        min_font=int(layout.get("panel_formula_min_font", 11)),
        max_font=int(layout.get("panel_formula_max_font", 13)),
        max_lines=int(layout.get("panel_formula_max_lines", 2)),
        floor_h=float(layout.get("panel_formula_h", 0.26)),
        cap_h=float(layout.get("panel_formula_max_h", 0.54)),
    )

    total_gaps = title_gap + caption_gap + formula_gap
    preferred_text_h = (
        title_block.preferred_h + caption_block.preferred_h + formula_block.preferred_h
    )
    floor_text_h = title_block.floor_h + caption_block.floor_h + formula_block.floor_h

    adaptive_visual = bool(layout.get("adaptive_panel_visual", True))
    if not adaptive_visual:
        fixed_visual_h = float(layout.get("panel_visual_h", 1.14))
        fixed_visual_h = max(0.0, min(fixed_visual_h, content_h - preferred_text_h - total_gaps))
        formula_h = max(
            formula_block.floor_h,
            content_h
            - (title_block.preferred_h + caption_block.preferred_h + fixed_visual_h + total_gaps),
        )
        return _PanelHeights(
            title_h=title_block.preferred_h,
            visual_h=fixed_visual_h,
            caption_h=caption_block.preferred_h,
            formula_h=max(0.0, formula_h),
            title_gap=title_gap,
            caption_gap=caption_gap,
            formula_gap=formula_gap,
        )

    visual_min_share = float(layout.get("panel_visual_min_share", 0.34))
    visual_max_share = float(layout.get("panel_visual_max_share", 0.62))
    visual_pref_share = float(layout.get("panel_visual_preferred_share", 0.46))
    visual_min_h = float(layout.get("panel_visual_min_h", content_h * visual_min_share))
    visual_max_h = float(layout.get("panel_visual_max_h", content_h * visual_max_share))
    visual_pref_h = float(layout.get("panel_visual_h", content_h * visual_pref_share))
    visual_min_h = min(max(0.0, visual_min_h), max(0.0, content_h - total_gaps))
    visual_max_h = max(visual_min_h, min(visual_max_h, max(0.0, content_h - total_gaps)))
    visual_pref_h = clamp(visual_pref_h, visual_min_h, visual_max_h)

    prioritize_text = bool(layout.get("prioritize_text_over_visual", True))

    title_h = title_block.preferred_h
    caption_h = caption_block.preferred_h
    formula_pref_h = formula_block.preferred_h

    shrink_needed = max(
        0.0,
        preferred_text_h + total_gaps + visual_min_h - content_h,
    )
    if shrink_needed > 0:
        if prioritize_text:
            priorities = [0.5, 1.2, 1.8]
        else:
            priorities = [0.9, 1.1, 1.2]
        shrunk = _shrink_with_priority(
            [title_h, caption_h, formula_pref_h],
            [title_block.floor_h, caption_block.floor_h, formula_block.floor_h],
            priorities,
            shrink_needed,
        )
        title_h, caption_h, formula_pref_h = shrunk

    remaining_after_text = max(0.0, content_h - (title_h + caption_h + formula_pref_h + total_gaps))
    visual_h = clamp(remaining_after_text, visual_min_h, visual_max_h)

    if remaining_after_text < visual_min_h:
        visual_h = max(0.22, remaining_after_text)

    formula_h = max(
        formula_block.floor_h if formula_text else 0.0,
        content_h - (title_h + visual_h + caption_h + total_gaps),
    )

    return _PanelHeights(
        title_h=max(0.0, title_h),
        visual_h=max(0.0, visual_h),
        caption_h=max(0.0, caption_h),
        formula_h=max(0.0, formula_h),
        title_gap=title_gap,
        caption_gap=caption_gap,
        formula_gap=formula_gap,
    )


def render_triple_role_panels(
    slide,
    *,
    panels: Sequence[Mapping[str, Any]],
    panel_region: Box,
    layout: Mapping[str, Any],
    style: Mapping[str, Any],
) -> None:
    panel_gap = float(layout.get("panel_gap", 0.24))
    default_cols = max(1, len(panels))
    panel_boxes = distribute_columns(panel_region, default_cols, gap=panel_gap)

    visible_panels = min(len(panels), len(panel_boxes))
    panel_boxes = panel_boxes[:visible_panels]

    panel_inner_pad_x = float(layout.get("panel_inner_pad_x", 0.12))
    panel_inner_pad_top = float(layout.get("panel_inner_pad_top", 0.10))
    panel_inner_pad_bottom = float(layout.get("panel_inner_pad_bottom", 0.08))

    for panel, panel_box in zip(panels, panel_boxes):
        add_rounded_box(
            slide,
            panel_box.x,
            panel_box.y,
            panel_box.w,
            panel_box.h,
            line_color=panel.get("line_color", style["panel_line_color"]),
            fill_color=panel.get("fill_color", style["panel_fill_color"]),
            line_width_pt=float(
                panel.get("line_width_pt", style["panel_line_width_pt"])
            ),
        )

        inner_x = panel_box.x + panel_inner_pad_x
        inner_w = max(0.0, panel_box.w - 2 * panel_inner_pad_x)
        inner_y = panel_box.y + panel_inner_pad_top
        inner_h = max(0.0, panel_box.h - panel_inner_pad_top - panel_inner_pad_bottom)

        panel_title = str(panel.get("title", "")).strip()
        caption_text = str(panel.get("caption", "")).strip()
        formula_text = str(panel.get("formula", "")).strip()

        heights = _allocate_panel_heights(
            inner_w=inner_w,
            content_h=inner_h,
            title_text=panel_title,
            caption_text=caption_text,
            formula_text=formula_text,
            layout=layout,
        )

        title_box = Box(inner_x, inner_y, inner_w, heights.title_h)
        _add_fitted_text(
            slide,
            box=title_box,
            text=panel_title,
            font_name=TITLE_FONT,
            color=style["panel_title_color"],
            min_font=int(layout.get("panel_title_min_font", 12)),
            max_font=int(panel.get("title_font_size", layout.get("panel_title_max_font", 16))),
            max_lines=2,
            bold=True,
            align=PP_ALIGN.CENTER,
        )

        visual_y = title_box.bottom + heights.title_gap
        visual_box = Box(inner_x, visual_y, inner_w, heights.visual_h)
        mini_visual = str(panel.get("mini_visual", "")).strip()
        if mini_visual and visual_box.w > 0 and visual_box.h > 0:
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

        caption_y = visual_box.bottom + heights.caption_gap
        caption_box = Box(inner_x, caption_y, inner_w, heights.caption_h)
        _add_fitted_text(
            slide,
            box=caption_box,
            text=caption_text,
            font_name=BODY_FONT,
            color=style["panel_caption_color"],
            min_font=int(layout.get("panel_caption_min_font", 11)),
            max_font=int(panel.get("caption_font_size", layout.get("panel_caption_max_font", 13))),
            max_lines=2,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

        formula_y = caption_box.bottom + heights.formula_gap
        formula_h = max(0.0, panel_box.bottom - panel_inner_pad_bottom - formula_y)
        formula_box = Box(inner_x, formula_y, inner_w, formula_h)
        _add_fitted_text(
            slide,
            box=formula_box,
            text=formula_text,
            font_name=FORMULA_FONT,
            color=style["panel_formula_color"],
            min_font=int(layout.get("panel_formula_min_font", 11)),
            max_font=int(panel.get("formula_font_size", layout.get("panel_formula_max_font", 13))),
            max_lines=int(layout.get("panel_formula_max_lines", 2)),
            bold=False,
            align=PP_ALIGN.CENTER,
        )

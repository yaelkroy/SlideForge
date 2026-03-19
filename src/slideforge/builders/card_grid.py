from __future__ import annotations

from typing import Any, Mapping

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, OFFWHITE, TITLE_FONT
from slideforge.config.themes import SlideTheme, get_theme, resolve_color
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, centered_visual_in_card, distribute_columns, distribute_rows, fit_text
from slideforge.render.header import render_header_from_spec
from slideforge.render.primitives import add_footer, add_rounded_box, add_textbox


def _fit_text_size(
    text: str,
    box: Box,
    *,
    min_font: int,
    max_font: int,
    max_lines: int,
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
    )
    return max(min_font, fitted.font_size)


def _box_from_dict(raw: Mapping[str, Any], fallback: Box) -> Box:
    return Box(
        raw.get("x", fallback.x),
        raw.get("y", fallback.y),
        raw.get("w", fallback.w),
        raw.get("h", fallback.h),
    )


def _resolve_grid_style(
    spec: Mapping[str, Any],
    *,
    theme_obj: SlideTheme,
) -> dict[str, Any]:
    grid_style = dict(spec.get("grid_style", {}) or {})

    card_fill_default = theme_obj.box_fill_color if theme_obj.box_fill_color is not None else OFFWHITE
    panel_fill_default = theme_obj.panel_fill_color if theme_obj.panel_fill_color is not None else card_fill_default

    return {
        "card_fill_color": resolve_color(grid_style.get("card_fill_color"), card_fill_default),
        "card_line_color": resolve_color(grid_style.get("card_line_color"), theme_obj.box_line_color),
        "card_title_color": resolve_color(grid_style.get("card_title_color"), theme_obj.box_title_color),
        "card_formula_color": resolve_color(grid_style.get("card_formula_color"), theme_obj.box_body_color),
        "card_caption_color": resolve_color(grid_style.get("card_caption_color"), theme_obj.muted_color),
        "card_visual_variant": str(grid_style.get("card_visual_variant", theme_obj.panel_visual_variant)),
        "card_line_width_pt": float(grid_style.get("card_line_width_pt", 1.25)),
        "takeaway_color": resolve_color(grid_style.get("takeaway_color"), theme_obj.subtitle_color),
        "footer_color": resolve_color(grid_style.get("footer_color"), theme_obj.footer_color),
        "footer_dark": bool(grid_style.get("footer_dark", theme_obj.footer_dark)),
        "title_align": grid_style.get("card_title_align", PP_ALIGN.CENTER),
        "formula_align": grid_style.get("card_formula_align", PP_ALIGN.CENTER),
        "caption_align": grid_style.get("card_caption_align", PP_ALIGN.CENTER),
        "panel_fill_fallback": panel_fill_default,
    }


def _resolve_card_style(
    card: Mapping[str, Any],
    *,
    grid_style: Mapping[str, Any],
) -> dict[str, Any]:
    card_style = dict(card.get("style", {}) or {})
    return {
        "fill_color": resolve_color(card_style.get("fill_color"), grid_style["card_fill_color"]),
        "line_color": resolve_color(card_style.get("line_color"), grid_style["card_line_color"]),
        "title_color": resolve_color(card_style.get("title_color"), grid_style["card_title_color"]),
        "formula_color": resolve_color(card_style.get("formula_color"), grid_style["card_formula_color"]),
        "caption_color": resolve_color(card_style.get("caption_color"), grid_style["card_caption_color"]),
        "visual_variant": str(card_style.get("visual_variant", grid_style["card_visual_variant"])),
        "line_width_pt": float(card_style.get("line_width_pt", grid_style["card_line_width_pt"])),
    }


def _add_grid_card(
    slide,
    card: dict[str, Any],
    card_box: Box,
    idx: int,
    *,
    grid_style: Mapping[str, Any],
    layout: Mapping[str, Any],
) -> None:
    card_style = _resolve_card_style(card, grid_style=grid_style)

    add_rounded_box(
        slide,
        card_box.x,
        card_box.y,
        card_box.w,
        card_box.h,
        line_color=card_style["line_color"],
        fill_color=card_style["fill_color"],
        line_width_pt=card_style["line_width_pt"],
    )

    title_text = str(card.get("title", "")).strip()
    formula_text = str(card.get("formula", "")).strip()
    caption_text = str(card.get("caption", "")).strip()

    title_h = float(card.get("title_h", layout.get("card_title_h", 0.24)))
    formula_h = float(card.get("formula_h", layout.get("card_formula_h", 0.18 if formula_text else 0.0)))
    caption_h = float(card.get("caption_h", layout.get("card_caption_h", 0.20 if caption_text else 0.0)))

    title_box = Box(card_box.x + 0.10, card_box.y + 0.10, card_box.w - 0.20, title_h)
    title_font = _fit_text_size(
        title_text,
        title_box,
        min_font=int(card.get("title_min_font", layout.get("card_title_min_font", 12))),
        max_font=int(card.get("title_max_font", layout.get("card_title_max_font", 15))),
        max_lines=int(card.get("title_max_lines", layout.get("card_title_max_lines", 2))),
    )
    add_textbox(
        slide,
        x=title_box.x,
        y=title_box.y,
        w=title_box.w,
        h=title_box.h,
        text=title_text,
        font_name=TITLE_FONT,
        font_size=title_font,
        color=card_style["title_color"],
        bold=True,
        align=grid_style["title_align"],
    )

    visual_box = centered_visual_in_card(
        card_box,
        title_h=title_h,
        caption_h=caption_h,
        formula_h=formula_h,
        top_pad=float(card.get("top_pad", layout.get("card_top_pad", 0.10))),
        bottom_pad=float(card.get("bottom_pad", layout.get("card_bottom_pad", 0.12))),
        gap_above_visual=float(card.get("gap_above_visual", layout.get("card_gap_above_visual", 0.10))),
        gap_below_visual=float(card.get("gap_below_visual", layout.get("card_gap_below_visual", 0.10))),
    )

    visual_override = card.get("visual_box")
    if isinstance(visual_override, Mapping):
        visual_box = _box_from_dict(visual_override, visual_box)

    add_mini_visual(
        slide,
        kind=str(card.get("mini_visual", "")),
        x=visual_box.x,
        y=visual_box.y,
        w=visual_box.w,
        h=visual_box.h,
        suffix=f"_card_grid_{idx}",
        variant=card_style["visual_variant"],
    )

    current_y = visual_box.bottom + float(card.get("below_visual_gap", layout.get("card_below_visual_gap", 0.08)))

    if formula_text:
        formula_box = Box(card_box.x + 0.10, current_y, card_box.w - 0.20, formula_h)
        formula_font = _fit_text_size(
            formula_text,
            formula_box,
            min_font=int(card.get("formula_min_font", layout.get("card_formula_min_font", 11))),
            max_font=int(card.get("formula_max_font", layout.get("card_formula_max_font", 13))),
            max_lines=int(card.get("formula_max_lines", layout.get("card_formula_max_lines", 2))),
        )
        add_textbox(
            slide,
            x=formula_box.x,
            y=formula_box.y,
            w=formula_box.w,
            h=formula_box.h,
            text=formula_text,
            font_name=FORMULA_FONT,
            font_size=formula_font,
            color=card_style["formula_color"],
            bold=False,
            align=grid_style["formula_align"],
        )
        current_y += formula_h + float(card.get("formula_to_caption_gap", layout.get("formula_to_caption_gap", 0.05)))

    if caption_text:
        caption_box = Box(card_box.x + 0.10, current_y, card_box.w - 0.20, caption_h)
        caption_font = _fit_text_size(
            caption_text,
            caption_box,
            min_font=int(card.get("caption_min_font", layout.get("card_caption_min_font", 10))),
            max_font=int(card.get("caption_max_font", layout.get("card_caption_max_font", 12))),
            max_lines=int(card.get("caption_max_lines", layout.get("card_caption_max_lines", 2))),
        )
        add_textbox(
            slide,
            x=caption_box.x,
            y=caption_box.y,
            w=caption_box.w,
            h=caption_box.h,
            text=caption_text,
            font_name=BODY_FONT,
            font_size=caption_font,
            color=card_style["caption_color"],
            bold=False,
            align=grid_style["caption_align"],
        )


def _default_grid_region(
    *,
    header_content_top_y: float,
    layout: Mapping[str, Any],
    has_takeaway: bool,
) -> Box:
    grid_x = float(layout.get("grid_x", 0.90))
    grid_y = float(layout.get("grid_y", header_content_top_y + float(layout.get("content_to_grid_gap", 0.16))))
    grid_w = float(layout.get("grid_w", 11.20))

    if "grid_h" in layout:
        grid_h = float(layout["grid_h"])
    else:
        bottom_limit = float(layout.get("grid_bottom_limit", 5.70 if has_takeaway else 6.10))
        grid_h = max(1.20, bottom_limit - grid_y)

    return Box(grid_x, grid_y, grid_w, grid_h)


def build_card_grid_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    slide_theme_name = spec.get("theme", "concept")
    theme_obj = get_theme(slide_theme_name=slide_theme_name)

    bg = spec.get("background") or choose_background(slide_theme_name, counters)
    slide = new_slide(prs, bg)

    layout = dict(spec.get("layout", {}) or {})
    grid = dict(spec.get("grid", {}) or {})
    rows = int(grid.get("rows", 1))
    cols = int(grid.get("cols", 3))
    cards = list(grid.get("cards", []) or [])

    takeaway = str(spec.get("takeaway", "")).strip()

    header_result = render_header_from_spec(
        slide,
        spec,
        theme=theme_obj,
    )

    resolved_grid_style = _resolve_grid_style(spec, theme_obj=theme_obj)

    region_dict = layout.get("grid_region")
    if isinstance(region_dict, Mapping):
        fallback_region = _default_grid_region(
            header_content_top_y=header_result.content_top_y,
            layout=layout,
            has_takeaway=bool(takeaway),
        )
        region = _box_from_dict(region_dict, fallback_region)
    else:
        region = _default_grid_region(
            header_content_top_y=header_result.content_top_y,
            layout=layout,
            has_takeaway=bool(takeaway),
        )

    gap_x = float(layout.get("gap_x", 0.28))
    gap_y = float(layout.get("gap_y", 0.0))

    row_boxes = distribute_rows(region, rows, gap=gap_y)

    idx = 0
    for row_box in row_boxes:
        col_boxes = distribute_columns(row_box, cols, gap=gap_x)
        for card_box in col_boxes:
            if idx >= len(cards):
                break
            _add_grid_card(
                slide,
                cards[idx],
                card_box,
                idx,
                grid_style=resolved_grid_style,
                layout=layout,
            )
            idx += 1

    if takeaway:
        takeaway_y = float(layout.get("takeaway_y", region.bottom + 0.30))
        takeaway_h = float(layout.get("takeaway_h", 0.26))
        takeaway_box = Box(
            float(layout.get("takeaway_x", 1.02)),
            takeaway_y,
            float(layout.get("takeaway_w", 10.96)),
            takeaway_h,
        )
        takeaway_font = _fit_text_size(
            takeaway,
            takeaway_box,
            min_font=int(layout.get("takeaway_min_font", 11)),
            max_font=int(layout.get("takeaway_max_font", 13)),
            max_lines=int(layout.get("takeaway_max_lines", 2)),
        )
        add_textbox(
            slide,
            x=takeaway_box.x,
            y=takeaway_box.y,
            w=takeaway_box.w,
            h=takeaway_box.h,
            text=takeaway,
            font_name=BODY_FONT,
            font_size=takeaway_font,
            color=resolved_grid_style["takeaway_color"],
            bold=bool(layout.get("takeaway_bold", False)),
            align=layout.get("takeaway_align", PP_ALIGN.CENTER),
        )

    add_footer(
        slide,
        dark=resolved_grid_style["footer_dark"],
        color=resolved_grid_style["footer_color"],
    )
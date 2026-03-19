from __future__ import annotations

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


def _join_items(items: list[str]) -> str:
    return "   •   ".join(item.strip() for item in items if item and item.strip())


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
    triple_style = dict(spec.get("triple_role_style", {}) or {})

    panel_fill_default = theme_obj.box_fill_color
    if panel_fill_default is None:
        panel_fill_default = theme_obj.panel_fill_color
    if panel_fill_default is None:
        panel_fill_default = OFFWHITE

    return {
        "panel_fill_color": resolve_color(
            triple_style.get("panel_fill_color"),
            panel_fill_default,
        ),
        "panel_line_color": resolve_color(
            triple_style.get("panel_line_color"),
            theme_obj.box_line_color,
        ),
        "panel_title_color": resolve_color(
            triple_style.get("panel_title_color"),
            theme_obj.box_title_color,
        ),
        "panel_caption_color": resolve_color(
            triple_style.get("panel_caption_color"),
            theme_obj.subtitle_color,
        ),
        "panel_formula_color": resolve_color(
            triple_style.get("panel_formula_color"),
            theme_obj.body_color,
        ),
        "panel_visual_variant": str(
            triple_style.get("panel_visual_variant", theme_obj.panel_visual_variant)
        ),
        "panel_line_width_pt": float(
            triple_style.get("panel_line_width_pt", 1.25)
        ),
        "bullets_color": resolve_color(
            triple_style.get("bullets_color"),
            theme_obj.subtitle_color,
        ),
        "formulas_color": resolve_color(
            triple_style.get("formulas_color"),
            theme_obj.body_color,
        ),
        "takeaway_color": resolve_color(
            triple_style.get("takeaway_color"),
            theme_obj.subtitle_color,
        ),
        "footer_color": resolve_color(
            triple_style.get("footer_color"),
            theme_obj.footer_color,
        ),
        "footer_dark": bool(
            triple_style.get("footer_dark", theme_obj.footer_dark)
        ),
    }


def _resolve_panel_style(
    panel: Mapping[str, Any],
    *,
    triple_style: Mapping[str, Any],
) -> dict[str, Any]:
    panel_style = dict(panel.get("style", {}) or {})
    return {
        "fill_color": resolve_color(
            panel_style.get("fill_color"),
            triple_style["panel_fill_color"],
        ),
        "line_color": resolve_color(
            panel_style.get("line_color"),
            triple_style["panel_line_color"],
        ),
        "title_color": resolve_color(
            panel_style.get("title_color"),
            triple_style["panel_title_color"],
        ),
        "caption_color": resolve_color(
            panel_style.get("caption_color"),
            triple_style["panel_caption_color"],
        ),
        "formula_color": resolve_color(
            panel_style.get("formula_color"),
            triple_style["panel_formula_color"],
        ),
        "visual_variant": str(
            panel_style.get("visual_variant", triple_style["panel_visual_variant"])
        ),
        "line_width_pt": float(
            panel_style.get("line_width_pt", triple_style["panel_line_width_pt"])
        ),
    }


def _add_role_panel(
    slide,
    panel: dict[str, Any],
    panel_box: Box,
    idx: int,
    *,
    triple_style: Mapping[str, Any],
    layout: Mapping[str, Any],
) -> None:
    resolved_panel_style = _resolve_panel_style(panel, triple_style=triple_style)

    add_rounded_box(
        slide,
        panel_box.x,
        panel_box.y,
        panel_box.w,
        panel_box.h,
        line_color=resolved_panel_style["line_color"],
        fill_color=resolved_panel_style["fill_color"],
        line_width_pt=resolved_panel_style["line_width_pt"],
    )

    title_text = str(panel.get("title", "")).strip()
    caption_text = str(panel.get("caption", "")).strip()
    formula_text = str(panel.get("formula", "")).strip()

    title_h = float(panel.get("title_h", layout.get("panel_title_h", 0.24)))
    caption_h = float(
        panel.get("caption_h", layout.get("panel_caption_h", 0.22 if caption_text else 0.0))
    )
    formula_h = float(
        panel.get("formula_h", layout.get("panel_formula_h", 0.18 if formula_text else 0.0))
    )

    title_box = Box(panel_box.x + 0.10, panel_box.y + 0.10, panel_box.w - 0.20, title_h)
    title_font = _fit_text_size(
        title_text,
        title_box,
        min_font=int(panel.get("title_min_font", layout.get("panel_title_min_font", 12))),
        max_font=int(panel.get("title_max_font", layout.get("panel_title_max_font", 15))),
        max_lines=int(panel.get("title_max_lines", layout.get("panel_title_max_lines", 2))),
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
        color=resolved_panel_style["title_color"],
        bold=True,
        align=PP_ALIGN.CENTER,
    )

    top_pad = float(panel.get("top_pad", layout.get("panel_top_pad", 0.10)))
    above_gap = float(panel.get("gap_above_visual", layout.get("panel_gap_above_visual", 0.10)))
    below_gap = float(panel.get("gap_below_visual", layout.get("panel_gap_below_visual", 0.08)))
    bottom_pad = float(panel.get("bottom_pad", layout.get("panel_bottom_pad", 0.12)))

    visual_h = panel_box.h - (
        top_pad + title_h + above_gap + caption_h + formula_h + below_gap + bottom_pad
    )
    visual_h = max(0.85, visual_h)

    visual_box = Box(
        panel_box.x + 0.14,
        panel_box.y + top_pad + title_h + above_gap,
        panel_box.w - 0.28,
        visual_h,
    )

    visual_override = panel.get("visual_box")
    if isinstance(visual_override, Mapping):
        visual_box = _box_from_dict(visual_override, visual_box)

    add_mini_visual(
        slide,
        kind=str(panel.get("mini_visual", "")),
        x=visual_box.x,
        y=visual_box.y,
        w=visual_box.w,
        h=visual_box.h,
        suffix=f"_triple_role_{idx}",
        variant=resolved_panel_style["visual_variant"],
    )

    current_y = visual_box.bottom + float(
        panel.get("below_visual_gap", layout.get("panel_below_visual_gap", 0.08))
    )

    if caption_text:
        caption_box = Box(panel_box.x + 0.12, current_y, panel_box.w - 0.24, caption_h)
        caption_font = _fit_text_size(
            caption_text,
            caption_box,
            min_font=int(panel.get("caption_min_font", layout.get("panel_caption_min_font", 11))),
            max_font=int(panel.get("caption_max_font", layout.get("panel_caption_max_font", 13))),
            max_lines=int(panel.get("caption_max_lines", layout.get("panel_caption_max_lines", 2))),
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
            color=resolved_panel_style["caption_color"],
            bold=False,
            align=PP_ALIGN.CENTER,
        )
        current_y += caption_h + float(
            panel.get("caption_to_formula_gap", layout.get("caption_to_formula_gap", 0.04))
        )

    if formula_text:
        formula_box = Box(panel_box.x + 0.10, current_y, panel_box.w - 0.20, formula_h)
        formula_font = _fit_text_size(
            formula_text,
            formula_box,
            min_font=int(panel.get("formula_min_font", layout.get("panel_formula_min_font", 11))),
            max_font=int(panel.get("formula_max_font", layout.get("panel_formula_max_font", 13))),
            max_lines=int(panel.get("formula_max_lines", layout.get("panel_formula_max_lines", 2))),
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
            color=resolved_panel_style["formula_color"],
            bold=False,
            align=PP_ALIGN.CENTER,
        )


def _default_panel_region(
    *,
    header_content_top_y: float,
    layout: Mapping[str, Any],
    has_bullets: bool,
    has_formulas: bool,
    has_takeaway: bool,
) -> Box:
    panel_x = float(layout.get("panel_x", 0.88))
    panel_y = float(
        layout.get(
            "panel_y",
            header_content_top_y + float(layout.get("content_to_panel_gap", 0.18)),
        )
    )
    panel_w = float(layout.get("panel_w", 11.24))

    if "panel_h" in layout:
        panel_h = float(layout["panel_h"])
    else:
        if has_takeaway:
            bottom_limit = float(layout.get("panel_bottom_limit", 4.86))
        elif has_formulas:
            bottom_limit = float(layout.get("panel_bottom_limit", 5.20))
        elif has_bullets:
            bottom_limit = float(layout.get("panel_bottom_limit", 5.00))
        else:
            bottom_limit = float(layout.get("panel_bottom_limit", 5.20))
        panel_h = max(1.30, bottom_limit - panel_y)

    return Box(panel_x, panel_y, panel_w, panel_h)


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
    panels = list(spec.get("panels", []) or [])
    bullets = list(spec.get("bullets", []) or [])
    formulas = list(spec.get("formulas", []) or [])
    takeaway = str(spec.get("takeaway", "")).strip()

    header_result = render_header_from_spec(
        slide,
        spec,
        theme=theme_obj,
    )

    triple_style = _resolve_triple_role_style(spec, theme_obj=theme_obj)

    region_dict = layout.get("panel_region")
    if isinstance(region_dict, Mapping):
        fallback_region = _default_panel_region(
            header_content_top_y=header_result.content_top_y,
            layout=layout,
            has_bullets=bool(bullets),
            has_formulas=bool(formulas),
            has_takeaway=bool(takeaway),
        )
        region = _box_from_dict(region_dict, fallback_region)
    else:
        region = _default_panel_region(
            header_content_top_y=header_result.content_top_y,
            layout=layout,
            has_bullets=bool(bullets),
            has_formulas=bool(formulas),
            has_takeaway=bool(takeaway),
        )

    gap = float(layout.get("panel_gap", 0.24))
    count = max(1, len(panels))
    panel_boxes = distribute_columns(region, count, gap=gap)

    for idx, panel in enumerate(panels):
        _add_role_panel(
            slide,
            panel,
            panel_boxes[idx],
            idx,
            triple_style=triple_style,
            layout=layout,
        )

    if bullets:
        bullets_text = _join_items(bullets)
        bullets_box = Box(
            float(layout.get("bullets_x", 1.02)),
            float(layout.get("bullets_y", region.bottom + 0.20)),
            float(layout.get("bullets_w", 10.96)),
            float(layout.get("bullets_h", 0.24)),
        )
        bullets_font = _fit_text_size(
            bullets_text,
            bullets_box,
            min_font=int(layout.get("bullets_min_font", 12)),
            max_font=int(layout.get("bullets_max_font", 14)),
            max_lines=int(layout.get("bullets_max_lines", 2)),
        )
        add_textbox(
            slide,
            x=bullets_box.x,
            y=bullets_box.y,
            w=bullets_box.w,
            h=bullets_box.h,
            text=bullets_text,
            font_name=BODY_FONT,
            font_size=bullets_font,
            color=triple_style["bullets_color"],
            bold=bool(layout.get("bullets_bold", False)),
            align=layout.get("bullets_align", PP_ALIGN.CENTER),
        )

    if formulas:
        formulas_text = _join_items(formulas)
        formulas_box = Box(
            float(layout.get("formula_x", 1.02)),
            float(layout.get("formula_y", region.bottom + 0.56)),
            float(layout.get("formula_w", 10.96)),
            float(layout.get("formula_h", 0.20)),
        )
        formulas_font = _fit_text_size(
            formulas_text,
            formulas_box,
            min_font=int(layout.get("formula_min_font", 12)),
            max_font=int(layout.get("formula_max_font", 14)),
            max_lines=int(layout.get("formula_max_lines", 2)),
        )
        add_textbox(
            slide,
            x=formulas_box.x,
            y=formulas_box.y,
            w=formulas_box.w,
            h=formulas_box.h,
            text=formulas_text,
            font_name=FORMULA_FONT,
            font_size=formulas_font,
            color=triple_style["formulas_color"],
            bold=False,
            align=layout.get("formula_align", PP_ALIGN.CENTER),
        )

    if takeaway:
        takeaway_box = Box(
            float(layout.get("takeaway_x", 1.02)),
            float(layout.get("takeaway_y", region.bottom + 0.92)),
            float(layout.get("takeaway_w", 10.96)),
            float(layout.get("takeaway_h", 0.24)),
        )
        takeaway_font = _fit_text_size(
            takeaway,
            takeaway_box,
            min_font=int(layout.get("takeaway_min_font", 12)),
            max_font=int(layout.get("takeaway_max_font", 14)),
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
            color=triple_style["takeaway_color"],
            bold=bool(layout.get("takeaway_bold", False)),
            align=layout.get("takeaway_align", PP_ALIGN.CENTER),
        )

    add_footer(
        slide,
        dark=triple_style["footer_dark"],
        color=triple_style["footer_color"],
    )
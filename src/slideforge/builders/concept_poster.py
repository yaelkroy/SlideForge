from __future__ import annotations

from typing import Any, Mapping

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, OFFWHITE
from slideforge.config.themes import SlideTheme, get_theme, resolve_color
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, layout_concept_poster
from slideforge.render.header import render_header_from_spec
from slideforge.render.primitives import add_footer, add_rounded_box, add_textbox


def _join_items(items: list[str]) -> str:
    cleaned = [item.strip() for item in items if item and item.strip()]
    return "   •   ".join(cleaned)


def _add_fitted_text(
    slide,
    *,
    box: Box,
    text: str,
    font_name: str,
    font_size: int,
    color,
    bold: bool = False,
    align=PP_ALIGN.CENTER,
) -> None:
    if not text.strip() or box.w <= 0 or box.h <= 0:
        return

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


def _box_from_dict(raw: Mapping[str, Any], fallback: Box) -> Box:
    return Box(
        raw.get("x", fallback.x),
        raw.get("y", fallback.y),
        raw.get("w", fallback.w),
        raw.get("h", fallback.h),
    )


def _resolve_poster_style(
    spec: Mapping[str, Any],
    *,
    theme_obj: SlideTheme,
) -> dict[str, Any]:
    poster_style = dict(spec.get("poster_style", {}) or {})

    box_fill_default = theme_obj.box_fill_color
    if box_fill_default is None:
        box_fill_default = theme_obj.panel_fill_color
    if box_fill_default is None:
        box_fill_default = OFFWHITE

    return {
        "poster_fill_color": resolve_color(
            poster_style.get("poster_fill_color"),
            box_fill_default,
        ),
        "poster_line_color": resolve_color(
            poster_style.get("poster_line_color"),
            theme_obj.box_line_color,
        ),
        "poster_line_width_pt": float(
            poster_style.get("poster_line_width_pt", 1.25)
        ),
        "visual_variant": str(
            poster_style.get("visual_variant", theme_obj.panel_visual_variant)
        ),
        "explanation_color": resolve_color(
            poster_style.get("explanation_color"),
            theme_obj.subtitle_color,
        ),
        "bullets_color": resolve_color(
            poster_style.get("bullets_color"),
            theme_obj.subtitle_color,
        ),
        "formulas_color": resolve_color(
            poster_style.get("formulas_color"),
            theme_obj.body_color,
        ),
        "note_color": resolve_color(
            poster_style.get("note_color"),
            theme_obj.subtitle_color,
        ),
        "takeaway_color": resolve_color(
            poster_style.get("takeaway_color"),
            theme_obj.subtitle_color,
        ),
        "footer_color": resolve_color(
            poster_style.get("footer_color"),
            theme_obj.footer_color,
        ),
        "footer_dark": bool(
            poster_style.get("footer_dark", theme_obj.footer_dark)
        ),
        "show_anchor_text": bool(
            poster_style.get("show_anchor_text", False)
        ),
    }


def build_concept_poster_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    slide_theme_name = spec.get("theme", "concept")
    theme_obj = get_theme(slide_theme_name=slide_theme_name)

    bg = spec.get("background") or choose_background(slide_theme_name, counters)
    slide = new_slide(prs, bg)

    layout = dict(spec.get("layout", {}) or {})
    poster_style = _resolve_poster_style(spec, theme_obj=theme_obj)

    mini_visual = str(spec.get("mini_visual", "")).strip()

    explanation = (
        str(spec.get("text_explanation", "")).strip()
        or str(spec.get("explanation", "")).strip()
    )

    bullets = list(spec.get("bullets", []) or [])
    bullets_text = _join_items(bullets)

    formulas = list(spec.get("formulas", []) or [])
    formulas_text = _join_items(formulas)

    anchor_text = str(spec.get("concrete_example_anchor", "")).strip()
    visible_anchor_text = str(spec.get("visible_anchor_text", "")).strip()
    show_anchor_text = bool(
        spec.get("show_anchor_text", poster_style["show_anchor_text"])
    )
    note_text = visible_anchor_text or (anchor_text if show_anchor_text else "")

    takeaway = str(spec.get("takeaway", "")).strip()

    header_result = render_header_from_spec(
        slide,
        spec,
        theme=theme_obj,
    )

    fallback_outer_box = Box(
        float(layout.get("poster_x", 0.96)),
        float(
            layout.get(
                "poster_y",
                header_result.content_top_y + float(layout.get("content_to_poster_gap", 0.12)),
            )
        ),
        float(layout.get("poster_w", 11.10)),
        float(layout.get("poster_h", 4.98)),
    )

    poster_box_dict = layout.get("poster_box")
    outer_box = (
        _box_from_dict(poster_box_dict, fallback_outer_box)
        if isinstance(poster_box_dict, Mapping)
        else fallback_outer_box
    )

    add_rounded_box(
        slide,
        outer_box.x,
        outer_box.y,
        outer_box.w,
        outer_box.h,
        line_color=poster_style["poster_line_color"],
        fill_color=poster_style["poster_fill_color"],
        line_width_pt=poster_style["poster_line_width_pt"],
    )

    poster_layout = layout_concept_poster(
        outer_box,
        explanation=explanation,
        bullets_text=bullets_text,
        formulas_text=formulas_text,
        note_text=note_text,
        takeaway_text=takeaway,
        top_pad=float(layout.get("top_pad", 0.18)),
        bottom_pad=float(layout.get("bottom_pad", 0.14)),
        gap=float(layout.get("content_gap", 0.08)),
        side_pad=float(layout.get("side_pad", 0.22)),
        visual_min_share=float(layout.get("visual_min_share", 0.62)),
        visual_max_share=float(layout.get("visual_max_share", 0.80)),
    )

    visual_override = layout.get("visual_box")
    visual_box = (
        _box_from_dict(visual_override, poster_layout.visual_box)
        if isinstance(visual_override, Mapping)
        else poster_layout.visual_box
    )

    if mini_visual:
        add_mini_visual(
            slide,
            kind=mini_visual,
            x=visual_box.x,
            y=visual_box.y,
            w=visual_box.w,
            h=visual_box.h,
            suffix="_concept_poster",
            variant=poster_style["visual_variant"],
        )

    fits = poster_layout.text_fits
    boxes = poster_layout.text_boxes

    if "explanation" in boxes and "explanation" in fits:
        _add_fitted_text(
            slide,
            box=boxes["explanation"],
            text=explanation,
            font_name=BODY_FONT,
            font_size=max(
                int(layout.get("explanation_min_font", 15)),
                fits["explanation"].font_size,
            ),
            color=poster_style["explanation_color"],
            bold=False,
            align=layout.get("explanation_align", PP_ALIGN.CENTER),
        )

    if "bullets" in boxes and "bullets" in fits:
        _add_fitted_text(
            slide,
            box=boxes["bullets"],
            text=bullets_text,
            font_name=BODY_FONT,
            font_size=max(
                int(layout.get("bullets_min_font", 13)),
                fits["bullets"].font_size,
            ),
            color=poster_style["bullets_color"],
            bold=bool(layout.get("bullets_bold", False)),
            align=layout.get("bullets_align", PP_ALIGN.CENTER),
        )

    if "formulas" in boxes and "formulas" in fits:
        _add_fitted_text(
            slide,
            box=boxes["formulas"],
            text=formulas_text,
            font_name=FORMULA_FONT,
            font_size=max(
                int(layout.get("formulas_min_font", 12)),
                fits["formulas"].font_size,
            ),
            color=poster_style["formulas_color"],
            bold=False,
            align=layout.get("formulas_align", PP_ALIGN.CENTER),
        )

    if "note" in boxes and "note" in fits:
        _add_fitted_text(
            slide,
            box=boxes["note"],
            text=note_text,
            font_name=BODY_FONT,
            font_size=max(
                int(layout.get("note_min_font", 12)),
                fits["note"].font_size,
            ),
            color=poster_style["note_color"],
            bold=bool(layout.get("note_bold", False)),
            align=layout.get("note_align", PP_ALIGN.CENTER),
        )

    if "takeaway" in boxes and "takeaway" in fits:
        _add_fitted_text(
            slide,
            box=boxes["takeaway"],
            text=takeaway,
            font_name=BODY_FONT,
            font_size=max(
                int(layout.get("takeaway_min_font", 12)),
                fits["takeaway"].font_size,
            ),
            color=poster_style["takeaway_color"],
            bold=True,
            align=layout.get("takeaway_align", PP_ALIGN.CENTER),
        )

    add_footer(
        slide,
        dark=poster_style["footer_dark"],
        color=poster_style["footer_color"],
    )
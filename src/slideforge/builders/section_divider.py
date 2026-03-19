from __future__ import annotations

from typing import Any, Mapping

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, OFFWHITE, TITLE_FONT
from slideforge.config.themes import SlideTheme, get_theme, resolve_color
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, fit_text
from slideforge.render.primitives import add_footer, add_textbox


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


def _resolve_divider_style(
    spec: Mapping[str, Any],
    *,
    theme_obj: SlideTheme,
) -> dict[str, Any]:
    section_style = dict(spec.get("section_style", {}) or {})

    return {
        "title_color": resolve_color(section_style.get("title_color"), theme_obj.title_color),
        "subtitle_color": resolve_color(section_style.get("subtitle_color"), theme_obj.subtitle_color),
        "label_color": resolve_color(section_style.get("label_color"), theme_obj.body_color),
        "anchor_color": resolve_color(section_style.get("anchor_color"), theme_obj.ghost_text_color),
        "footer_color": resolve_color(section_style.get("footer_color"), theme_obj.footer_color),
        "footer_dark": bool(section_style.get("footer_dark", theme_obj.footer_dark)),
        "visual_variant": str(section_style.get("visual_variant", theme_obj.panel_visual_variant)),
        "show_anchor_text": bool(section_style.get("show_anchor_text", False)),
    }


def build_section_divider_slide(
    prs: Presentation,
    spec: dict[str, Any],
    counters: dict[str, int],
) -> None:
    slide_theme_name = spec.get("theme", "section")
    theme_obj = get_theme(slide_theme_name=slide_theme_name)

    bg = spec.get("background") or choose_background(slide_theme_name, counters)
    slide = new_slide(prs, bg)

    title = str(spec.get("title") or spec["slide_title"]).strip()
    subtitle = str(spec.get("subtitle", "")).strip()
    layout = dict(spec.get("layout", {}) or {})
    section_visual = dict(spec.get("section_visual", {}) or {})
    style = _resolve_divider_style(spec, theme_obj=theme_obj)

    title_region_dict = layout.get(
        "title_region",
        {"x": 1.00, "y": 1.95, "w": 11.00, "h": 0.92},
    )
    subtitle_region_dict = layout.get(
        "subtitle_region",
        {"x": 1.20, "y": 2.90, "w": 10.60, "h": 0.42},
    )
    band_dict = layout.get(
        "band_region",
        {"x": 0.90, "y": 3.52, "w": 11.55, "h": 1.52},
    )

    title_box = _box_from_dict(title_region_dict, Box(1.00, 1.95, 11.00, 0.92))
    subtitle_box = _box_from_dict(subtitle_region_dict, Box(1.20, 2.90, 10.60, 0.42))
    band_box = _box_from_dict(band_dict, Box(0.90, 3.52, 11.55, 1.52))

    title_font = _fit_text_size(
        title,
        title_box,
        min_font=int(layout.get("title_min_font", 28)),
        max_font=int(layout.get("title_max_font", 34)),
        max_lines=int(layout.get("title_max_lines", 2)),
    )
    add_textbox(
        slide,
        x=title_box.x,
        y=title_box.y,
        w=title_box.w,
        h=title_box.h,
        text=title,
        font_name=TITLE_FONT,
        font_size=title_font,
        color=style["title_color"],
        bold=True,
        align=layout.get("title_align", PP_ALIGN.CENTER),
    )

    if subtitle:
        subtitle_font = _fit_text_size(
            subtitle,
            subtitle_box,
            min_font=int(layout.get("subtitle_min_font", 15)),
            max_font=int(layout.get("subtitle_max_font", 18)),
            max_lines=int(layout.get("subtitle_max_lines", 2)),
        )
        add_textbox(
            slide,
            x=subtitle_box.x,
            y=subtitle_box.y,
            w=subtitle_box.w,
            h=subtitle_box.h,
            text=subtitle,
            font_name=BODY_FONT,
            font_size=subtitle_font,
            color=style["subtitle_color"],
            bold=False,
            align=layout.get("subtitle_align", PP_ALIGN.CENTER),
        )

    elements = list(section_visual.get("elements", []) or [])
    count = len(elements)

    if count > 0:
        side_pad = float(layout.get("band_side_pad", 0.35))
        inter_gap = float(layout.get("band_gap", 0.30))
        usable_w = band_box.w - 2 * side_pad - inter_gap * max(0, count - 1)
        elem_w = usable_w / count if count else usable_w
        elem_h = float(layout.get("element_h", min(1.24, band_box.h - 0.22)))
        elem_y = band_box.y + (band_box.h - elem_h) / 2

        label_h = float(layout.get("label_h", 0.22))
        label_gap = float(layout.get("label_gap", 0.06))
        visual_h = max(0.60, elem_h - label_h - label_gap)

        for idx, elem in enumerate(elements):
            x = band_box.x + side_pad + idx * (elem_w + inter_gap)
            label = str(elem.get("label", "")).strip()

            if label:
                visual_y = elem_y
                add_mini_visual(
                    slide,
                    kind=str(elem.get("kind", "")),
                    x=x,
                    y=visual_y,
                    w=elem_w,
                    h=visual_h,
                    suffix=f"_section_divider_{idx}",
                    variant=str(elem.get("visual_variant", style["visual_variant"])),
                )

                label_box = Box(x, visual_y + visual_h + label_gap, elem_w, label_h)
                label_font = _fit_text_size(
                    label,
                    label_box,
                    min_font=int(layout.get("label_min_font", 12)),
                    max_font=int(layout.get("label_max_font", 15)),
                    max_lines=1,
                )
                add_textbox(
                    slide,
                    x=label_box.x,
                    y=label_box.y,
                    w=label_box.w,
                    h=label_box.h,
                    text=label,
                    font_name=BODY_FONT,
                    font_size=label_font,
                    color=style["label_color"],
                    bold=False,
                    align=PP_ALIGN.CENTER,
                )
            else:
                add_mini_visual(
                    slide,
                    kind=str(elem.get("kind", "")),
                    x=x,
                    y=elem_y + (elem_h - visual_h) / 2,
                    w=elem_w,
                    h=visual_h,
                    suffix=f"_section_divider_{idx}",
                    variant=str(elem.get("visual_variant", style["visual_variant"])),
                )

    # IMPORTANT:
    # concrete_example_anchor is treated as design guidance by default
    # and is NOT rendered unless explicitly enabled.
    anchor_text = str(spec.get("concrete_example_anchor", "")).strip()
    visible_anchor_text = str(spec.get("visible_anchor_text", "")).strip()

    show_anchor_text = bool(
        spec.get("show_anchor_text", style["show_anchor_text"])
    )
    bottom_text = visible_anchor_text or (anchor_text if show_anchor_text else "")

    if bottom_text:
        words_box = Box(
            float(layout.get("faint_words_x", 1.10)),
            float(layout.get("faint_words_y", 5.82)),
            float(layout.get("faint_words_w", 11.00)),
            float(layout.get("faint_words_h", 0.22)),
        )
        words_font = _fit_text_size(
            bottom_text,
            words_box,
            min_font=int(layout.get("faint_words_min_font", 11)),
            max_font=int(layout.get("faint_words_max_font", 14)),
            max_lines=int(layout.get("faint_words_max_lines", 1)),
        )
        add_textbox(
            slide,
            x=words_box.x,
            y=words_box.y,
            w=words_box.w,
            h=words_box.h,
            text=bottom_text,
            font_name=BODY_FONT,
            font_size=words_font,
            color=style["anchor_color"],
            bold=False,
            align=layout.get("faint_words_align", PP_ALIGN.CENTER),
        )

    add_footer(
        slide,
        dark=style["footer_dark"],
        color=style["footer_color"],
    )
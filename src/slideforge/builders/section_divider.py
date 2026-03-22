from __future__ import annotations

import warnings
from typing import Any, Mapping

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual, resolve_visual_kind
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, OFFWHITE, TITLE_FONT
from slideforge.config.themes import SlideTheme, get_theme, resolve_color
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, fit_text
from slideforge.render.primitives import add_footer, add_textbox

try:
    from slideforge.assets.packs.geometry.heroes import get_visual_metadata as _hero_visual_metadata
except Exception:  # pragma: no cover - optional during bootstrap
    _hero_visual_metadata = None

try:
    from slideforge.assets.packs.geometry.norms_dots_angles import get_visual_metadata as _nda_visual_metadata
except Exception:  # pragma: no cover - optional during bootstrap
    _nda_visual_metadata = None


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


def _lookup_visual_metadata(kind: str) -> dict[str, Any]:
    canonical = resolve_visual_kind(kind)
    for getter in (_hero_visual_metadata, _nda_visual_metadata):
        if getter is None:
            continue
        try:
            metadata = getter(canonical)
        except Exception:
            metadata = {}
        if metadata:
            return dict(metadata)
    return {}


def _inset_box(box: Box, *, pad_x: float, pad_y: float) -> Box:
    return Box(
        box.x + pad_x,
        box.y + pad_y,
        max(0.10, box.w - 2 * pad_x),
        max(0.10, box.h - 2 * pad_y),
    )


def _fit_visual_box_to_contract(
    available_box: Box,
    *,
    kind: str,
) -> Box:
    metadata = _lookup_visual_metadata(kind)
    if not metadata:
        return available_box

    preferred_aspect_ratio = float(metadata.get("preferred_aspect_ratio", 0.0) or 0.0)
    min_width = float(metadata.get("min_width_in", 0.0) or 0.0)
    min_height = float(metadata.get("min_height_in", 0.0) or 0.0)

    if preferred_aspect_ratio <= 0:
        return available_box

    width_limited_height = available_box.w / preferred_aspect_ratio
    target_height = min(available_box.h, width_limited_height)

    if min_height > 0:
        target_height = max(target_height, min(min_height, available_box.h))

    target_width = target_height * preferred_aspect_ratio
    if min_width > 0:
        target_width = max(target_width, min(min_width, available_box.w))

    if target_width > available_box.w:
        target_width = available_box.w
        target_height = min(available_box.h, target_width / preferred_aspect_ratio)

    if target_height > available_box.h:
        target_height = available_box.h
        target_width = min(available_box.w, target_height * preferred_aspect_ratio)

    return Box(
        available_box.x + (available_box.w - target_width) / 2,
        available_box.y + (available_box.h - target_height) / 2,
        target_width,
        target_height,
    )


def _warn_if_contract_is_still_violated(kind: str, visual_box: Box, *, slide_title: str) -> None:
    metadata = _lookup_visual_metadata(kind)
    if not metadata:
        return

    min_height = float(metadata.get("min_height_in", 0.0) or 0.0)
    min_width = float(metadata.get("min_width_in", 0.0) or 0.0)
    preferred_aspect_ratio = float(metadata.get("preferred_aspect_ratio", 0.0) or 0.0)
    preferred_height = float(metadata.get("preferred_height_in", 0.0) or 0.0)
    actual_aspect_ratio = visual_box.w / max(visual_box.h, 0.01)

    problems: list[str] = []
    if min_height > 0 and visual_box.h + 1e-6 < min_height:
        problems.append(f"height {visual_box.h:.2f}in < min {min_height:.2f}in")
    if min_width > 0 and visual_box.w + 1e-6 < min_width:
        problems.append(f"width {visual_box.w:.2f}in < min {min_width:.2f}in")
    if preferred_height > 0 and visual_box.h + 1e-6 < preferred_height:
        problems.append(f"height {visual_box.h:.2f}in < preferred {preferred_height:.2f}in")
    if preferred_aspect_ratio > 0 and actual_aspect_ratio > preferred_aspect_ratio * 1.18:
        problems.append(
            f"aspect {actual_aspect_ratio:.2f} is wider than preferred {preferred_aspect_ratio:.2f}"
        )

    if problems:
        warnings.warn(
            (
                f"Section divider visual '{resolve_visual_kind(kind)}' on slide '{slide_title}' "
                f"is still under-allocated after layout resolution: {', '.join(problems)}."
            ),
            stacklevel=2,
        )


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
        unlabeled_single_hero = (
            count == 1
            and bool(layout.get("expand_single_hero", True))
            and not str(elements[0].get("label", "")).strip()
        )

        if unlabeled_single_hero:
            elem = elements[0]
            available_box = _inset_box(
                band_box,
                pad_x=float(layout.get("hero_pad_x", 0.14)),
                pad_y=float(layout.get("hero_pad_y", 0.10)),
            )
            visual_box = _fit_visual_box_to_contract(
                available_box,
                kind=str(elem.get("kind", "")),
            )
            add_mini_visual(
                slide,
                kind=str(elem.get("kind", "")),
                x=visual_box.x,
                y=visual_box.y,
                w=visual_box.w,
                h=visual_box.h,
                suffix="_section_divider_0",
                variant=str(elem.get("visual_variant", style["visual_variant"])),
            )
            _warn_if_contract_is_still_violated(
                str(elem.get("kind", "")),
                visual_box,
                slide_title=title,
            )
        else:
            side_pad = float(layout.get("band_side_pad", 0.35))
            inter_gap = float(layout.get("band_gap", 0.30))
            usable_w = band_box.w - 2 * side_pad - inter_gap * max(0, count - 1)
            default_elem_w = usable_w / count if count else usable_w
            default_elem_h = float(layout.get("element_h", min(1.24, band_box.h - 0.22)))
            default_elem_y = band_box.y + (band_box.h - default_elem_h) / 2

            label_h = float(layout.get("label_h", 0.22))
            label_gap = float(layout.get("label_gap", 0.06))

            for idx, elem in enumerate(elements):
                label = str(elem.get("label", "")).strip()
                has_explicit_box = all(key in elem for key in ("x", "y", "w", "h"))

                if has_explicit_box:
                    elem_box = Box(
                        float(elem["x"]),
                        float(elem["y"]),
                        float(elem["w"]),
                        float(elem["h"]),
                    )
                else:
                    x = band_box.x + side_pad + idx * (default_elem_w + inter_gap)
                    elem_box = Box(x, default_elem_y, default_elem_w, default_elem_h)

                if label:
                    visual_box = Box(
                        elem_box.x,
                        elem_box.y,
                        elem_box.w,
                        max(0.60, elem_box.h - label_h - label_gap),
                    )
                else:
                    visual_box = elem_box

                add_mini_visual(
                    slide,
                    kind=str(elem.get("kind", "")),
                    x=visual_box.x,
                    y=visual_box.y,
                    w=visual_box.w,
                    h=visual_box.h,
                    suffix=f"_section_divider_{idx}",
                    variant=str(elem.get("visual_variant", style["visual_variant"])),
                )
                _warn_if_contract_is_still_violated(
                    str(elem.get("kind", "")),
                    visual_box,
                    slide_title=title,
                )

                if label:
                    label_box = Box(
                        elem_box.x,
                        elem_box.y + visual_box.h + label_gap,
                        elem_box.w,
                        label_h,
                    )
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

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


def _clean_items(items: list[str]) -> list[str]:
    return [item.strip() for item in items if item and item.strip()]


def _join_items(items: list[str], *, separator: str = "   •   ") -> str:
    return separator.join(_clean_items(items))


def _format_formulas(
    formulas: list[str],
    *,
    stack_formulas: bool,
    stacked_separator: str = "\n",
    inline_separator: str = "   •   ",
) -> str:
    cleaned = _clean_items(formulas)
    if not cleaned:
        return ""
    if stack_formulas:
        return stacked_separator.join(cleaned)
    return inline_separator.join(cleaned)


def _as_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "y", "on"}:
            return True
        if lowered in {"0", "false", "no", "n", "off"}:
            return False
    return bool(value)


def _infer_dense_math_mode(
    *,
    spec: Mapping[str, Any],
    layout: Mapping[str, Any],
    formulas: list[str],
    bullets: list[str],
    explanation: str,
    takeaway: str,
    note_text: str,
) -> bool:
    explicit = layout.get("dense_math_mode", spec.get("dense_math_mode"))
    if explicit is not None:
        return _as_bool(explicit)

    formula_count = len(_clean_items(formulas))
    bullet_count = len(_clean_items(bullets))
    char_load = sum(len(item) for item in formulas) + len(explanation) + len(note_text) + len(takeaway)

    return (
        formula_count >= 2
        or (formula_count >= 1 and bullet_count >= 3)
        or char_load >= 300
        or _as_bool(spec.get("required_formulas"), False)
    )


def _infer_compact_concept_mode(
    *,
    spec: Mapping[str, Any],
    layout: Mapping[str, Any],
    dense_math_mode: bool,
    formulas: list[str],
    bullets: list[str],
    explanation: str,
    takeaway: str,
    note_text: str,
) -> bool:
    explicit = layout.get("compact_concept_mode", spec.get("compact_concept_mode"))
    if explicit is not None:
        return _as_bool(explicit)

    if dense_math_mode:
        return False

    formula_count = len(_clean_items(formulas))
    bullet_count = len(_clean_items(bullets))
    char_load = len(explanation) + len(takeaway) + len(note_text) + sum(len(item) for item in formulas) + sum(
        len(item) for item in bullets
    )

    return (
        char_load <= 240
        and bullet_count <= 2
        and formula_count <= 2
        and bool(str(spec.get("mini_visual", "")).strip())
    )


def _resolve_priority_options(
    *,
    spec: Mapping[str, Any],
    layout: Mapping[str, Any],
    dense_math_mode: bool,
    compact_concept_mode: bool,
    formulas: list[str],
) -> dict[str, Any]:
    prioritize_text_over_visual = _as_bool(
        layout.get(
            "prioritize_text_over_visual",
            spec.get("prioritize_text_over_visual", False),
        )
    )

    stack_formulas = _as_bool(
        layout.get(
            "stack_formulas",
            spec.get(
                "stack_formulas",
                prioritize_text_over_visual or dense_math_mode or len(_clean_items(formulas)) > 1,
            ),
        )
    )

    if prioritize_text_over_visual:
        visual_min_share = float(layout.get("text_priority_visual_min_share", 0.40))
        visual_max_share = float(layout.get("text_priority_visual_max_share", 0.60))
        preferred_visual_share = float(layout.get("text_priority_preferred_visual_share", 0.48))
        layout_mode = "worked_math"
    elif dense_math_mode:
        visual_min_share = float(layout.get("dense_math_visual_min_share", 0.44))
        visual_max_share = float(layout.get("dense_math_visual_max_share", 0.66))
        preferred_visual_share = float(layout.get("dense_math_preferred_visual_share", 0.54))
        layout_mode = "worked_math"
    elif compact_concept_mode:
        visual_min_share = float(layout.get("compact_visual_min_share", 0.66))
        visual_max_share = float(layout.get("compact_visual_max_share", 0.84))
        preferred_visual_share = float(layout.get("compact_preferred_visual_share", 0.74))
        layout_mode = "compact_concept"
    else:
        visual_min_share = float(layout.get("visual_min_share", 0.60))
        visual_max_share = float(layout.get("visual_max_share", 0.82))
        preferred_visual_share = float(layout.get("preferred_visual_share", 0.70))
        layout_mode = "concept"

    return {
        "dense_math_mode": dense_math_mode,
        "compact_concept_mode": compact_concept_mode,
        "prioritize_text_over_visual": prioritize_text_over_visual,
        "stack_formulas": stack_formulas,
        "visual_min_share": visual_min_share,
        "visual_max_share": visual_max_share,
        "preferred_visual_share": preferred_visual_share,
        "layout_mode": layout_mode,
    }


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


def _candidate_content_variants(
    *,
    explanation: str,
    bullets_text: str,
    formulas_text: str,
    note_text: str,
    takeaway_text: str,
    required_bullets: bool,
    required_formulas: bool,
    required_note: bool,
    required_takeaway: bool,
) -> list[dict[str, str]]:
    def maybe_drop(text: str, required: bool) -> list[str]:
        return [text] if required or not text.strip() else [text, ""]

    variants: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str, str]] = set()

    bullet_options = maybe_drop(bullets_text, required_bullets)
    formula_options = maybe_drop(formulas_text, required_formulas)
    note_options = maybe_drop(note_text, required_note)
    takeaway_options = maybe_drop(takeaway_text, required_takeaway)

    for bullets in bullet_options:
        for formulas in formula_options:
            for note in note_options:
                for takeaway in takeaway_options:
                    variant = {
                        "explanation": explanation,
                        "bullets": bullets,
                        "formulas": formulas,
                        "note": note,
                        "takeaway": takeaway,
                    }
                    key = (
                        variant["explanation"],
                        variant["bullets"],
                        variant["formulas"],
                        variant["note"],
                        variant["takeaway"],
                    )
                    if key in seen:
                        continue
                    seen.add(key)
                    variants.append(variant)

    def richness_score(v: dict[str, str]) -> tuple[int, int, int, int]:
        return (
            1 if v["takeaway"].strip() else 0,
            1 if v["formulas"].strip() else 0,
            1 if v["bullets"].strip() else 0,
            1 if v["note"].strip() else 0,
        )

    variants.sort(key=richness_score, reverse=True)
    return variants


def _variant_text_stats(variant: Mapping[str, str]) -> tuple[int, int]:
    kept_count = sum(
        1
        for key in ("bullets", "formulas", "note", "takeaway")
        if str(variant.get(key, "")).strip()
    )
    text_chars = sum(
        len(str(variant.get(key, "")).strip())
        for key in ("explanation", "bullets", "formulas", "note", "takeaway")
    )
    return kept_count, text_chars


def _choose_best_poster_layout(
    *,
    outer_box: Box,
    explanation: str,
    bullets_text: str,
    formulas_text: str,
    note_text: str,
    takeaway_text: str,
    layout: Mapping[str, Any],
    required_bullets: bool,
    required_formulas: bool,
    required_note: bool,
    required_takeaway: bool,
    prioritize_text_over_visual: bool,
    dense_math_mode: bool,
    compact_concept_mode: bool,
    visual_min_share: float,
    visual_max_share: float,
    preferred_visual_share: float,
    layout_mode: str,
):
    variants = _candidate_content_variants(
        explanation=explanation,
        bullets_text=bullets_text,
        formulas_text=formulas_text,
        note_text=note_text,
        takeaway_text=takeaway_text,
        required_bullets=required_bullets,
        required_formulas=required_formulas,
        required_note=required_note,
        required_takeaway=required_takeaway,
    )

    best_variant = variants[0]
    best_layout = None
    best_score = -10**9

    for variant in variants:
        poster_layout = layout_concept_poster(
            outer_box,
            explanation=variant["explanation"],
            bullets_text=variant["bullets"],
            formulas_text=variant["formulas"],
            note_text=variant["note"],
            takeaway_text=variant["takeaway"],
            top_pad=float(layout.get("top_pad", 0.18)),
            bottom_pad=float(layout.get("bottom_pad", 0.14)),
            gap=float(layout.get("content_gap", 0.08)),
            side_pad=float(layout.get("side_pad", 0.22)),
            visual_min_share=visual_min_share,
            visual_max_share=visual_max_share,
            preferred_visual_share=preferred_visual_share,
            layout_mode=layout_mode,
            dense_math_mode=dense_math_mode,
            prioritize_text_over_visual=prioritize_text_over_visual,
            reserve_formula_first=prioritize_text_over_visual or dense_math_mode,
            compact_concept_mode=compact_concept_mode,
        )

        kept_count, text_chars = _variant_text_stats(variant)
        text_share = max(0.0, 1.0 - poster_layout.visual_share)
        fit_bonus = sum(
            1
            for fit in poster_layout.text_fits.values()
            if getattr(fit, "fits", False)
        )
        unreadable_penalty = sum(
            1
            for fit in poster_layout.text_fits.values()
            if getattr(fit, "fits", True) is False
        )

        if prioritize_text_over_visual:
            score = (
                kept_count * 18.0
                + fit_bonus * 6.0
                + text_share * 100.0
                + min(text_chars, 600) * 0.02
                - poster_layout.visual_share * 18.0
                - unreadable_penalty * 20.0
            )
        elif dense_math_mode:
            score = (
                kept_count * 12.0
                + fit_bonus * 4.0
                + text_share * 55.0
                + min(text_chars, 600) * 0.012
                + poster_layout.visual_share * 18.0
                - unreadable_penalty * 14.0
            )
        elif compact_concept_mode:
            score = (
                poster_layout.visual_share * 115.0
                + fit_bonus * 5.0
                + kept_count * 5.0
                - abs(poster_layout.visual_share - preferred_visual_share) * 45.0
                - unreadable_penalty * 16.0
            )
        else:
            score = (
                poster_layout.visual_share * 100.0
                + kept_count * 3.0
                + fit_bonus * 2.0
                - abs(poster_layout.visual_share - preferred_visual_share) * 24.0
                - unreadable_penalty * 12.0
            )

        if prioritize_text_over_visual:
            if kept_count == 4 and poster_layout.visual_share <= preferred_visual_share:
                return variant, poster_layout
        elif dense_math_mode:
            if kept_count == 4 and poster_layout.visual_share <= preferred_visual_share:
                return variant, poster_layout
            if poster_layout.visual_share >= preferred_visual_share and fit_bonus >= max(1, kept_count - 1):
                return variant, poster_layout
        elif compact_concept_mode:
            if fit_bonus >= max(1, kept_count) and abs(poster_layout.visual_share - preferred_visual_share) <= 0.05:
                return variant, poster_layout
        else:
            if poster_layout.visual_share >= preferred_visual_share and fit_bonus >= max(1, kept_count - 1):
                return variant, poster_layout

        if score > best_score:
            best_score = score
            best_variant = variant
            best_layout = poster_layout

    return best_variant, best_layout


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

    anchor_text = str(spec.get("concrete_example_anchor", "")).strip()
    visible_anchor_text = str(spec.get("visible_anchor_text", "")).strip()
    show_anchor_text = bool(
        spec.get("show_anchor_text", poster_style["show_anchor_text"])
    )
    note_text = visible_anchor_text or (anchor_text if show_anchor_text else "")

    takeaway = str(spec.get("takeaway", "")).strip()

    dense_math_mode = _infer_dense_math_mode(
        spec=spec,
        layout=layout,
        formulas=formulas,
        bullets=bullets,
        explanation=explanation,
        takeaway=takeaway,
        note_text=note_text,
    )
    compact_concept_mode = _infer_compact_concept_mode(
        spec=spec,
        layout=layout,
        dense_math_mode=dense_math_mode,
        formulas=formulas,
        bullets=bullets,
        explanation=explanation,
        takeaway=takeaway,
        note_text=note_text,
    )
    priority_options = _resolve_priority_options(
        spec=spec,
        layout=layout,
        dense_math_mode=dense_math_mode,
        compact_concept_mode=compact_concept_mode,
        formulas=formulas,
    )

    formulas_text = _format_formulas(
        formulas,
        stack_formulas=priority_options["stack_formulas"],
        stacked_separator=str(layout.get("stacked_formula_separator", "\n")),
        inline_separator=str(layout.get("formula_separator", "   •   ")),
    )

    required_bullets = bool(spec.get("required_bullets", False))
    required_formulas = bool(spec.get("required_formulas", False)) or dense_math_mode
    required_note = bool(spec.get("required_note", False))
    required_takeaway = bool(spec.get("required_takeaway", True))

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
                header_result.content_top_y
                + float(layout.get("content_to_poster_gap", 0.12)),
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

    chosen_variant, poster_layout = _choose_best_poster_layout(
        outer_box=outer_box,
        explanation=explanation,
        bullets_text=bullets_text,
        formulas_text=formulas_text,
        note_text=note_text,
        takeaway_text=takeaway,
        layout=layout,
        required_bullets=required_bullets,
        required_formulas=required_formulas,
        required_note=required_note,
        required_takeaway=required_takeaway,
        prioritize_text_over_visual=priority_options["prioritize_text_over_visual"],
        dense_math_mode=priority_options["dense_math_mode"],
        compact_concept_mode=priority_options["compact_concept_mode"],
        visual_min_share=priority_options["visual_min_share"],
        visual_max_share=priority_options["visual_max_share"],
        preferred_visual_share=priority_options["preferred_visual_share"],
        layout_mode=priority_options["layout_mode"],
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
            text=chosen_variant["explanation"],
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
            text=chosen_variant["bullets"],
            font_name=BODY_FONT,
            font_size=max(
                int(layout.get("bullets_min_font", 13)),
                fits["bullets"].font_size,
            ),
            color=poster_style["bullets_color"],
            bold=bool(layout.get("bullets_bold", False)),
            align=layout.get("bullets_align", PP_ALIGN.CENTER),
        )

    formula_align_default = PP_ALIGN.LEFT if priority_options["stack_formulas"] else PP_ALIGN.CENTER
    if "formulas" in boxes and "formulas" in fits:
        _add_fitted_text(
            slide,
            box=boxes["formulas"],
            text=chosen_variant["formulas"],
            font_name=FORMULA_FONT,
            font_size=max(
                int(layout.get("formulas_min_font", 12)),
                fits["formulas"].font_size,
            ),
            color=poster_style["formulas_color"],
            bold=False,
            align=layout.get("formulas_align", formula_align_default),
        )

    if "note" in boxes and "note" in fits:
        _add_fitted_text(
            slide,
            box=boxes["note"],
            text=chosen_variant["note"],
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
            text=chosen_variant["takeaway"],
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

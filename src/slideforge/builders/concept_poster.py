from __future__ import annotations

from typing import Any, Mapping

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, FORMULA_FONT, OFFWHITE
from slideforge.config.themes import get_theme, resolve_color
from slideforge.io.backgrounds import choose_background
from slideforge.layout.autofit import Box, layout_concept_poster
from slideforge.render.header import render_header_from_spec
from slideforge.render.primitives import add_footer, add_rounded_box, add_textbox

INLINE_SEP = "   •   "


def _text(value: Any) -> str:
    return str(value or "").strip()


def _bool(value: Any, default: bool = False) -> bool:
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


def _clean_items(items: list[Any] | tuple[Any, ...] | None) -> list[str]:
    return [_text(item) for item in (items or []) if _text(item)]


def _join(items: list[Any] | tuple[Any, ...] | None, separator: str = INLINE_SEP) -> str:
    return separator.join(_clean_items(items))


def _box(raw: Mapping[str, Any], fallback: Box) -> Box:
    return Box(
        float(raw.get("x", fallback.x)),
        float(raw.get("y", fallback.y)),
        float(raw.get("w", fallback.w)),
        float(raw.get("h", fallback.h)),
    )


def _style(spec: Mapping[str, Any], theme) -> dict[str, Any]:
    raw = dict(spec.get("poster_style", {}) or {})
    fill_default = theme.box_fill_color or theme.panel_fill_color or OFFWHITE
    return {
        "poster_fill_color": resolve_color(raw.get("poster_fill_color"), fill_default),
        "poster_line_color": resolve_color(raw.get("poster_line_color"), theme.box_line_color),
        "poster_line_width_pt": float(raw.get("poster_line_width_pt", 1.25)),
        "visual_variant": str(raw.get("visual_variant", theme.panel_visual_variant)),
        "explanation_color": resolve_color(raw.get("explanation_color"), theme.subtitle_color),
        "bullets_color": resolve_color(raw.get("bullets_color"), theme.subtitle_color),
        "formulas_color": resolve_color(raw.get("formulas_color"), theme.body_color),
        "note_color": resolve_color(raw.get("note_color"), theme.subtitle_color),
        "takeaway_color": resolve_color(raw.get("takeaway_color"), theme.subtitle_color),
        "footer_color": resolve_color(raw.get("footer_color"), theme.footer_color),
        "footer_dark": bool(raw.get("footer_dark", theme.footer_dark)),
        "show_anchor_text": bool(raw.get("show_anchor_text", False)),
    }


def _legacy_dense(formulas: list[str], bullets: list[str], explanation: str, takeaway: str, note: str, required: bool) -> bool:
    formula_count = len(_clean_items(formulas))
    bullet_count = len(_clean_items(bullets))
    char_load = sum(len(item) for item in formulas) + len(explanation) + len(note) + len(takeaway)
    return formula_count >= 2 or (formula_count >= 1 and bullet_count >= 3) or char_load >= 300 or required


def _legacy_compact(formulas: list[str], bullets: list[str], explanation: str, takeaway: str, note: str, mini_visual: str) -> bool:
    char_load = len(explanation) + len(takeaway) + len(note) + sum(len(x) for x in formulas) + sum(len(x) for x in bullets)
    return bool(mini_visual) and char_load <= 240 and len(_clean_items(bullets)) <= 2 and len(_clean_items(formulas)) <= 2


def _profile(spec: Mapping[str, Any], layout: Mapping[str, Any], *, formulas: list[str], bullets: list[str], explanation: str, takeaway: str, note: str, mini_visual: str) -> dict[str, Any]:
    profile = _text(
        layout.get("poster_profile")
        or spec.get("poster_profile")
        or layout.get("layout_profile")
        or spec.get("layout_profile")
    ).lower()
    explicit_dense = layout.get("dense_math_mode", spec.get("dense_math_mode"))
    explicit_compact = layout.get("compact_concept_mode", spec.get("compact_concept_mode"))
    explicit_text = layout.get("prioritize_text_over_visual", spec.get("prioritize_text_over_visual"))
    prioritize_text = _bool(explicit_text) if explicit_text is not None else False
    required_formulas = _bool(spec.get("required_formulas"), False)

    if profile in {"text_first", "worked_math", "dense_math"}:
        dense, compact, mode = True, False, "worked_math"
        if profile == "text_first":
            prioritize_text = True
    elif profile in {"compact", "compact_concept", "concept_compact"}:
        dense, compact, mode = False, True, "compact_concept"
    elif profile in {"concept", "default", "visual_dominant"}:
        dense, compact, mode = False, False, "concept"
    else:
        dense = _bool(explicit_dense) if explicit_dense is not None else _legacy_dense(
            formulas, bullets, explanation, takeaway, note, required_formulas
        )
        compact = _bool(explicit_compact) if explicit_compact is not None else (not dense and _legacy_compact(
            formulas, bullets, explanation, takeaway, note, mini_visual
        ))
        mode = "worked_math" if (prioritize_text or dense) else ("compact_concept" if compact else "concept")
        profile = "text_first" if prioritize_text else ("dense_math" if dense else ("compact_concept" if compact else "concept"))

    explicit_stack = layout.get("stack_formulas", spec.get("stack_formulas"))
    stack = _bool(explicit_stack) if explicit_stack is not None else prioritize_text or dense or len(_clean_items(formulas)) > 1

    if prioritize_text:
        shares = (
            float(layout.get("text_priority_visual_min_share", 0.40)),
            float(layout.get("text_priority_visual_max_share", 0.60)),
            float(layout.get("text_priority_preferred_visual_share", 0.48)),
        )
    elif dense:
        shares = (
            float(layout.get("dense_math_visual_min_share", 0.44)),
            float(layout.get("dense_math_visual_max_share", 0.66)),
            float(layout.get("dense_math_preferred_visual_share", 0.54)),
        )
    elif compact:
        shares = (
            float(layout.get("compact_visual_min_share", 0.66)),
            float(layout.get("compact_visual_max_share", 0.84)),
            float(layout.get("compact_preferred_visual_share", 0.74)),
        )
    else:
        shares = (
            float(layout.get("visual_min_share", 0.60)),
            float(layout.get("visual_max_share", 0.82)),
            float(layout.get("preferred_visual_share", 0.70)),
        )

    return {
        "name": profile or mode,
        "dense_math_mode": dense,
        "compact_concept_mode": compact,
        "prioritize_text_over_visual": prioritize_text,
        "stack_formulas": stack,
        "layout_mode": mode,
        "visual_min_share": shares[0],
        "visual_max_share": shares[1],
        "preferred_visual_share": shares[2],
    }


def _content(spec: Mapping[str, Any], style: Mapping[str, Any], profile: Mapping[str, Any], layout: Mapping[str, Any]) -> dict[str, str]:
    formulas = list(spec.get("formulas", []) or [])
    visible_anchor = _text(spec.get("visible_anchor_text"))
    anchor = _text(spec.get("concrete_example_anchor"))
    note = visible_anchor or (anchor if _bool(spec.get("show_anchor_text", style["show_anchor_text"])) else "")
    formula_sep = str(layout.get("formula_separator", INLINE_SEP))
    formulas_text = "\n".join(_clean_items(formulas)) if profile["stack_formulas"] else _join(formulas, formula_sep)
    return {
        "explanation": _text(spec.get("text_explanation") or spec.get("explanation")),
        "bullets": _join(spec.get("bullets", [])),
        "formulas": formulas_text,
        "note": note,
        "takeaway": _text(spec.get("takeaway")),
    }


def _variants(base: Mapping[str, str], *, required_bullets: bool, required_formulas: bool, required_note: bool, required_takeaway: bool) -> list[dict[str, str]]:
    opts = {
        "bullets": [base["bullets"]] if required_bullets or not base["bullets"] else [base["bullets"], ""],
        "formulas": [base["formulas"]] if required_formulas or not base["formulas"] else [base["formulas"], ""],
        "note": [base["note"]] if required_note or not base["note"] else [base["note"], ""],
        "takeaway": [base["takeaway"]] if required_takeaway or not base["takeaway"] else [base["takeaway"], ""],
    }
    out, seen = [], set()
    for bullets in opts["bullets"]:
        for formulas in opts["formulas"]:
            for note in opts["note"]:
                for takeaway in opts["takeaway"]:
                    variant = {
                        "explanation": base["explanation"],
                        "bullets": bullets,
                        "formulas": formulas,
                        "note": note,
                        "takeaway": takeaway,
                    }
                    key = tuple(variant[k] for k in ("explanation", "bullets", "formulas", "note", "takeaway"))
                    if key not in seen:
                        seen.add(key)
                        out.append(variant)
    out.sort(key=lambda v: (1 if v["takeaway"] else 0, 1 if v["formulas"] else 0, 1 if v["bullets"] else 0, 1 if v["note"] else 0), reverse=True)
    return out


def _layout_for_variant(outer_box: Box, variant: Mapping[str, str], profile: Mapping[str, Any], layout: Mapping[str, Any]):
    return layout_concept_poster(
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
        visual_min_share=profile["visual_min_share"],
        visual_max_share=profile["visual_max_share"],
        preferred_visual_share=profile["preferred_visual_share"],
        layout_mode=profile["layout_mode"],
        dense_math_mode=profile["dense_math_mode"],
        prioritize_text_over_visual=profile["prioritize_text_over_visual"],
        reserve_formula_first=profile["prioritize_text_over_visual"] or profile["dense_math_mode"],
        compact_concept_mode=profile["compact_concept_mode"],
    )


def _variant_stats(variant: Mapping[str, str]) -> tuple[int, int]:
    kept = sum(1 for k in ("bullets", "formulas", "note", "takeaway") if variant[k])
    chars = sum(len(variant[k]) for k in ("explanation", "bullets", "formulas", "note", "takeaway"))
    return kept, chars


def _score(variant: Mapping[str, str], poster_layout: Any, profile: Mapping[str, Any]) -> float:
    kept, chars = _variant_stats(variant)
    fits = sum(1 for fit in poster_layout.text_fits.values() if getattr(fit, "fits", False))
    bad = sum(1 for fit in poster_layout.text_fits.values() if getattr(fit, "fits", True) is False)
    text_share = max(0.0, 1.0 - poster_layout.visual_share)
    visual_distance = abs(poster_layout.visual_share - profile["preferred_visual_share"])
    if profile["prioritize_text_over_visual"]:
        return kept * 18 + fits * 6 + text_share * 100 + min(chars, 600) * 0.02 - poster_layout.visual_share * 18 - bad * 20
    if profile["dense_math_mode"]:
        return kept * 12 + fits * 4 + text_share * 55 + min(chars, 600) * 0.012 + poster_layout.visual_share * 18 - bad * 14
    if profile["compact_concept_mode"]:
        return poster_layout.visual_share * 115 + fits * 5 + kept * 5 - visual_distance * 45 - bad * 16
    return poster_layout.visual_share * 100 + kept * 3 + fits * 2 - visual_distance * 24 - bad * 12


def _good_enough(variant: Mapping[str, str], poster_layout: Any, profile: Mapping[str, Any]) -> bool:
    kept, _ = _variant_stats(variant)
    fits = sum(1 for fit in poster_layout.text_fits.values() if getattr(fit, "fits", False))
    if profile["prioritize_text_over_visual"]:
        return kept == 4 and poster_layout.visual_share <= profile["preferred_visual_share"]
    if profile["dense_math_mode"]:
        return (kept == 4 and poster_layout.visual_share <= profile["preferred_visual_share"]) or (
            poster_layout.visual_share >= profile["preferred_visual_share"] and fits >= max(1, kept - 1)
        )
    if profile["compact_concept_mode"]:
        return fits >= max(1, kept) and abs(poster_layout.visual_share - profile["preferred_visual_share"]) <= 0.05
    return poster_layout.visual_share >= profile["preferred_visual_share"] and fits >= max(1, kept - 1)


def _pick_variant(outer_box: Box, base: Mapping[str, str], profile: Mapping[str, Any], layout: Mapping[str, Any], *, required_bullets: bool, required_formulas: bool, required_note: bool, required_takeaway: bool) -> tuple[dict[str, str], Any]:
    best_variant, best_layout, best_score = dict(base), None, float("-inf")
    for variant in _variants(base, required_bullets=required_bullets, required_formulas=required_formulas, required_note=required_note, required_takeaway=required_takeaway):
        poster_layout = _layout_for_variant(outer_box, variant, profile, layout)
        if _good_enough(variant, poster_layout, profile):
            return variant, poster_layout
        score = _score(variant, poster_layout, profile)
        if score > best_score:
            best_variant, best_layout, best_score = variant, poster_layout, score
    return best_variant, best_layout or _layout_for_variant(outer_box, base, profile, layout)


def _draw_text(slide, box: Box, text: str, *, font_name: str, font_size: int, color, bold: bool = False, align=PP_ALIGN.CENTER) -> None:
    if text.strip() and box.w > 0 and box.h > 0:
        add_textbox(slide, x=box.x, y=box.y, w=box.w, h=box.h, text=text, font_name=font_name, font_size=font_size, color=color, bold=bold, align=align)


def _render_blocks(slide, variant: Mapping[str, str], poster_layout: Any, profile: Mapping[str, Any], layout: Mapping[str, Any], style: Mapping[str, Any]) -> None:
    text_specs = [
        ("explanation", BODY_FONT, "explanation_min_font", 15, style["explanation_color"], False, layout.get("explanation_align", PP_ALIGN.CENTER)),
        ("bullets", BODY_FONT, "bullets_min_font", 13, style["bullets_color"], _bool(layout.get("bullets_bold", False)), layout.get("bullets_align", PP_ALIGN.CENTER)),
        ("formulas", FORMULA_FONT, "formulas_min_font", 12, style["formulas_color"], False, layout.get("formulas_align", PP_ALIGN.LEFT if profile["stack_formulas"] else PP_ALIGN.CENTER)),
        ("note", BODY_FONT, "note_min_font", 12, style["note_color"], _bool(layout.get("note_bold", False)), layout.get("note_align", PP_ALIGN.CENTER)),
        ("takeaway", BODY_FONT, "takeaway_min_font", 12, style["takeaway_color"], True, layout.get("takeaway_align", PP_ALIGN.CENTER)),
    ]
    for key, font_name, min_key, default_min, color, bold, align in text_specs:
        if key in poster_layout.text_boxes and key in poster_layout.text_fits and variant[key]:
            _draw_text(
                slide,
                poster_layout.text_boxes[key],
                variant[key],
                font_name=font_name,
                font_size=max(int(layout.get(min_key, default_min)), poster_layout.text_fits[key].font_size),
                color=color,
                bold=bold,
                align=align,
            )


def build_concept_poster_slide(prs: Presentation, spec: dict[str, Any], counters: dict[str, int]) -> None:
    theme = get_theme(slide_theme_name=spec.get("theme", "concept"))
    style = _style(spec, theme)
    layout = dict(spec.get("layout", {}) or {})
    mini_visual = _text(spec.get("mini_visual"))
    formulas = list(spec.get("formulas", []) or [])
    bullets = list(spec.get("bullets", []) or [])
    explanation = _text(spec.get("text_explanation") or spec.get("explanation"))
    takeaway = _text(spec.get("takeaway"))
    tmp_note = _text(spec.get("visible_anchor_text")) or (_text(spec.get("concrete_example_anchor")) if _bool(spec.get("show_anchor_text", style["show_anchor_text"])) else "")
    profile = _profile(spec, layout, formulas=formulas, bullets=bullets, explanation=explanation, takeaway=takeaway, note=tmp_note, mini_visual=mini_visual)
    base = _content(spec, style, profile, layout)

    slide = new_slide(prs, spec.get("background") or choose_background(spec.get("theme", "concept"), counters))
    header = render_header_from_spec(slide, spec, theme=theme)
    fallback_outer = Box(
        float(layout.get("poster_x", 0.96)),
        float(layout.get("poster_y", header.content_top_y + float(layout.get("content_to_poster_gap", 0.12)))),
        float(layout.get("poster_w", 11.10)),
        float(layout.get("poster_h", 4.98)),
    )
    outer_box = _box(layout["poster_box"], fallback_outer) if isinstance(layout.get("poster_box"), Mapping) else fallback_outer

    add_rounded_box(slide, outer_box.x, outer_box.y, outer_box.w, outer_box.h, line_color=style["poster_line_color"], fill_color=style["poster_fill_color"], line_width_pt=style["poster_line_width_pt"])
    variant, poster_layout = _pick_variant(
        outer_box,
        base,
        profile,
        layout,
        required_bullets=_bool(spec.get("required_bullets", False)),
        required_formulas=_bool(spec.get("required_formulas", False)) or profile["dense_math_mode"],
        required_note=_bool(spec.get("required_note", False)),
        required_takeaway=_bool(spec.get("required_takeaway", True)),
    )

    visual_box = _box(layout["visual_box"], poster_layout.visual_box) if isinstance(layout.get("visual_box"), Mapping) else poster_layout.visual_box
    if mini_visual:
        add_mini_visual(slide, kind=mini_visual, x=visual_box.x, y=visual_box.y, w=visual_box.w, h=visual_box.h, suffix="_concept_poster", variant=style["visual_variant"])

    _render_blocks(slide, variant, poster_layout, profile, layout, style)
    add_footer(slide, dark=style["footer_dark"], color=style["footer_color"])

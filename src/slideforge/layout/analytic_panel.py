from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Iterable

from slideforge.assets.mini_visuals import resolve_visual_kind
from slideforge.layout.base import Box
from slideforge.layout.text_fit import TextFit
from slideforge.layout.worked_example import (
    WorkedExampleLayoutResult,
    layout_worked_example_top_visual,
    layout_worked_example_two_column,
)


@dataclass(frozen=True)
class AnalyticPanelLayoutResult:
    outer_box: Box
    diagram_box: Box
    steps_box: Box
    result_box: Box
    takeaway_box: Box
    explanation_box: Box
    text_fits: dict[str, TextFit]
    mode: str
    diagram_share: float
    candidate_name: str
    score: float
    split_required: bool
    overflow_sections: tuple[str, ...]
    notes: tuple[str, ...] = ()
    all_candidates_failed: bool = False


TEXT_HARD_RATIO = 0.88
TEXT_WARN_RATIO = 0.82
TEXT_SAFE_RATIO = 0.78
MIN_RESULT_BOX_H = 0.62
MIN_TAKEAWAY_BOX_H = 0.40
HARD_SPLIT_SCORE = 46.0

LABEL_MIN_PT = {
    "low": 10.0,
    "medium": 11.0,
    "high": 12.0,
}

_VISUAL_METADATA: dict[str, dict[str, Any]] = {
    "point_vector_projection_hero": {
        "preferred_layout": "hero",
        "min_width_in": 7.2,
        "min_height_in": 2.25,
        "preferred_aspect_ratio": 3.2,
        "label_density": "low",
        "text_bearing": False,
        "allow_top_strip": True,
    },
    "point_and_vector_same_coords": {
        "preferred_layout": "two_column",
        "min_width_in": 4.7,
        "min_height_in": 2.0,
        "preferred_aspect_ratio": 2.3,
        "label_density": "medium",
        "text_bearing": False,
        "allow_top_strip": False,
    },
    "vector_difference_geometry": {
        "preferred_layout": "two_column",
        "min_width_in": 4.8,
        "min_height_in": 2.0,
        "preferred_aspect_ratio": 2.5,
        "label_density": "medium",
        "text_bearing": False,
        "allow_top_strip": False,
    },
    "displacement_geometry": {
        "preferred_layout": "two_column",
        "min_width_in": 4.6,
        "min_height_in": 2.0,
        "preferred_aspect_ratio": 2.4,
        "label_density": "medium",
        "text_bearing": False,
        "allow_top_strip": False,
    },
    "norm_worked_geometry": {
        "preferred_layout": "two_column",
        "min_width_in": 3.4,
        "min_height_in": 2.25,
        "preferred_aspect_ratio": 0.88,
        "label_density": "medium",
        "text_bearing": False,
        "allow_top_strip": False,
    },
    "dot_product_worked_geometry": {
        "preferred_layout": "two_column",
        "min_width_in": 3.85,
        "min_height_in": 2.35,
        "preferred_aspect_ratio": 1.0,
        "label_density": "high",
        "text_bearing": False,
        "allow_top_strip": False,
    },
    "angle_homework_geometry": {
        "preferred_layout": "two_column",
        "min_width_in": 4.35,
        "min_height_in": 2.05,
        "preferred_aspect_ratio": 2.1,
        "label_density": "medium",
        "text_bearing": False,
        "allow_top_strip": False,
    },
    "angle_recovery_geometry": {
        "preferred_layout": "two_column",
        "min_width_in": 4.0,
        "min_height_in": 2.0,
        "preferred_aspect_ratio": 1.9,
        "label_density": "medium",
        "text_bearing": False,
        "allow_top_strip": False,
    },
    "orthogonal_vectors_geometry": {
        "preferred_layout": "two_column",
        "min_width_in": 3.8,
        "min_height_in": 2.1,
        "preferred_aspect_ratio": 1.0,
        "label_density": "medium",
        "text_bearing": False,
        "allow_top_strip": False,
    },
    "projection_homework_geometry": {
        "preferred_layout": "two_column",
        "min_width_in": 3.8,
        "min_height_in": 2.15,
        "preferred_aspect_ratio": 0.92,
        "label_density": "low",
        "text_bearing": False,
        "allow_top_strip": False,
    },
}

_ALLOWED_TWO_COLUMN_KEYS = {
    "top_pad",
    "bottom_pad",
    "side_pad",
    "col_gap",
    "gap",
    "diagram_min_share",
    "diagram_max_share",
    "diagram_preferred_share",
    "min_steps_h",
    "explanation_min_h",
    "explanation_max_h",
    "result_min_h",
    "result_max_h",
    "takeaway_min_h",
    "takeaway_max_h",
    "min_diagram_h_share",
    "steps_min_font",
    "steps_max_font",
    "result_min_font",
    "result_max_font",
}

_ALLOWED_TOP_VISUAL_KEYS = {
    "top_pad",
    "bottom_pad",
    "side_pad",
    "gap",
    "diagram_min_share",
    "diagram_max_share",
    "diagram_preferred_share",
    "min_steps_h",
    "explanation_min_h",
    "explanation_max_h",
    "result_min_h",
    "result_max_h",
    "takeaway_min_h",
    "takeaway_max_h",
    "steps_min_font",
    "steps_max_font",
    "result_min_font",
    "result_max_font",
}


def _metadata(kind: str | None) -> dict[str, Any]:
    key = resolve_visual_kind(str(kind or "").strip()) if kind else ""
    return dict(_VISUAL_METADATA.get(key, {}))


def _density_score(*, explanation_text: str, steps_text: str, result_text: str, takeaway_text: str) -> float:
    score = 0.0
    score += steps_text.count("Step ") * 1.9
    score += len(steps_text) / 240.0
    score += max(1, len([ln for ln in result_text.splitlines() if ln.strip()])) * 0.8 if result_text.strip() else 0.0
    score += 0.8 if explanation_text.strip() else 0.0
    score += 0.6 if takeaway_text.strip() else 0.0
    score += len(result_text) / 180.0
    return score


def _safe_kwargs(kwargs: dict[str, Any], allowed: Iterable[str]) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if k in allowed and v is not None}


def _build_two_column_candidate(
    outer_box: Box,
    *,
    explanation_text: str,
    steps_text: str,
    result_text: str,
    takeaway_text: str,
    share_triplet: tuple[float, float, float],
    kwargs: dict[str, Any],
) -> WorkedExampleLayoutResult:
    settings = _safe_kwargs(kwargs, _ALLOWED_TWO_COLUMN_KEYS)
    settings.update(
        {
            "diagram_min_share": share_triplet[0],
            "diagram_preferred_share": share_triplet[1],
            "diagram_max_share": share_triplet[2],
        }
    )
    return layout_worked_example_two_column(
        outer_box,
        explanation_text=explanation_text,
        steps_text=steps_text,
        result_text=result_text,
        takeaway_text=takeaway_text,
        **settings,
    )


def _build_top_visual_candidate(
    outer_box: Box,
    *,
    explanation_text: str,
    steps_text: str,
    result_text: str,
    takeaway_text: str,
    share_triplet: tuple[float, float, float],
    kwargs: dict[str, Any],
) -> WorkedExampleLayoutResult:
    settings = _safe_kwargs(kwargs, _ALLOWED_TOP_VISUAL_KEYS)
    settings.update(
        {
            "diagram_min_share": share_triplet[0],
            "diagram_preferred_share": share_triplet[1],
            "diagram_max_share": share_triplet[2],
        }
    )
    return layout_worked_example_top_visual(
        outer_box,
        explanation_text=explanation_text,
        steps_text=steps_text,
        result_text=result_text,
        takeaway_text=takeaway_text,
        **settings,
    )


def _underfill_penalty(layout: WorkedExampleLayoutResult) -> float:
    occupied = 0.0
    for box in [layout.diagram_box, layout.explanation_box, layout.steps_box, layout.result_box, layout.takeaway_box]:
        occupied += max(0.0, box.w * box.h)
    outer = max(0.01, layout.outer_box.w * layout.outer_box.h)
    fill = occupied / outer
    return max(0.0, 0.58 - fill) * 26.0


def _estimate_label_pt(box: Box, *, density: str, text_bearing: bool) -> float:
    w_factor = {"low": 2.6, "medium": 2.15, "high": 1.8}.get(density, 2.0)
    h_factor = {"low": 5.6, "medium": 4.8, "high": 4.1}.get(density, 4.5)
    est = min(box.w * w_factor, box.h * h_factor)
    if text_bearing:
        est -= 1.0
    return est


def _text_penalty(layout: WorkedExampleLayoutResult) -> tuple[float, list[str], list[str]]:
    penalty = 0.0
    notes: list[str] = []
    hard: list[str] = []
    region = {
        "explanation": layout.explanation_box,
        "steps": layout.steps_box,
        "result": layout.result_box,
        "takeaway": layout.takeaway_box,
    }
    for name, fit in layout.text_fits.items():
        box = region.get(name)
        if box is None or box.h <= 0:
            continue
        ratio = fit.estimated_height / max(box.h, 1e-6)
        if not fit.fits or ratio > TEXT_HARD_RATIO:
            penalty += 420.0
            notes.append(f"hard_text_overflow:{name}")
            hard.append(name)
            continue
        if ratio > TEXT_WARN_RATIO:
            penalty += 160.0 + (ratio - TEXT_WARN_RATIO) * 180.0
            notes.append(f"bottom_risk:{name}")
        elif ratio > TEXT_SAFE_RATIO:
            penalty += (ratio - TEXT_SAFE_RATIO) * 70.0

    if layout.result_box.h > 0 and layout.result_box.h < MIN_RESULT_BOX_H:
        penalty += 120.0
        notes.append("hard_result_box_tight")
        hard.append("result_box")
    elif layout.result_box.h > 0 and layout.result_box.h < MIN_RESULT_BOX_H + 0.12:
        penalty += 30.0
        notes.append("result_box_tight")

    if layout.takeaway_box.h > 0 and layout.takeaway_box.h < MIN_TAKEAWAY_BOX_H:
        penalty += 90.0
        notes.append("hard_takeaway_box_tight")
        hard.append("takeaway_box")
    elif layout.takeaway_box.h > 0 and layout.takeaway_box.h < MIN_TAKEAWAY_BOX_H + 0.10:
        penalty += 18.0
        notes.append("takeaway_box_tight")

    return penalty, notes, hard


def _geometry_penalty(layout: WorkedExampleLayoutResult, *, metadata: dict[str, Any], candidate_mode: str) -> tuple[float, list[str], list[str]]:
    penalty = 0.0
    notes: list[str] = []
    hard: list[str] = []
    box = layout.diagram_box
    min_w = float(metadata.get("min_width_in", 0.0) or 0.0)
    min_h = float(metadata.get("min_height_in", 0.0) or 0.0)
    pref_ratio = float(metadata.get("preferred_aspect_ratio", 0.0) or 0.0)
    preferred_layout = str(metadata.get("preferred_layout", "either") or "either").strip().lower()
    allow_top_strip = bool(metadata.get("allow_top_strip", True))
    label_density = str(metadata.get("label_density", "medium") or "medium").strip().lower()
    text_bearing = bool(metadata.get("text_bearing", False))

    if min_w and box.w < min_w:
        penalty += 360.0 + (min_w - box.w) * 90.0
        notes.append("hard_diagram_too_narrow")
        hard.append("diagram_width")
    elif min_w and box.w < min_w * 1.08:
        penalty += 80.0 + (min_w * 1.08 - box.w) * 40.0
        notes.append("diagram_near_min_width")

    if min_h and box.h < min_h:
        penalty += 360.0 + (min_h - box.h) * 95.0
        notes.append("hard_diagram_too_short")
        hard.append("diagram_height")
    elif min_h and box.h < min_h * 1.08:
        penalty += 80.0 + (min_h * 1.08 - box.h) * 40.0
        notes.append("diagram_near_min_height")

    if pref_ratio and box.h > 0:
        actual = box.w / max(box.h, 1e-6)
        delta = abs(actual - pref_ratio)
        penalty += delta * 12.0
        if delta > 1.1:
            penalty += 110.0
            notes.append("hard_diagram_aspect_far_from_preference")
            hard.append("diagram_aspect")
        elif delta > 0.7:
            notes.append("diagram_aspect_far_from_preference")

    if candidate_mode == "top_visual" and not allow_top_strip:
        penalty += 500.0
        notes.append("hard_top_strip_forbidden")
        hard.append("top_strip")

    if preferred_layout == "two_column" and candidate_mode == "top_visual":
        penalty += 36.0
    elif preferred_layout in {"hero", "top_visual"} and candidate_mode == "two_column":
        penalty += 14.0

    if label_density in LABEL_MIN_PT:
        est_pt = _estimate_label_pt(box, density=label_density, text_bearing=text_bearing)
        min_pt = LABEL_MIN_PT[label_density]
        if est_pt < min_pt:
            penalty += 320.0 + (min_pt - est_pt) * 42.0
            notes.append("hard_visual_labels_too_small")
            hard.append("visual_labels")
        elif est_pt < min_pt + 1.5:
            penalty += 55.0
            notes.append("visual_labels_near_min")

    if label_density == "high" and candidate_mode == "top_visual":
        penalty += 40.0
    elif label_density == "medium" and candidate_mode == "top_visual":
        penalty += 18.0

    return penalty, notes, hard


def _candidate_definitions(*, requested_mode: str, density: float, metadata: dict[str, Any], explanation_text: str, result_text: str, takeaway_text: str) -> list[tuple[str, str, tuple[float, float, float]]]:
    allow_top = bool(metadata.get("allow_top_strip", True))
    preferred_layout = str(metadata.get("preferred_layout", "either") or "either").strip().lower()
    candidates: list[tuple[str, str, tuple[float, float, float]]] = []
    derivation_only = (not explanation_text.strip()) and bool(result_text.strip()) and (not takeaway_text.strip())
    squareish_visual = float(metadata.get("preferred_aspect_ratio", 0.0) or 0.0) <= 1.15 and float(metadata.get("preferred_aspect_ratio", 0.0) or 0.0) > 0

    if requested_mode == "top_visual" and allow_top:
        candidates.append(("top_visual_requested", "top_visual", (0.24, 0.31, 0.40)))
    elif requested_mode == "two_column":
        candidates.append(("two_column_requested", "two_column", (0.23, 0.30, 0.39)))

    if preferred_layout in {"hero", "top_visual"} and allow_top:
        candidates.append(("top_visual_hero", "top_visual", (0.28, 0.35, 0.45)))

    if derivation_only and squareish_visual:
        candidates.append(("two_column_square_visual", "two_column", (0.28, 0.36, 0.44)))
        candidates.append(("two_column_square_visual_relaxed", "two_column", (0.30, 0.39, 0.47)))

    if density >= 7.5:
        candidates.append(("two_column_text_heavy", "two_column", (0.20, 0.24, 0.30)))
        candidates.append(("two_column", "two_column", (0.22, 0.27, 0.34)))
        if allow_top:
            candidates.append(("top_visual", "top_visual", (0.20, 0.27, 0.36)))
    else:
        candidates.append(("two_column", "two_column", (0.23, 0.29, 0.36)))
        candidates.append(("two_column_visual_heavy", "two_column", (0.27, 0.34, 0.41)))
        if allow_top:
            candidates.append(("top_visual", "top_visual", (0.22, 0.29, 0.38)))

    deduped: list[tuple[str, str, tuple[float, float, float]]] = []
    seen: set[str] = set()
    for item in candidates:
        if item[0] in seen:
            continue
        seen.add(item[0])
        deduped.append(item)
    return deduped or [("two_column", "two_column", (0.22, 0.28, 0.36))]


def _candidate_score(base: WorkedExampleLayoutResult, *, metadata: dict[str, Any], candidate_name: str, density: float, derivation_only: bool = False) -> tuple[float, tuple[str, ...], tuple[str, ...]]:
    notes: list[str] = []
    hard: list[str] = []
    penalty = 0.0
    text_penalty, text_notes, text_hard = _text_penalty(base)
    geom_penalty, geom_notes, geom_hard = _geometry_penalty(
        base,
        metadata=metadata,
        candidate_mode="top_visual" if candidate_name.startswith("top_visual") else "two_column",
    )
    penalty += text_penalty + geom_penalty + _underfill_penalty(base)
    notes.extend(text_notes)
    notes.extend(geom_notes)
    hard.extend(text_hard)
    hard.extend(geom_hard)

    if candidate_name == "two_column_text_heavy":
        penalty += abs(base.diagram_share - 0.24) * 25.0
    elif candidate_name == "two_column_visual_heavy":
        penalty += abs(base.diagram_share - 0.33) * 18.0
    elif candidate_name == "two_column_square_visual":
        penalty += abs(base.diagram_share - 0.36) * 14.0
    elif candidate_name == "two_column_square_visual_relaxed":
        penalty += abs(base.diagram_share - 0.39) * 12.0
    elif candidate_name.startswith("top_visual"):
        penalty += abs(base.diagram_share - 0.32) * 22.0
        if density >= 7.5:
            penalty += 18.0

    if density >= 8.5 and candidate_name == "two_column_visual_heavy":
        penalty += 12.0

    preferred_aspect = float(metadata.get("preferred_aspect_ratio", 0.0) or 0.0)
    if derivation_only and 0.0 < preferred_aspect <= 1.15 and base.diagram_share < 0.31:
        penalty += (0.31 - base.diagram_share) * 220.0
        notes.append("diagram_share_too_small_for_square_derivation_visual")

    return penalty, tuple(dict.fromkeys(notes)), tuple(dict.fromkeys(hard))


def _as_result(base: WorkedExampleLayoutResult, *, candidate_name: str, score: float, split_required: bool, overflow_sections: tuple[str, ...], notes: tuple[str, ...], all_candidates_failed: bool = False) -> AnalyticPanelLayoutResult:
    return AnalyticPanelLayoutResult(
        outer_box=base.outer_box,
        diagram_box=base.diagram_box,
        steps_box=base.steps_box,
        result_box=base.result_box,
        takeaway_box=base.takeaway_box,
        explanation_box=base.explanation_box,
        text_fits=base.text_fits,
        mode=base.mode,
        diagram_share=base.diagram_share,
        candidate_name=candidate_name,
        score=score,
        split_required=split_required,
        overflow_sections=overflow_sections,
        notes=notes,
        all_candidates_failed=all_candidates_failed,
    )


def layout_analytic_panel(
    outer_box: Box,
    *,
    explanation_text: str = "",
    steps_text: str = "",
    result_text: str = "",
    takeaway_text: str = "",
    layout_mode: str = "two_column",
    visual_kind: str | None = None,
    force_candidates: Iterable[str] | None = None,
    split_score_threshold: float = HARD_SPLIT_SCORE,
    **kwargs,
) -> AnalyticPanelLayoutResult:
    metadata = _metadata(visual_kind)
    density = _density_score(
        explanation_text=explanation_text,
        steps_text=steps_text,
        result_text=result_text,
        takeaway_text=takeaway_text,
    )
    requested_mode = str(layout_mode or "two_column").strip().lower()
    derivation_only = (not explanation_text.strip()) and bool(result_text.strip()) and (not takeaway_text.strip())
    if derivation_only:
        kwargs.setdefault("steps_min_font", 10)
        kwargs.setdefault("steps_max_font", 13)
        kwargs.setdefault("result_min_font", 11)
        kwargs.setdefault("result_max_font", 15)
    candidates = _candidate_definitions(requested_mode=requested_mode, density=density, metadata=metadata, explanation_text=explanation_text, result_text=result_text, takeaway_text=takeaway_text)
    if force_candidates:
        wanted = {str(name) for name in force_candidates}
        candidates = [c for c in candidates if c[0] in wanted] or candidates

    best: AnalyticPanelLayoutResult | None = None
    any_acceptable = False
    for candidate_name, family, shares in candidates:
        if family == "top_visual":
            base = _build_top_visual_candidate(
                outer_box,
                explanation_text=explanation_text,
                steps_text=steps_text,
                result_text=result_text,
                takeaway_text=takeaway_text,
                share_triplet=shares,
                kwargs=kwargs,
            )
        else:
            base = _build_two_column_candidate(
                outer_box,
                explanation_text=explanation_text,
                steps_text=steps_text,
                result_text=result_text,
                takeaway_text=takeaway_text,
                share_triplet=shares,
                kwargs=kwargs,
            )

        score, notes, hard = _candidate_score(base, metadata=metadata, candidate_name=candidate_name, density=density, derivation_only=derivation_only)
        overflow = tuple(sorted(k for k, fit in base.text_fits.items() if not fit.fits))
        split_required = bool(bool(hard) or score >= split_score_threshold or (len(overflow) >= 1 and density >= 8.0))
        if not split_required:
            any_acceptable = True
        result = _as_result(base, candidate_name=candidate_name, score=score, split_required=split_required, overflow_sections=overflow or hard, notes=notes)
        if best is None or result.score < best.score:
            best = result
    assert best is not None
    if not any_acceptable:
        notes = tuple(dict.fromkeys(best.notes + ("all_candidates_failed", "auto_split_recommended")))
        return replace(best, split_required=True, all_candidates_failed=True, notes=notes)
    return best


def layout_analytic_panel_top_visual(
    outer_box: Box,
    *,
    explanation_text: str = "",
    steps_text: str = "",
    result_text: str = "",
    takeaway_text: str = "",
    visual_kind: str | None = None,
    **kwargs,
) -> AnalyticPanelLayoutResult:
    return layout_analytic_panel(
        outer_box,
        explanation_text=explanation_text,
        steps_text=steps_text,
        result_text=result_text,
        takeaway_text=takeaway_text,
        layout_mode="top_visual",
        visual_kind=visual_kind,
        **kwargs,
    )


def layout_analytic_panel_two_column(
    outer_box: Box,
    *,
    explanation_text: str = "",
    steps_text: str = "",
    result_text: str = "",
    takeaway_text: str = "",
    visual_kind: str | None = None,
    **kwargs,
) -> AnalyticPanelLayoutResult:
    return layout_analytic_panel(
        outer_box,
        explanation_text=explanation_text,
        steps_text=steps_text,
        result_text=result_text,
        takeaway_text=takeaway_text,
        layout_mode="two_column",
        visual_kind=visual_kind,
        **kwargs,
    )


__all__ = [
    "AnalyticPanelLayoutResult",
    "layout_analytic_panel",
    "layout_analytic_panel_top_visual",
    "layout_analytic_panel_two_column",
]

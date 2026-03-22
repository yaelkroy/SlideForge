from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from slideforge.assets.mini_visuals import resolve_visual_kind
from slideforge.layout.base import Box
from slideforge.layout.text_fit import TextFit, clamp
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


# Visual metadata lives here for now so the layout solver can reason about
# geometry without requiring each drawer module to export metadata yet.
_VISUAL_METADATA: dict[str, dict[str, Any]] = {
    # Title / divider hero
    "point_vector_projection_hero": {
        "preferred_layout": "hero",
        "min_width_in": 7.2,
        "min_height_in": 2.2,
        "preferred_aspect_ratio": 3.4,
        "label_density": "low",
        "text_bearing": False,
        "allow_top_strip": True,
    },
    # Concept bridges
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
        "min_height_in": 2.05,
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
    # Analytic / worked visuals
    "norm_worked_geometry": {
        "preferred_layout": "two_column",
        "min_width_in": 3.2,
        "min_height_in": 2.2,
        "preferred_aspect_ratio": 0.85,
        "label_density": "medium",
        "text_bearing": False,
        "allow_top_strip": False,
    },
    "dot_product_worked_geometry": {
        "preferred_layout": "two_column",
        "min_width_in": 3.6,
        "min_height_in": 2.35,
        "preferred_aspect_ratio": 0.95,
        "label_density": "high",
        "text_bearing": False,
        "allow_top_strip": False,
    },
    "angle_homework_geometry": {
        "preferred_layout": "two_column",
        "min_width_in": 4.3,
        "min_height_in": 2.0,
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
        "min_width_in": 3.7,
        "min_height_in": 2.1,
        "preferred_aspect_ratio": 1.0,
        "label_density": "medium",
        "text_bearing": False,
        "allow_top_strip": False,
    },
    "projection_homework_geometry": {
        "preferred_layout": "two_column",
        "min_width_in": 3.7,
        "min_height_in": 2.15,
        "preferred_aspect_ratio": 0.9,
        "label_density": "medium",
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
    return max(0.0, 0.56 - fill) * 22.0


def _text_penalty(layout: WorkedExampleLayoutResult) -> tuple[float, list[str]]:
    penalty = 0.0
    notes: list[str] = []
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
        if not fit.fits:
            penalty += 130.0
            notes.append(f"overflow:{name}")
        if ratio > 0.90:
            penalty += (ratio - 0.90) * 260.0
            notes.append(f"bottom_risk:{name}")
        elif ratio > 0.84:
            penalty += (ratio - 0.84) * 80.0
    return penalty, notes


def _geometry_penalty(layout: WorkedExampleLayoutResult, *, metadata: dict[str, Any], candidate_mode: str) -> tuple[float, list[str]]:
    penalty = 0.0
    notes: list[str] = []
    box = layout.diagram_box
    min_w = float(metadata.get("min_width_in", 0.0) or 0.0)
    min_h = float(metadata.get("min_height_in", 0.0) or 0.0)
    pref_ratio = float(metadata.get("preferred_aspect_ratio", 0.0) or 0.0)
    preferred_layout = str(metadata.get("preferred_layout", "either") or "either").strip().lower()
    allow_top_strip = bool(metadata.get("allow_top_strip", True))
    label_density = str(metadata.get("label_density", "medium") or "medium").strip().lower()

    if min_w and box.w < min_w:
        penalty += (min_w - box.w) * 85.0
        notes.append("diagram_too_narrow")
    if min_h and box.h < min_h:
        penalty += (min_h - box.h) * 95.0
        notes.append("diagram_too_short")
    if pref_ratio and box.h > 0:
        actual = box.w / max(box.h, 1e-6)
        delta = abs(actual - pref_ratio)
        penalty += delta * 10.0
        if delta > 0.8:
            notes.append("diagram_aspect_far_from_preference")

    if candidate_mode == "top_visual" and not allow_top_strip:
        penalty += 260.0
        notes.append("top_strip_forbidden")

    if preferred_layout == "two_column" and candidate_mode == "top_visual":
        penalty += 32.0
    elif preferred_layout in {"hero", "top_visual"} and candidate_mode == "two_column":
        penalty += 14.0

    if label_density == "high" and candidate_mode == "top_visual":
        penalty += 30.0
    elif label_density == "medium" and candidate_mode == "top_visual":
        penalty += 14.0

    if layout.result_box.h > 0 and layout.result_box.h < 0.55:
        penalty += 18.0
        notes.append("result_box_tight")
    if layout.takeaway_box.h > 0 and layout.takeaway_box.h < 0.34:
        penalty += 14.0
        notes.append("takeaway_box_tight")
    return penalty, notes


def _candidate_definitions(*, requested_mode: str, density: float, metadata: dict[str, Any]) -> list[tuple[str, str, tuple[float, float, float]]]:
    allow_top = bool(metadata.get("allow_top_strip", True))
    preferred_layout = str(metadata.get("preferred_layout", "either") or "either").strip().lower()
    candidates: list[tuple[str, str, tuple[float, float, float]]] = []

    # Start with what the slide asked for, but don't trust it blindly.
    if requested_mode == "top_visual" and allow_top:
        candidates.append(("top_visual_requested", "top_visual", (0.24, 0.31, 0.40)))
    elif requested_mode == "two_column":
        candidates.append(("two_column_requested", "two_column", (0.24, 0.30, 0.38)))

    if preferred_layout in {"hero", "top_visual"} and allow_top:
        candidates.append(("top_visual_hero", "top_visual", (0.28, 0.35, 0.44)))

    if density >= 7.5:
        candidates.append(("two_column_text_heavy", "two_column", (0.20, 0.24, 0.30)))
        candidates.append(("two_column", "two_column", (0.22, 0.27, 0.34)))
        if allow_top:
            candidates.append(("top_visual", "top_visual", (0.20, 0.27, 0.36)))
    else:
        candidates.append(("two_column", "two_column", (0.23, 0.29, 0.36)))
        candidates.append(("two_column_visual_heavy", "two_column", (0.26, 0.33, 0.40)))
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


def _candidate_score(base: WorkedExampleLayoutResult, *, metadata: dict[str, Any], candidate_name: str, density: float) -> tuple[float, tuple[str, ...]]:
    notes: list[str] = []
    penalty = 0.0
    text_penalty, text_notes = _text_penalty(base)
    geom_penalty, geom_notes = _geometry_penalty(
        base,
        metadata=metadata,
        candidate_mode="top_visual" if candidate_name.startswith("top_visual") else "two_column",
    )
    penalty += text_penalty + geom_penalty + _underfill_penalty(base)
    notes.extend(text_notes)
    notes.extend(geom_notes)

    # Penalize awkward balance. Dense analytic slides usually want more text width.
    if candidate_name == "two_column_text_heavy":
        penalty += abs(base.diagram_share - 0.24) * 25.0
    elif candidate_name == "two_column_visual_heavy":
        penalty += abs(base.diagram_share - 0.33) * 16.0
    elif candidate_name.startswith("top_visual"):
        penalty += abs(base.diagram_share - 0.32) * 20.0
        if density >= 7.5:
            penalty += 16.0

    if density >= 8.5 and candidate_name == "two_column_visual_heavy":
        penalty += 12.0

    return penalty, tuple(notes)


def _as_result(base: WorkedExampleLayoutResult, *, candidate_name: str, score: float, split_required: bool, overflow_sections: tuple[str, ...], notes: tuple[str, ...]) -> AnalyticPanelLayoutResult:
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
    split_score_threshold: float = 42.0,
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
    candidates = _candidate_definitions(requested_mode=requested_mode, density=density, metadata=metadata)
    if force_candidates:
        wanted = {str(name) for name in force_candidates}
        candidates = [c for c in candidates if c[0] in wanted] or candidates

    best: AnalyticPanelLayoutResult | None = None
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

        score, notes = _candidate_score(base, metadata=metadata, candidate_name=candidate_name, density=density)
        overflow = tuple(sorted(k for k, fit in base.text_fits.items() if not fit.fits))
        split_required = bool(score >= split_score_threshold or (len(overflow) >= 2 and density >= 8.0))
        result = _as_result(base, candidate_name=candidate_name, score=score, split_required=split_required, overflow_sections=overflow, notes=notes)
        if best is None or result.score < best.score:
            best = result
    assert best is not None
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

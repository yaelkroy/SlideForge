from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from slideforge.assets.packs.geometry.heroes import VISUAL_METADATA as HERO_VISUAL_METADATA
from slideforge.assets.packs.geometry.norms_dots_angles import VISUAL_METADATA as NDA_VISUAL_METADATA
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


_DEFAULT_VISUAL_METADATA: dict[str, dict[str, Any]] = {
    # title/hero
    "point_vector_projection_hero": {
        "preferred_layout": "hero",
        "min_width_in": 7.4,
        "min_height_in": 2.15,
        "preferred_aspect_ratio": 3.7,
        "label_density": "low",
        "text_bearing": False,
        "allow_top_strip": True,
        "hero_simplify_labels": True,
    },
    # points / vectors bridge slides
    "point_and_vector_same_coords": {
        "preferred_layout": "two_column",
        "min_width_in": 4.6,
        "min_height_in": 2.15,
        "preferred_aspect_ratio": 2.5,
        "label_density": "medium",
        "text_bearing": False,
        "allow_top_strip": False,
    },
    "vector_difference_geometry": {
        "preferred_layout": "two_column",
        "min_width_in": 4.8,
        "min_height_in": 2.1,
        "preferred_aspect_ratio": 2.7,
        "label_density": "medium",
        "text_bearing": False,
        "allow_top_strip": False,
    },
    "displacement_geometry": {
        "preferred_layout": "two_column",
        "min_width_in": 4.5,
        "min_height_in": 2.0,
        "preferred_aspect_ratio": 2.4,
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


def _merged_visual_metadata(kind: str | None) -> dict[str, Any]:
    key = str(kind or "").strip()
    merged = dict(_DEFAULT_VISUAL_METADATA.get(key, {}))
    merged.update(HERO_VISUAL_METADATA.get(key, {}))
    merged.update(NDA_VISUAL_METADATA.get(key, {}))
    return merged


def _lines_count(text: str) -> int:
    return len([line for line in str(text or "").splitlines() if line.strip()])


def _density_score(
    *,
    explanation_text: str,
    steps_text: str,
    result_text: str,
    takeaway_text: str,
) -> float:
    score = 0.0
    score += steps_text.count("Step ") * 1.7
    score += max(0.0, len(steps_text) / 260.0)
    score += _lines_count(result_text) * 0.8
    score += 0.7 if takeaway_text.strip() else 0.0
    score += 0.7 if explanation_text.strip() else 0.0
    score += max(0.0, len(result_text) / 180.0)
    return score


def _underfill_penalty(layout: WorkedExampleLayoutResult) -> float:
    occupied = 0.0
    for box in [layout.diagram_box, layout.explanation_box, layout.steps_box, layout.result_box, layout.takeaway_box]:
        occupied += max(0.0, box.w * box.h)
    outer = max(0.01, layout.outer_box.w * layout.outer_box.h)
    fill_ratio = occupied / outer
    # Mild penalty only when the slide is visibly sparse.
    return max(0.0, 0.54 - fill_ratio) * 18.0


def _bottom_safety_penalty(layout: WorkedExampleLayoutResult) -> float:
    penalty = 0.0
    region_for = {
        "explanation": layout.explanation_box,
        "steps": layout.steps_box,
        "result": layout.result_box,
        "takeaway": layout.takeaway_box,
    }
    for key, fit in layout.text_fits.items():
        box = region_for.get(key)
        if box is None or box.h <= 0:
            continue
        ratio = fit.estimated_height / max(box.h, 1e-6)
        if ratio > 0.90:
            penalty += (ratio - 0.90) * 240.0
        elif ratio > 0.84:
            penalty += (ratio - 0.84) * 70.0
        if not fit.fits:
            penalty += 50.0
    return penalty


def _geometry_penalty(
    *,
    layout: WorkedExampleLayoutResult,
    metadata: dict[str, Any],
    candidate_mode: str,
) -> tuple[float, list[str]]:
    box = layout.diagram_box
    notes: list[str] = []
    penalty = 0.0

    min_w = float(metadata.get("min_width_in", 0.0) or 0.0)
    min_h = float(metadata.get("min_height_in", 0.0) or 0.0)
    pref_ratio = float(metadata.get("preferred_aspect_ratio", 0.0) or 0.0)
    density = str(metadata.get("label_density", "medium") or "medium").strip().lower()
    preferred_layout = str(metadata.get("preferred_layout", "either") or "either").strip().lower()
    allow_top_strip = bool(metadata.get("allow_top_strip", True))

    if min_w and box.w < min_w:
        penalty += (min_w - box.w) * 75.0
        notes.append("diagram_too_narrow")
    if min_h and box.h < min_h:
        penalty += (min_h - box.h) * 95.0
        notes.append("diagram_too_short")
    if pref_ratio and box.h > 0:
        actual_ratio = box.w / max(box.h, 1e-6)
        penalty += abs(actual_ratio - pref_ratio) * 9.0
        if abs(actual_ratio - pref_ratio) > 0.9:
            notes.append("diagram_aspect_far_from_preference")

    if candidate_mode == "top_visual" and not allow_top_strip:
        penalty += 240.0
        notes.append("top_strip_forbidden")

    if preferred_layout == "two_column" and candidate_mode == "top_visual":
        penalty += 28.0
    elif preferred_layout in {"hero", "top_visual"} and candidate_mode.startswith("two_column"):
        penalty += 16.0

    density_weights = {"low": 0.0, "medium": 12.0, "high": 22.0}
    if density in density_weights and candidate_mode == "top_visual":
        penalty += density_weights[density]
    if density == "high" and box.w < max(min_w, 3.6):
        penalty += 24.0
        notes.append("labels_at_risk")

    return penalty, notes


def _candidate_score(
    layout: WorkedExampleLayoutResult,
    *,
    metadata: dict[str, Any],
    candidate_name: str,
    density_score: float,
) -> tuple[float, tuple[str, ...]]:
    notes: list[str] = []
    overflow = tuple(sorted(k for k, fit in layout.text_fits.items() if not fit.fits))
    if overflow:
        notes.extend(f"overflow:{name}" for name in overflow)

    penalty = 0.0
    penalty += len(overflow) * 120.0
    penalty += _bottom_safety_penalty(layout)
    penalty += _underfill_penalty(layout)

    geom_penalty, geom_notes = _geometry_penalty(
        layout=layout,
        metadata=metadata,
        candidate_mode="top_visual" if candidate_name.startswith("top_visual") else "two_column",
    )
    penalty += geom_penalty
    notes.extend(geom_notes)

    # Penalize obviously awkward balance.
    if candidate_name == "two_column_text_heavy":
        penalty += abs(layout.diagram_share - 0.22) * 35.0
    elif candidate_name == "two_column_visual_heavy":
        penalty += abs(layout.diagram_share - 0.34) * 25.0
    elif candidate_name.startswith("top_visual"):
        penalty += abs(layout.diagram_share - 0.34) * 30.0

    # Dense content should prefer text-heavy candidates.
    if density_score >= 7.5 and candidate_name.startswith("top_visual"):
        penalty += 18.0
    if density_score >= 8.5 and candidate_name == "two_column_visual_heavy":
        penalty += 14.0

    # Very small result/takeaway regions are risky.
    if layout.result_box.h > 0 and layout.result_box.h < 0.55:
        penalty += 20.0
        notes.append("result_box_tight")
    if layout.takeaway_box.h > 0 and layout.takeaway_box.h < 0.35:
        penalty += 16.0
        notes.append("takeaway_box_tight")

    return penalty, tuple(notes)


def _safe_dict(kwargs: dict[str, Any], allowed: Iterable[str]) -> dict[str, Any]:
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
    settings = _safe_dict(kwargs, _ALLOWED_TWO_COLUMN_KEYS)
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
    settings = _safe_dict(kwargs, _ALLOWED_TOP_VISUAL_KEYS)
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


def _candidate_definitions(
    *,
    requested_mode: str,
    metadata: dict[str, Any],
    density_score: float,
) -> list[tuple[str, str, tuple[float, float, float]]]:
    allow_top = bool(metadata.get("allow_top_strip", True))
    preferred_layout = str(metadata.get("preferred_layout", "either") or "either").strip().lower()

    candidates: list[tuple[str, str, tuple[float, float, float]]] = []

    # Put likely-good candidates first.
    if preferred_layout in {"hero", "top_visual"} and allow_top:
        candidates.append(("top_visual_hero", "top_visual", (0.28, 0.35, 0.44)))
    if requested_mode == "top_visual" and allow_top:
        candidates.append(("top_visual_requested", "top_visual", (0.24, 0.31, 0.40)))

    # Analytic defaults lean text-first.
    if density_score >= 7.5:
        candidates.append(("two_column_text_heavy", "two_column", (0.20, 0.24, 0.30)))
        candidates.append(("two_column", "two_column", (0.22, 0.27, 0.34)))
    else:
        candidates.append(("two_column", "two_column", (0.22, 0.28, 0.36)))
        candidates.append(("two_column_visual_heavy", "two_column", (0.26, 0.32, 0.40)))

    if allow_top and preferred_layout not in {"two_column"}:
        candidates.append(("top_visual", "top_visual", (0.22, 0.29, 0.38)))

    # Deduplicate by candidate name.
    seen: set[str] = set()
    deduped: list[tuple[str, str, tuple[float, float, float]]] = []
    for item in candidates:
        if item[0] in seen:
            continue
        seen.add(item[0])
        deduped.append(item)
    return deduped


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


def layout_analytic_panel_top_visual(
    outer_box,
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
    outer_box,
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


def layout_analytic_panel(
    outer_box,
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
    metadata = _merged_visual_metadata(visual_kind)
    density = _density_score(
        explanation_text=explanation_text,
        steps_text=steps_text,
        result_text=result_text,
        takeaway_text=takeaway_text,
    )

    requested_mode = str(layout_mode or "two_column").strip().lower()
    candidate_defs = _candidate_definitions(requested_mode=requested_mode, metadata=metadata, density_score=density)
    if force_candidates:
        wanted = {str(name) for name in force_candidates}
        candidate_defs = [c for c in candidate_defs if c[0] in wanted]
    if not candidate_defs:
        candidate_defs = [("two_column", "two_column", (0.22, 0.28, 0.36))]

    best_result: AnalyticPanelLayoutResult | None = None

    for candidate_name, family, shares in candidate_defs:
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

        score, notes = _candidate_score(base, metadata=metadata, candidate_name=candidate_name, density_score=density)
        overflow = tuple(sorted(k for k, fit in base.text_fits.items() if not fit.fits))
        split_required = bool(score >= split_score_threshold or (len(overflow) >= 2 and density >= 8.0))
        result = _as_result(base, candidate_name=candidate_name, score=score, split_required=split_required, overflow_sections=overflow, notes=notes)
        if best_result is None or result.score < best_result.score:
            best_result = result

    assert best_result is not None
    return best_result


__all__ = [
    "AnalyticPanelLayoutResult",
    "layout_analytic_panel",
    "layout_analytic_panel_top_visual",
    "layout_analytic_panel_two_column",
]

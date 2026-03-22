from __future__ import annotations

from slideforge.layout.worked_example import (
    WorkedExampleLayoutResult,
    layout_worked_example,
    layout_worked_example_top_visual,
    layout_worked_example_two_column,
)


_TWO_COLUMN_DEFAULTS = {
    "top_pad": 0.16,
    "bottom_pad": 0.14,
    "side_pad": 0.20,
    "col_gap": 0.20,
    "gap": 0.10,
    "diagram_min_share": 0.22,
    "diagram_preferred_share": 0.28,
    "diagram_max_share": 0.38,
    "min_steps_h": 1.85,
    "explanation_min_h": 0.34,
    "explanation_max_h": 0.62,
    "result_min_h": 0.68,
    "result_max_h": 1.02,
    "takeaway_min_h": 0.48,
    "takeaway_max_h": 0.82,
    "min_diagram_h_share": 0.58,
}

_TOP_VISUAL_DEFAULTS = {
    "top_pad": 0.16,
    "bottom_pad": 0.14,
    "side_pad": 0.20,
    "gap": 0.10,
    "diagram_min_share": 0.22,
    "diagram_preferred_share": 0.28,
    "diagram_max_share": 0.40,
    "min_steps_h": 1.75,
    "explanation_min_h": 0.30,
    "explanation_max_h": 0.56,
    "result_min_h": 0.76,
    "result_max_h": 1.16,
    "takeaway_min_h": 0.54,
    "takeaway_max_h": 0.90,
}


def _merged(defaults: dict[str, float], kwargs: dict) -> dict:
    merged = dict(defaults)
    merged.update({k: v for k, v in kwargs.items() if v is not None})
    return merged


def _density_boost(
    *,
    steps_text: str = "",
    result_text: str = "",
    takeaway_text: str = "",
    explanation_text: str = "",
) -> dict[str, float]:
    score = 0
    score += 2 * max(0, steps_text.count("Step "))
    score += 1 if explanation_text.strip() else 0
    score += max(0, len([line for line in result_text.splitlines() if line.strip()]) - 1)
    score += 1 if takeaway_text.strip() else 0
    score += min(3, len(steps_text) // 180)

    if score >= 10:
        return {
            "diagram_preferred_share": 0.24,
            "diagram_max_share": 0.34,
            "min_steps_h": 2.05,
            "result_min_h": 0.80,
            "takeaway_min_h": 0.58,
        }
    if score >= 7:
        return {
            "diagram_preferred_share": 0.26,
            "diagram_max_share": 0.36,
            "min_steps_h": 1.95,
            "result_min_h": 0.74,
            "takeaway_min_h": 0.54,
        }
    return {}


def layout_analytic_panel_two_column(
    outer_box,
    *,
    explanation_text: str = "",
    steps_text: str = "",
    result_text: str = "",
    takeaway_text: str = "",
    **kwargs,
) -> WorkedExampleLayoutResult:
    settings = _merged(_TWO_COLUMN_DEFAULTS, kwargs)
    settings.update(_density_boost(
        steps_text=steps_text,
        result_text=result_text,
        takeaway_text=takeaway_text,
        explanation_text=explanation_text,
    ))
    return layout_worked_example_two_column(
        outer_box,
        explanation_text=explanation_text,
        steps_text=steps_text,
        result_text=result_text,
        takeaway_text=takeaway_text,
        **settings,
    )


def layout_analytic_panel_top_visual(
    outer_box,
    *,
    explanation_text: str = "",
    steps_text: str = "",
    result_text: str = "",
    takeaway_text: str = "",
    **kwargs,
) -> WorkedExampleLayoutResult:
    settings = _merged(_TOP_VISUAL_DEFAULTS, kwargs)
    settings.update(_density_boost(
        steps_text=steps_text,
        result_text=result_text,
        takeaway_text=takeaway_text,
        explanation_text=explanation_text,
    ))
    return layout_worked_example_top_visual(
        outer_box,
        explanation_text=explanation_text,
        steps_text=steps_text,
        result_text=result_text,
        takeaway_text=takeaway_text,
        **settings,
    )


def layout_analytic_panel(
    outer_box,
    *,
    explanation_text: str = "",
    steps_text: str = "",
    result_text: str = "",
    takeaway_text: str = "",
    layout_mode: str = "two_column",
    **kwargs,
) -> WorkedExampleLayoutResult:
    mode = str(layout_mode or "two_column").strip().lower()
    if mode == "top_visual":
        return layout_analytic_panel_top_visual(
            outer_box,
            explanation_text=explanation_text,
            steps_text=steps_text,
            result_text=result_text,
            takeaway_text=takeaway_text,
            **kwargs,
        )
    return layout_analytic_panel_two_column(
        outer_box,
        explanation_text=explanation_text,
        steps_text=steps_text,
        result_text=result_text,
        takeaway_text=takeaway_text,
        **kwargs,
    )


__all__ = [
    "WorkedExampleLayoutResult",
    "layout_analytic_panel",
    "layout_analytic_panel_top_visual",
    "layout_analytic_panel_two_column",
]

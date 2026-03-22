from __future__ import annotations

from pptx import Presentation

from slideforge.builders.worked_example_panel import build_worked_example_panel_slide


def build_analytic_panel_slide(
    prs: Presentation,
    spec: dict,
    counters: dict[str, int],
) -> None:
    """Universal composition-semantic alias for the legacy worked-example builder.

    The engine concept is an analytic panel: a visual region plus a reasoning stack
    (steps, result, takeaway). Existing decks may still use ``worked_example_panel``;
    new decks should prefer ``analytic_panel``.
    """
    build_worked_example_panel_slide(prs, spec, counters)


__all__ = ["build_analytic_panel_slide"]

from __future__ import annotations

from pptx import Presentation

from slideforge.builders.worked_example_panel import build_worked_example_panel_slide


def build_analytic_panel_slide(
    prs: Presentation,
    spec: dict,
    counters: dict[str, int],
) -> None:
    build_worked_example_panel_slide(prs, spec, counters)


__all__ = ["build_analytic_panel_slide"]

from __future__ import annotations

from typing import Any, Mapping, Sequence

from slideforge.layout.multi_panel_summary import MultiPanelSummaryLayout, layout_multi_panel_summary
from slideforge.render.multi_panel_cards import render_multi_panel_panels


def render_triple_role_panels(
    slide,
    *,
    panels: Sequence[Mapping[str, Any]],
    panel_region,
    layout: Mapping[str, Any],
    style: Mapping[str, Any],
) -> None:
    layout_result = layout_multi_panel_summary(panel_region, panel_count=len(panels), layout=layout)
    render_multi_panel_panels(slide, panels=panels, layout_result=layout_result, layout=layout, style=style, suffix="_triple_role")


__all__ = ["render_triple_role_panels", "MultiPanelSummaryLayout"]

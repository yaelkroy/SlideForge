from __future__ import annotations

"""Compatibility façade for shared rendering helpers.

The real implementations now live in focused modules:
- slideforge.render.text
- slideforge.render.cards
- slideforge.render.connectors
- slideforge.render.decorations

Keep importing from ``slideforge.render.primitives`` during the transition.
"""

from slideforge.render.cards import (
    add_box_title,
    add_footer,
    add_hub_box,
    add_node_box,
    add_rounded_box,
    add_surface_card,
    add_title_panel,
)
from slideforge.render.connectors import add_arrow, add_soft_connector
from slideforge.render.decorations import (
    add_callout,
    add_divider_line,
    add_ghost_label,
    add_header_rule,
    add_pill_tag,
)
from slideforge.render.text import add_background, add_bullets_box, add_textbox, style_paragraph

__all__ = [
    "add_arrow",
    "add_background",
    "add_box_title",
    "add_bullets_box",
    "add_callout",
    "add_divider_line",
    "add_footer",
    "add_ghost_label",
    "add_header_rule",
    "add_hub_box",
    "add_node_box",
    "add_pill_tag",
    "add_rounded_box",
    "add_soft_connector",
    "add_surface_card",
    "add_textbox",
    "add_title_panel",
    "style_paragraph",
]

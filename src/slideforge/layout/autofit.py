from __future__ import annotations

from slideforge.layout.base import (
    Box,
    DEFAULT_WIDE_SLIDE,
    SlideSize,
    Unit,
)
from slideforge.layout.cards import (
    centered_visual_in_card,
    estimate_best_note_box,
)
from slideforge.layout.dependency import (
    DependencyMapLayoutResult,
    layout_dependency_map,
)
from slideforge.layout.grid import (
    distribute_columns,
    distribute_rows,
)
from slideforge.layout.poster import (
    PosterLayoutResult,
    layout_concept_poster,
)
from slideforge.layout.stack import (
    TextBlockSpec,
    VerticalLayoutResult,
    layout_vertical_stack,
)
from slideforge.layout.table import (
    TableLayoutResult,
    layout_notation_table,
)
from slideforge.layout.text_fit import (
    TextFit,
    choose_single_or_double_line_height,
    clamp,
    estimate_chars_per_line,
    estimate_text_height,
    fit_text,
    line_height_inches,
    normalize_text,
    points_to_inches,
    wrap_text_to_width,
)

__all__ = [
    "Unit",
    "Box",
    "SlideSize",
    "DEFAULT_WIDE_SLIDE",
    "TextFit",
    "TextBlockSpec",
    "VerticalLayoutResult",
    "PosterLayoutResult",
    "TableLayoutResult",
    "DependencyMapLayoutResult",
    "clamp",
    "points_to_inches",
    "line_height_inches",
    "estimate_chars_per_line",
    "normalize_text",
    "wrap_text_to_width",
    "estimate_text_height",
    "fit_text",
    "choose_single_or_double_line_height",
    "distribute_columns",
    "distribute_rows",
    "layout_vertical_stack",
    "layout_concept_poster",
    "layout_notation_table",
    "centered_visual_in_card",
    "estimate_best_note_box",
    "layout_dependency_map",
]
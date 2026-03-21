from __future__ import annotations

from collections.abc import Callable

from pptx import Presentation

from slideforge.builders.basic import (
    build_bullets_slide,
    build_formula_slide,
    build_image_slide,
    build_section_slide,
    build_title_slide,
    build_two_column_slide,
)
from slideforge.builders.card_grid import build_card_grid_slide
from slideforge.builders.concept_poster import build_concept_poster_slide
from slideforge.builders.dependency_map import build_dependency_map_slide
from slideforge.builders.example_pipeline import build_example_pipeline_slide
# from slideforge.builders.integrated_bridge import build_integrated_bridge_slide
from slideforge.builders.notation_panel import build_notation_panel_slide
from slideforge.builders.pipeline import build_pipeline_slide
from slideforge.builders.prereq_grid import build_prereq_grid_slide
from slideforge.builders.section_divider import build_section_divider_slide
from slideforge.builders.title_composite import build_title_composite_slide
from slideforge.builders.triple_role import build_triple_role_slide
from slideforge.builders.worked_example_panel import build_worked_example_panel_slide

SlideBuilder = Callable[[Presentation, dict], None]


BUILDERS: dict[str, SlideBuilder] = {
    # Core deck scaffolding
    "title": build_title_slide,
    "title_composite": build_title_composite_slide,
    "section": build_section_slide,
    "section_divider": build_section_divider_slide,
    # Standard content slides
    "bullets": build_bullets_slide,
    "formula": build_formula_slide,
    "two_column": build_two_column_slide,
    "image": build_image_slide,
    # Structured academic builders
    "dependency_map": build_dependency_map_slide,
    "pipeline": build_pipeline_slide,
    "prereq_grid": build_prereq_grid_slide,
    "example_pipeline": build_example_pipeline_slide,
    "card_grid": build_card_grid_slide,
    "notation_panel": build_notation_panel_slide,
    "triple_role": build_triple_role_slide,
    "concept_poster": build_concept_poster_slide,
    # Dense math / worked examples
    "worked_example_panel": build_worked_example_panel_slide,
    "worked_example": build_worked_example_panel_slide,
    # Compatibility placeholder for parked builder
    # "integrated_bridge": build_integrated_bridge_slide,
}


__all__ = ["BUILDERS", "SlideBuilder"]

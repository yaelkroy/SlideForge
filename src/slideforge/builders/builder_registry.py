from slideforge.builders.basic import (
    build_title_slide,
    build_section_slide,
    build_bullets_slide,
    build_formula_slide,
    build_two_column_slide,
    build_image_slide,
)
from slideforge.builders.title_composite import build_title_composite_slide
from slideforge.builders.section_divider import build_section_divider_slide
from slideforge.builders.dependency_map import build_dependency_map_slide


BUILDERS = {
    "title": build_title_slide,
    "title_composite": build_title_composite_slide,
    "section": build_section_slide,
    "section_divider": build_section_divider_slide,
    "bullets": build_bullets_slide,
    "formula": build_formula_slide,
    "two_column": build_two_column_slide,
    "image": build_image_slide,
    "dependency_map": build_dependency_map_slide,
}
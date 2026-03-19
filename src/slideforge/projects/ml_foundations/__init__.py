from __future__ import annotations

from slideforge.projects.ml_foundations.slides_part1 import ML_FOUNDATIONS_PART1_SLIDES
from slideforge.projects.ml_foundations.slides_part2 import ML_FOUNDATIONS_PART2_SLIDES


ML_FOUNDATIONS_SLIDES = [
    *ML_FOUNDATIONS_PART1_SLIDES,
    *ML_FOUNDATIONS_PART2_SLIDES,
]


__all__ = [
    "ML_FOUNDATIONS_PART1_SLIDES",
    "ML_FOUNDATIONS_PART2_SLIDES",
    "ML_FOUNDATIONS_SLIDES",
]
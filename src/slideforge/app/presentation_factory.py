from __future__ import annotations

from pptx import Presentation

from slideforge.config.constants import SLIDE_W, SLIDE_H
from slideforge.utils.units import inches


def create_presentation() -> Presentation:
    prs = Presentation()
    prs.slide_width = inches(SLIDE_W)
    prs.slide_height = inches(SLIDE_H)
    return prs
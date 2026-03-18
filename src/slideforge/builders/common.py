from __future__ import annotations

from pptx import Presentation

from slideforge.render.primitives import add_background


def new_slide(prs: Presentation, background_name: str):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, prs, background_name)
    return slide
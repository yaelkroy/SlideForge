from __future__ import annotations

from pptx.util import Inches, Pt


def inches(value: float):
    return Inches(value)


def pt(value: float):
    return Pt(value)
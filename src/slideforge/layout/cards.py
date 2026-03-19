from __future__ import annotations

from slideforge.layout.base import Box, Unit
from slideforge.layout.text_fit import TextFit, fit_text


def centered_visual_in_card(
    card_box: Box,
    *,
    title_h: Unit = 0.24,
    caption_h: Unit = 0.22,
    formula_h: Unit = 0.18,
    top_pad: Unit = 0.10,
    bottom_pad: Unit = 0.10,
    gap_above_visual: Unit = 0.08,
    gap_below_visual: Unit = 0.08,
) -> Box:
    """
    Compute a centered visual box inside a card so the diagram is not stuck at the top.
    """
    reserved_h = (
        top_pad
        + title_h
        + gap_above_visual
        + caption_h
        + formula_h
        + gap_below_visual
        + bottom_pad
    )
    visual_h = max(0.50, card_box.h - reserved_h)

    y = card_box.y + top_pad + title_h + gap_above_visual
    return Box(
        x=card_box.x + 0.14,
        y=y,
        w=max(0.20, card_box.w - 0.28),
        h=visual_h,
    )


def estimate_best_note_box(
    container: Box,
    text: str,
    *,
    min_font: int = 12,
    max_font: int = 14,
    max_lines: int = 2,
) -> tuple[Box, TextFit]:
    """
    Decide whether a note should occupy one or two lines and return a fitted box.
    """
    fit = fit_text(
        text,
        container.w,
        container.h,
        min_font_size=min_font,
        max_font_size=max_font,
        max_lines=max_lines,
    )
    final_h = min(container.h, fit.estimated_height)
    return Box(container.x, container.y, container.w, final_h), fit
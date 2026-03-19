from __future__ import annotations

from dataclasses import dataclass

from slideforge.layout.base import Box, Unit
from slideforge.layout.stack import TextBlockSpec, layout_vertical_stack
from slideforge.layout.text_fit import TextFit, clamp


@dataclass
class PosterLayoutResult:
    outer_box: Box
    visual_box: Box
    text_boxes: dict[str, Box]
    text_fits: dict[str, TextFit]
    visual_share: float


def layout_concept_poster(
    outer_box: Box,
    *,
    explanation: str = "",
    bullets_text: str = "",
    formulas_text: str = "",
    note_text: str = "",
    takeaway_text: str = "",
    top_pad: Unit = 0.20,
    bottom_pad: Unit = 0.14,
    gap: Unit = 0.08,
    visual_min_share: float = 0.65,
    visual_max_share: float = 0.78,
) -> PosterLayoutResult:
    """
    Create a vertically balanced concept-poster layout:
    large visual centered above a small stack of text blocks.

    The visual gets as much space as possible while respecting minimum readable
    text sizes. The remaining text boxes are auto-fitted and non-overlapping.
    """
    specs: list[TextBlockSpec] = []

    if explanation.strip():
        specs.append(
            TextBlockSpec(
                key="explanation",
                text=explanation,
                min_font_size=15,
                max_font_size=18,
                max_lines=3,
            )
        )

    if bullets_text.strip():
        specs.append(
            TextBlockSpec(
                key="bullets",
                text=bullets_text,
                min_font_size=13,
                max_font_size=15,
                max_lines=3,
            )
        )

    if formulas_text.strip():
        specs.append(
            TextBlockSpec(
                key="formulas",
                text=formulas_text,
                min_font_size=13,
                max_font_size=15,
                max_lines=2,
            )
        )

    if note_text.strip():
        # Notes often should be 1–2 lines, not tiny compressed paragraphs.
        specs.append(
            TextBlockSpec(
                key="note",
                text=note_text,
                min_font_size=12,
                max_font_size=14,
                max_lines=2,
            )
        )

    if takeaway_text.strip():
        specs.append(
            TextBlockSpec(
                key="takeaway",
                text=takeaway_text,
                min_font_size=13,
                max_font_size=15,
                max_lines=2,
                bold=True,
            )
        )

    usable_h = outer_box.h - top_pad - bottom_pad
    target_visual_h = clamp(
        usable_h * 0.72,
        usable_h * visual_min_share,
        usable_h * visual_max_share,
    )

    # Reserve lower text stack area first.
    lower_text_box = Box(
        outer_box.x + 0.22,
        outer_box.y + top_pad + target_visual_h + gap,
        outer_box.w - 0.44,
        max(
            0.0,
            outer_box.bottom - bottom_pad - (outer_box.y + top_pad + target_visual_h + gap),
        ),
    )

    text_layout = layout_vertical_stack(
        lower_text_box,
        specs,
        gap=gap,
        top_pad=0.0,
        bottom_pad=0.0,
    )

    # Recompute visual box from actual used text height.
    actual_text_h = text_layout.used_height
    visual_h = max(
        usable_h * visual_min_share,
        usable_h - actual_text_h - (gap if actual_text_h > 0 else 0.0),
    )
    visual_h = min(
        visual_h,
        usable_h * visual_max_share if actual_text_h > 0 else usable_h,
    )

    visual_box = Box(
        outer_box.x + 0.28,
        outer_box.y + top_pad,
        outer_box.w - 0.56,
        visual_h,
    )

    # Re-layout the text directly under the final visual box.
    lower_text_box = Box(
        outer_box.x + 0.22,
        visual_box.bottom + gap,
        outer_box.w - 0.44,
        max(0.0, outer_box.bottom - bottom_pad - (visual_box.bottom + gap)),
    )
    text_layout = layout_vertical_stack(
        lower_text_box,
        specs,
        gap=gap,
        top_pad=0.0,
        bottom_pad=0.0,
    )

    return PosterLayoutResult(
        outer_box=outer_box,
        visual_box=visual_box,
        text_boxes=text_layout.boxes,
        text_fits=text_layout.text_fits,
        visual_share=visual_box.h / max(outer_box.h, 1e-6),
    )
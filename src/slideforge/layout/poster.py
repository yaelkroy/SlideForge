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


def _build_text_specs(
    *,
    explanation: str,
    bullets_text: str,
    formulas_text: str,
    note_text: str,
    takeaway_text: str,
) -> list[TextBlockSpec]:
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
                min_font_size=12,
                max_font_size=14,
                max_lines=3,
            )
        )

    if note_text.strip():
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
                min_font_size=12,
                max_font_size=14,
                max_lines=2,
                bold=True,
            )
        )

    return specs


def _text_container(
    outer_box: Box,
    *,
    top_pad: Unit,
    bottom_pad: Unit,
    side_pad: Unit,
    visual_h: Unit,
    gap: Unit,
) -> Box:
    return Box(
        outer_box.x + side_pad,
        outer_box.y + top_pad + visual_h + gap,
        max(0.0, outer_box.w - 2 * side_pad),
        max(0.0, outer_box.h - top_pad - bottom_pad - visual_h - gap),
    )


def layout_concept_poster(
    outer_box: Box,
    *,
    explanation: str = "",
    bullets_text: str = "",
    formulas_text: str = "",
    note_text: str = "",
    takeaway_text: str = "",
    top_pad: Unit = 0.18,
    bottom_pad: Unit = 0.14,
    gap: Unit = 0.08,
    side_pad: Unit = 0.22,
    visual_min_share: float = 0.58,
    visual_max_share: float = 0.80,
) -> PosterLayoutResult:
    """
    Layout for concept-poster slides:

    - keeps one dominant visual
    - reserves a lower text stack
    - adapts when the text stack becomes denser
    - prevents the visual from being squeezed to a tiny top strip

    The result is intentionally conservative for mathematical slides so formulas,
    notes, and takeaway lines do not collide.
    """
    usable_h = max(0.0, outer_box.h - top_pad - bottom_pad)
    specs = _build_text_specs(
        explanation=explanation,
        bullets_text=bullets_text,
        formulas_text=formulas_text,
        note_text=note_text,
        takeaway_text=takeaway_text,
    )

    if usable_h <= 0:
        empty_visual = Box(
            outer_box.x + side_pad,
            outer_box.y + top_pad,
            max(0.0, outer_box.w - 2 * side_pad),
            0.0,
        )
        return PosterLayoutResult(
            outer_box=outer_box,
            visual_box=empty_visual,
            text_boxes={},
            text_fits={},
            visual_share=0.0,
        )

    min_visual_h = usable_h * clamp(visual_min_share, 0.0, 1.0)
    max_visual_h = usable_h * clamp(visual_max_share, 0.0, 1.0)

    # Start from a generous visual share, then reduce only as much as needed.
    target_visual_h = min(max_visual_h, usable_h * 0.73)

    # Pass 1: estimate text below a candidate visual.
    pass1_text_box = _text_container(
        outer_box,
        top_pad=top_pad,
        bottom_pad=bottom_pad,
        side_pad=side_pad,
        visual_h=target_visual_h,
        gap=gap,
    )
    pass1 = layout_vertical_stack(
        pass1_text_box,
        specs,
        gap=gap,
        top_pad=0.0,
        bottom_pad=0.0,
    )

    # Rebalance:
    # - if text is light, visual can stay large
    # - if text is dense, give more room to text but never let visual collapse
    text_h_needed = pass1.used_height
    if specs:
        visual_h = usable_h - text_h_needed - gap
    else:
        visual_h = usable_h

    visual_h = clamp(visual_h, min_visual_h, max_visual_h)

    visual_box = Box(
        outer_box.x + side_pad + 0.06,
        outer_box.y + top_pad,
        max(0.0, outer_box.w - 2 * side_pad - 0.12),
        visual_h,
    )

    # Pass 2: final text stack directly below final visual box.
    final_text_box = Box(
        outer_box.x + side_pad,
        visual_box.bottom + gap,
        max(0.0, outer_box.w - 2 * side_pad),
        max(0.0, outer_box.bottom - bottom_pad - (visual_box.bottom + gap)),
    )
    final_text_layout = layout_vertical_stack(
        final_text_box,
        specs,
        gap=gap,
        top_pad=0.0,
        bottom_pad=0.0,
    )

    # If the final text stack still overflows badly, compress by shrinking visual
    # one more time, but preserve the minimum concept-poster visual share.
    remaining_text_overflow = max(0.0, final_text_layout.used_height - final_text_box.h)
    if remaining_text_overflow > 0.02:
        adjusted_visual_h = max(min_visual_h, visual_box.h - remaining_text_overflow)
        if adjusted_visual_h < visual_box.h:
            visual_box = Box(
                visual_box.x,
                visual_box.y,
                visual_box.w,
                adjusted_visual_h,
            )
            final_text_box = Box(
                outer_box.x + side_pad,
                visual_box.bottom + gap,
                max(0.0, outer_box.w - 2 * side_pad),
                max(0.0, outer_box.bottom - bottom_pad - (visual_box.bottom + gap)),
            )
            final_text_layout = layout_vertical_stack(
                final_text_box,
                specs,
                gap=gap,
                top_pad=0.0,
                bottom_pad=0.0,
            )

    return PosterLayoutResult(
        outer_box=outer_box,
        visual_box=visual_box,
        text_boxes=final_text_layout.boxes,
        text_fits=final_text_layout.text_fits,
        visual_share=visual_box.h / max(outer_box.h, 1e-6),
    )
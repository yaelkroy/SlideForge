from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from slideforge.layout.base import Box, Unit
from slideforge.layout.text_fit import TextFit, fit_text, line_height_inches


@dataclass
class TextBlockSpec:
    """
    Declarative input for vertical layout and text fitting.

    height_mode:
      - "auto": estimate from text and choose font size between max/min
      - "fixed": use fixed_h exactly
    """

    key: str
    text: str
    min_font_size: int = 12
    max_font_size: int = 18
    fixed_h: Unit | None = None
    line_spacing: float = 1.15
    height_mode: Literal["auto", "fixed"] = "auto"
    prefer_single_line: bool = False
    max_lines: int | None = None
    bold: bool = False


@dataclass
class VerticalLayoutResult:
    container: Box
    boxes: dict[str, Box] = field(default_factory=dict)
    text_fits: dict[str, TextFit] = field(default_factory=dict)
    used_height: Unit = 0.0
    free_height: Unit = 0.0


def layout_vertical_stack(
    container: Box,
    specs: list[TextBlockSpec],
    *,
    gap: Unit = 0.08,
    top_pad: Unit = 0.0,
    bottom_pad: Unit = 0.0,
) -> VerticalLayoutResult:
    """
    Stack text blocks vertically inside a container with automatic height sizing.

    This is useful for:
    - explanation + bullets + formulas + notes under a diagram
    - compact slide posters
    - text areas that must not overlap
    """
    result = VerticalLayoutResult(container=container)

    inner = container.inset(0.0, 0.0)
    usable_y = inner.y + top_pad
    usable_h = max(0.0, inner.h - top_pad - bottom_pad)

    estimates: list[tuple[TextBlockSpec, float, TextFit | None]] = []
    total_h = 0.0

    for spec in specs:
        if spec.height_mode == "fixed" and spec.fixed_h is not None:
            estimates.append((spec, spec.fixed_h, None))
            total_h += spec.fixed_h
        else:
            fit = fit_text(
                spec.text,
                inner.w,
                usable_h,
                min_font_size=spec.min_font_size,
                max_font_size=spec.max_font_size,
                line_spacing=spec.line_spacing,
                prefer_single_line=spec.prefer_single_line,
                max_lines=spec.max_lines,
            )
            h = fit.estimated_height
            estimates.append((spec, h, fit))
            total_h += h

    total_h += max(0, len(specs) - 1) * gap

    if total_h > usable_h and specs:
        overflow = total_h - usable_h
        auto_indices = [
            i for i, (s, _, _) in enumerate(estimates) if s.height_mode == "auto"
        ]
        if auto_indices:
            per_block = overflow / len(auto_indices)
            new_estimates: list[tuple[TextBlockSpec, float, TextFit | None]] = []

            for idx, (spec, h, fit) in enumerate(estimates):
                if idx in auto_indices:
                    new_h = max(
                        line_height_inches(spec.min_font_size, spec.line_spacing) + 0.04,
                        h - per_block,
                    )
                    refit = fit_text(
                        spec.text,
                        inner.w,
                        new_h,
                        min_font_size=spec.min_font_size,
                        max_font_size=(fit.font_size if fit else spec.max_font_size),
                        line_spacing=spec.line_spacing,
                        prefer_single_line=False,
                        max_lines=spec.max_lines,
                    )
                    new_estimates.append((spec, max(new_h, refit.estimated_height), refit))
                else:
                    new_estimates.append((spec, h, fit))

            estimates = new_estimates

    y = usable_y
    for spec, h, fit in estimates:
        box = Box(inner.x, y, inner.w, h)
        result.boxes[spec.key] = box
        if fit is not None:
            result.text_fits[spec.key] = fit
        y += h + gap

    result.used_height = max(0.0, y - usable_y - gap if specs else 0.0)
    result.free_height = max(0.0, usable_h - result.used_height)
    return result
from __future__ import annotations

import math
import textwrap
from dataclasses import dataclass

from slideforge.config.constants import BODY_FONT, FORMULA_FONT, TITLE_FONT, SLIDE_H, SLIDE_W


_FONT_WIDTH_FACTORS = {
    BODY_FONT.lower(): 0.50,
    TITLE_FONT.lower(): 0.52,
    FORMULA_FONT.lower(): 0.56,
}


@dataclass(frozen=True)
class FittedText:
    font_size: int
    line_count: int
    height_in: float
    wrapped_lines: list[str]


def _font_factor(font_name: str, bold: bool = False) -> float:
    base = _FONT_WIDTH_FACTORS.get(font_name.lower(), 0.51)
    return base + (0.03 if bold else 0.0)


def _chars_per_line(width_in: float, font_size_pt: int, font_name: str, bold: bool = False) -> int:
    usable_pt = max(12.0, width_in * 72.0)
    avg_char_pt = max(4.0, font_size_pt * _font_factor(font_name, bold=bold))
    return max(4, int(usable_pt / avg_char_pt))


def wrap_text_to_width(
    text: str,
    width_in: float,
    font_size_pt: int,
    font_name: str = BODY_FONT,
    bold: bool = False,
) -> list[str]:
    clean = " ".join(text.replace("\n", " \n ").split())
    if not clean:
        return [""]

    parts = []
    current: list[str] = []
    limit = _chars_per_line(width_in, font_size_pt, font_name, bold=bold)

    for token in clean.split(" "):
        if token == "\n":
            if current:
                parts.append(" ".join(current))
                current = []
            else:
                parts.append("")
            continue

        trial = " ".join(current + [token]).strip()
        if len(trial) <= limit:
            current.append(token)
            continue

        if current:
            parts.append(" ".join(current))
            current = [token]
        else:
            hard = textwrap.wrap(token, width=limit) or [token]
            parts.extend(hard[:-1])
            current = [hard[-1]]

    if current:
        parts.append(" ".join(current))

    return parts or [""]


def estimate_text_height_in(
    text: str,
    width_in: float,
    font_size_pt: int,
    font_name: str = BODY_FONT,
    bold: bool = False,
    line_spacing: float = 1.12,
    pad_top_in: float = 0.00,
    pad_bottom_in: float = 0.00,
) -> float:
    lines = wrap_text_to_width(text, width_in, font_size_pt, font_name=font_name, bold=bold)
    line_h_in = (font_size_pt / 72.0) * line_spacing
    return pad_top_in + pad_bottom_in + max(1, len(lines)) * line_h_in


def fit_text_to_box(
    text: str,
    width_in: float,
    height_in: float,
    *,
    min_font_size: int = 12,
    max_font_size: int = 18,
    font_name: str = BODY_FONT,
    bold: bool = False,
    line_spacing: float = 1.12,
    pad_top_in: float = 0.00,
    pad_bottom_in: float = 0.00,
) -> FittedText:
    best_size = min_font_size
    best_lines = wrap_text_to_width(text, width_in, best_size, font_name=font_name, bold=bold)

    for size in range(max_font_size, min_font_size - 1, -1):
        wrapped = wrap_text_to_width(text, width_in, size, font_name=font_name, bold=bold)
        needed_h = estimate_text_height_in(
            text,
            width_in,
            size,
            font_name=font_name,
            bold=bold,
            line_spacing=line_spacing,
            pad_top_in=pad_top_in,
            pad_bottom_in=pad_bottom_in,
        )
        if needed_h <= height_in:
            return FittedText(
                font_size=size,
                line_count=max(1, len(wrapped)),
                height_in=needed_h,
                wrapped_lines=wrapped,
            )

        best_size = size
        best_lines = wrapped

    fallback_h = estimate_text_height_in(
        text,
        width_in,
        best_size,
        font_name=font_name,
        bold=bold,
        line_spacing=line_spacing,
        pad_top_in=pad_top_in,
        pad_bottom_in=pad_bottom_in,
    )
    return FittedText(
        font_size=best_size,
        line_count=max(1, len(best_lines)),
        height_in=fallback_h,
        wrapped_lines=best_lines,
    )


def stack_heights_centered(
    container_y: float,
    container_h: float,
    block_heights: list[float],
    gap: float,
) -> list[float]:
    if not block_heights:
        return []

    total_h = sum(block_heights) + gap * (len(block_heights) - 1)
    start_y = container_y + max(0.0, (container_h - total_h) / 2.0)

    ys: list[float] = []
    current = start_y
    for h in block_heights:
        ys.append(current)
        current += h + gap
    return ys


def centered_box(
    outer_x: float,
    outer_y: float,
    outer_w: float,
    outer_h: float,
    inner_w: float,
    inner_h: float,
    *,
    y_bias: float = 0.0,
) -> tuple[float, float, float, float]:
    x = outer_x + max(0.0, (outer_w - inner_w) / 2.0)
    y = outer_y + max(0.0, (outer_h - inner_h) / 2.0) + y_bias
    return x, y, inner_w, inner_h


def safe_inner_box(
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    pad_x: float = 0.18,
    pad_top: float = 0.16,
    pad_bottom: float = 0.16,
) -> tuple[float, float, float, float]:
    return (
        x + pad_x,
        y + pad_top,
        max(0.1, w - 2 * pad_x),
        max(0.1, h - pad_top - pad_bottom),
    )


def max_visual_height_after_text(
    container_h: float,
    text_heights: list[float],
    *,
    gap: float = 0.08,
    min_visual_h: float = 2.50,
) -> float:
    reserved = sum(text_heights)
    if text_heights:
        reserved += gap * len(text_heights)
    return max(min_visual_h, container_h - reserved)


def slide_aspect_ratio() -> float:
    return SLIDE_W / SLIDE_H


def choose_lines_or_width(
    text: str,
    width_in: float,
    target_lines: int,
    *,
    min_font_size: int,
    max_font_size: int,
    font_name: str = BODY_FONT,
    bold: bool = False,
) -> int:
    best = min_font_size
    for size in range(max_font_size, min_font_size - 1, -1):
        wrapped = wrap_text_to_width(text, width_in, size, font_name=font_name, bold=bold)
        if len(wrapped) <= target_lines:
            return size
        best = size
    return best
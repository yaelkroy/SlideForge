from __future__ import annotations

from dataclasses import dataclass
import math
import textwrap


POINTS_PER_INCH = 72.0


@dataclass
class FitResult:
    text: str
    font_size: int
    lines: int
    height_in: float


def estimate_chars_per_line(
    width_in: float,
    font_size: int,
    avg_char_factor: float = 0.54,
    horizontal_padding_in: float = 0.0,
) -> int:
    usable_width_in = max(0.15, width_in - horizontal_padding_in)
    usable_width_pt = usable_width_in * POINTS_PER_INCH
    chars = usable_width_pt / max(1.0, font_size * avg_char_factor)
    return max(3, int(chars))


def wrap_text_to_width(
    text: str,
    width_in: float,
    font_size: int,
    avg_char_factor: float = 0.54,
    max_lines: int | None = None,
) -> list[str]:
    raw = " ".join(str(text).replace("\n", " ").split())
    if not raw:
        return [""]

    width = estimate_chars_per_line(
        width_in=width_in,
        font_size=font_size,
        avg_char_factor=avg_char_factor,
    )
    wrapper = textwrap.TextWrapper(
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
        replace_whitespace=False,
        drop_whitespace=True,
    )
    lines = wrapper.wrap(raw) or [raw]

    if max_lines is not None and len(lines) > max_lines:
        kept = lines[:max_lines]
        if kept:
            last = kept[-1].rstrip()
            if len(last) > 1 and not last.endswith("…"):
                last = last[:-1].rstrip()
            kept[-1] = f"{last}…"
        lines = kept

    return lines


def estimate_text_height_in(
    line_count: int,
    font_size: int,
    line_spacing: float = 1.18,
    vertical_padding_in: float = 0.02,
) -> float:
    line_height_in = (font_size * line_spacing) / POINTS_PER_INCH
    return line_count * line_height_in + vertical_padding_in


def fit_text_to_box(
    text: str,
    width_in: float,
    height_in: float,
    *,
    min_font_size: int,
    max_font_size: int,
    max_lines: int | None = None,
    avg_char_factor: float = 0.54,
    line_spacing: float = 1.18,
    vertical_padding_in: float = 0.02,
) -> FitResult:
    cleaned = " ".join(str(text).replace("\n", " ").split())
    if not cleaned:
        return FitResult(text="", font_size=max_font_size, lines=0, height_in=0.0)

    for size in range(max_font_size, min_font_size - 1, -1):
        lines = wrap_text_to_width(
            text=cleaned,
            width_in=width_in,
            font_size=size,
            avg_char_factor=avg_char_factor,
            max_lines=max_lines,
        )
        text_height = estimate_text_height_in(
            line_count=len(lines),
            font_size=size,
            line_spacing=line_spacing,
            vertical_padding_in=vertical_padding_in,
        )
        if text_height <= height_in:
            return FitResult(
                text="\n".join(lines),
                font_size=size,
                lines=len(lines),
                height_in=text_height,
            )

    lines = wrap_text_to_width(
        text=cleaned,
        width_in=width_in,
        font_size=min_font_size,
        avg_char_factor=avg_char_factor,
        max_lines=max_lines,
    )
    text_height = estimate_text_height_in(
        line_count=len(lines),
        font_size=min_font_size,
        line_spacing=line_spacing,
        vertical_padding_in=vertical_padding_in,
    )
    return FitResult(
        text="\n".join(lines),
        font_size=min_font_size,
        lines=len(lines),
        height_in=min(text_height, height_in),
    )


def fit_joined_items_to_box(
    items: list[str],
    width_in: float,
    height_in: float,
    *,
    min_font_size: int,
    max_font_size: int,
    separator: str = "   •   ",
    max_lines: int | None = 2,
    avg_char_factor: float = 0.54,
    line_spacing: float = 1.18,
) -> FitResult:
    cleaned_items = [item.strip() for item in items if item and item.strip()]
    joined = separator.join(cleaned_items)
    return fit_text_to_box(
        text=joined,
        width_in=width_in,
        height_in=height_in,
        min_font_size=min_font_size,
        max_font_size=max_font_size,
        max_lines=max_lines,
        avg_char_factor=avg_char_factor,
        line_spacing=line_spacing,
    )


def distribute_vertical_stack(
    top_y: float,
    available_h: float,
    block_heights: list[float],
    gap: float,
) -> list[float]:
    if not block_heights:
        return []

    total_h = sum(block_heights) + gap * max(0, len(block_heights) - 1)
    start_y = top_y + max(0.0, (available_h - total_h) / 2.0)

    ys: list[float] = []
    cursor = start_y
    for h in block_heights:
        ys.append(cursor)
        cursor += h + gap
    return ys


def bounded(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))
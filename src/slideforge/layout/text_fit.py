from __future__ import annotations

from dataclasses import dataclass
import textwrap

from slideforge.layout.base import Unit


@dataclass
class TextFit:
    text: str
    font_size: int
    line_count: int
    wrapped_lines: list[str]
    estimated_height: Unit
    fits: bool


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def points_to_inches(points: float) -> float:
    return points / 72.0


def line_height_inches(font_size_pt: int, line_spacing: float = 1.18) -> float:
    """
    Convert font size to a practical line-height estimate in inches.

    Slightly conservative line spacing helps prevent PowerPoint-rendered text
    from touching the bottom edge of fitted boxes.
    """
    return points_to_inches(font_size_pt) * line_spacing


def estimate_chars_per_line(
    box_width_in: float,
    font_size_pt: int,
    *,
    avg_char_width_em: float = 0.55,
    min_chars: int = 4,
) -> int:
    """
    Roughly estimate the number of characters that fit on one line.

    For Latin text in PowerPoint-like fonts, 0.52 to 0.58 em is a practical
    average character width estimate.
    """
    char_width_in = points_to_inches(font_size_pt) * avg_char_width_em
    if char_width_in <= 0:
        return min_chars
    return max(min_chars, int(box_width_in / char_width_in))


def normalize_text(text: str) -> str:
    return " ".join((text or "").replace("\n", " \n ").split())


def wrap_text_to_width(
    text: str,
    box_width_in: float,
    font_size_pt: int,
    *,
    avg_char_width_em: float = 0.55,
) -> list[str]:
    """
    Wrap text while preserving manual line breaks as hard breaks.
    """
    normalized = text or ""
    segments = normalized.split("\n")
    width_chars = estimate_chars_per_line(
        box_width_in,
        font_size_pt,
        avg_char_width_em=avg_char_width_em,
    )

    wrapped: list[str] = []
    for seg in segments:
        seg = seg.strip()
        if not seg:
            wrapped.append("")
            continue
        wrapped.extend(
            textwrap.wrap(
                seg,
                width=width_chars,
                break_long_words=False,
                break_on_hyphens=False,
            )
            or [seg]
        )
    return wrapped


def estimate_text_height(
    text: str,
    box_width_in: float,
    font_size_pt: int,
    *,
    line_spacing: float = 1.18,
    padding_y_in: float = 0.03,
    avg_char_width_em: float = 0.55,
) -> tuple[float, int, list[str]]:
    """
    Estimate text block height for PowerPoint placement.

    The padding is intentionally a bit conservative so the final rendered text
    is less likely to overlap the bottom border of a container.
    """
    lines = wrap_text_to_width(
        text,
        box_width_in,
        font_size_pt,
        avg_char_width_em=avg_char_width_em,
    )
    nonempty_lines = max(1, len(lines))
    h = nonempty_lines * line_height_inches(font_size_pt, line_spacing) + 2 * padding_y_in
    return h, nonempty_lines, lines


def fit_text(
    text: str,
    box_width_in: float,
    box_height_in: float,
    *,
    min_font_size: int = 12,
    max_font_size: int = 18,
    line_spacing: float = 1.18,
    prefer_single_line: bool = False,
    max_lines: int | None = None,
    avg_char_width_em: float = 0.55,
) -> TextFit:
    """
    Choose the largest font size that fits both horizontally and vertically.
    """
    text = text or ""
    chosen: TextFit | None = None

    for size in range(max_font_size, min_font_size - 1, -1):
        est_h, line_count, lines = estimate_text_height(
            text,
            box_width_in,
            size,
            line_spacing=line_spacing,
            avg_char_width_em=avg_char_width_em,
        )
        fits_height = est_h <= box_height_in
        fits_lines = True if max_lines is None else (line_count <= max_lines)

        if prefer_single_line and line_count > 1:
            fits_lines = False

        if fits_height and fits_lines:
            return TextFit(
                text=text,
                font_size=size,
                line_count=line_count,
                wrapped_lines=lines,
                estimated_height=est_h,
                fits=True,
            )

        chosen = TextFit(
            text=text,
            font_size=size,
            line_count=line_count,
            wrapped_lines=lines,
            estimated_height=est_h,
            fits=False,
        )

    return chosen or TextFit(
        text=text,
        font_size=min_font_size,
        line_count=1,
        wrapped_lines=[text],
        estimated_height=line_height_inches(min_font_size, line_spacing),
        fits=False,
    )


def choose_single_or_double_line_height(
    text: str,
    box_width_in: float,
    *,
    font_size_pt: int,
    line_spacing: float = 1.18,
    avg_char_width_em: float = 0.55,
    single_line_pad: float = 0.06,
    double_line_pad: float = 0.06,
) -> tuple[int, float]:
    """
    Decide whether a note is naturally one or two lines at a given font size.
    Returns (line_count, suggested_height_inches).
    """
    lines = wrap_text_to_width(
        text,
        box_width_in,
        font_size_pt,
        avg_char_width_em=avg_char_width_em,
    )
    line_count = 1 if len(lines) <= 1 else 2
    if line_count == 1:
        return 1, line_height_inches(font_size_pt, line_spacing) + single_line_pad
    return 2, 2 * line_height_inches(font_size_pt, line_spacing) + double_line_pad
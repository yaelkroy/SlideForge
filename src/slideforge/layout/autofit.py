from __future__ import annotations

from dataclasses import dataclass, field
import math
import textwrap
from typing import Iterable, Literal


Unit = float  # SlideForge currently uses inches in builders.


@dataclass(frozen=True)
class Box:
    """Axis-aligned rectangle in slide units (typically inches)."""

    x: Unit
    y: Unit
    w: Unit
    h: Unit

    @property
    def right(self) -> Unit:
        return self.x + self.w

    @property
    def bottom(self) -> Unit:
        return self.y + self.h

    def inset(self, pad_x: Unit = 0.0, pad_y: Unit | None = None) -> "Box":
        py = pad_x if pad_y is None else pad_y
        return Box(
            x=self.x + pad_x,
            y=self.y + py,
            w=max(0.0, self.w - 2 * pad_x),
            h=max(0.0, self.h - 2 * py),
        )

    def move(self, dx: Unit = 0.0, dy: Unit = 0.0) -> "Box":
        return Box(self.x + dx, self.y + dy, self.w, self.h)

    def with_height(self, h: Unit) -> "Box":
        return Box(self.x, self.y, self.w, h)

    def with_width(self, w: Unit) -> "Box":
        return Box(self.x, self.y, w, self.h)


@dataclass(frozen=True)
class SlideSize:
    width: Unit = 13.333
    height: Unit = 7.5


DEFAULT_WIDE_SLIDE = SlideSize()


@dataclass
class TextFit:
    text: str
    font_size: int
    line_count: int
    wrapped_lines: list[str]
    estimated_height: Unit
    fits: bool


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


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def points_to_inches(points: float) -> float:
    return points / 72.0


def line_height_inches(font_size_pt: int, line_spacing: float = 1.15) -> float:
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
    line_spacing: float = 1.15,
    padding_y_in: float = 0.02,
    avg_char_width_em: float = 0.55,
) -> tuple[float, int, list[str]]:
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
    line_spacing: float = 1.15,
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
    line_spacing: float = 1.15,
    avg_char_width_em: float = 0.55,
    single_line_pad: float = 0.05,
    double_line_pad: float = 0.05,
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


def distribute_columns(
    container: Box,
    n: int,
    *,
    gap: Unit = 0.25,
    ratios: Iterable[float] | None = None,
) -> list[Box]:
    if n <= 0:
        return []

    if ratios is None:
        ratios = [1.0] * n
    ratios_list = list(ratios)
    if len(ratios_list) != n:
        raise ValueError("ratios length must equal n")

    total_gap = gap * (n - 1)
    usable_w = max(0.0, container.w - total_gap)
    ratio_sum = sum(ratios_list)
    if ratio_sum <= 0:
        ratio_sum = float(n)
        ratios_list = [1.0] * n

    boxes: list[Box] = []
    x = container.x
    for idx, r in enumerate(ratios_list):
        w = usable_w * (r / ratio_sum)
        if idx == n - 1:
            # Force last box to close floating-point drift.
            w = container.right - x
        boxes.append(Box(x, container.y, w, container.h))
        x += w + gap
    return boxes


def distribute_rows(
    container: Box,
    n: int,
    *,
    gap: Unit = 0.20,
    ratios: Iterable[float] | None = None,
) -> list[Box]:
    if n <= 0:
        return []

    if ratios is None:
        ratios = [1.0] * n
    ratios_list = list(ratios)
    if len(ratios_list) != n:
        raise ValueError("ratios length must equal n")

    total_gap = gap * (n - 1)
    usable_h = max(0.0, container.h - total_gap)
    ratio_sum = sum(ratios_list)
    if ratio_sum <= 0:
        ratio_sum = float(n)
        ratios_list = [1.0] * n

    boxes: list[Box] = []
    y = container.y
    for idx, r in enumerate(ratios_list):
        h = usable_h * (r / ratio_sum)
        if idx == n - 1:
            h = container.bottom - y
        boxes.append(Box(container.x, y, container.w, h))
        y += h + gap
    return boxes


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

    # First pass: estimate heights at preferred max sizes.
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

    # If overflow happens, do a second pass reducing auto blocks proportionally.
    if total_h > usable_h and specs:
        overflow = total_h - usable_h
        auto_indices = [i for i, (s, _, _) in enumerate(estimates) if s.height_mode == "auto"]
        if auto_indices:
            per_block = overflow / len(auto_indices)
            new_estimates: list[tuple[TextBlockSpec, float, TextFit | None]] = []
            for idx, (spec, h, fit) in enumerate(estimates):
                if idx in auto_indices:
                    new_h = max(line_height_inches(spec.min_font_size, spec.line_spacing) + 0.04, h - per_block)
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
    target_visual_h = clamp(usable_h * 0.72, usable_h * visual_min_share, usable_h * visual_max_share)

    # Reserve lower text stack area first.
    lower_text_box = Box(
        outer_box.x + 0.22,
        outer_box.y + top_pad + target_visual_h + gap,
        outer_box.w - 0.44,
        max(0.0, outer_box.bottom - bottom_pad - (outer_box.y + top_pad + target_visual_h + gap)),
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
    visual_h = min(visual_h, usable_h * visual_max_share if actual_text_h > 0 else usable_h)

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


@dataclass
class TableLayoutResult:
    outer_box: Box
    header_box: Box
    row_boxes: list[Box]
    col_boxes: list[Box]
    recommended_body_font: int
    recommended_header_font: int


def layout_notation_table(
    outer_box: Box,
    *,
    rows: int,
    col_ratios: tuple[float, float, float] = (0.18, 0.38, 0.44),
    header_h: Unit = 0.34,
    row_gap: Unit = 0.04,
    col_gap: Unit = 0.12,
    min_body_font: int = 13,
    max_body_font: int = 18,
    min_header_font: int = 12,
    max_header_font: int = 16,
) -> TableLayoutResult:
    """
    Compute a notation table layout with readable row height and a recommended font size.

    This intentionally avoids tiny table fonts by deriving body font primarily from row height.
    """
    inner = outer_box.inset(0.14, 0.10)
    header_box = Box(inner.x, inner.y, inner.w, header_h)

    body_y = header_box.bottom + 0.06
    body_h = max(0.0, inner.bottom - body_y)
    row_boxes = distribute_rows(
        Box(inner.x, body_y, inner.w, body_h),
        rows,
        gap=row_gap,
    )
    col_boxes = distribute_columns(
        Box(inner.x, body_y, inner.w, body_h),
        3,
        gap=col_gap,
        ratios=col_ratios,
    )

    if row_boxes:
        row_h = row_boxes[0].h
    else:
        row_h = 0.45

    body_by_height = int((row_h * 72.0) / 1.35)
    recommended_body_font = int(clamp(body_by_height, min_body_font, max_body_font))

    header_by_height = int((header_h * 72.0) / 1.25)
    recommended_header_font = int(clamp(header_by_height, min_header_font, max_header_font))

    return TableLayoutResult(
        outer_box=outer_box,
        header_box=header_box,
        row_boxes=row_boxes,
        col_boxes=col_boxes,
        recommended_body_font=recommended_body_font,
        recommended_header_font=recommended_header_font,
    )


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
    reserved_h = top_pad + title_h + gap_above_visual + caption_h + formula_h + gap_below_visual + bottom_pad
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
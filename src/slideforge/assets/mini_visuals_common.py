from __future__ import annotations

from pathlib import Path
import re

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

from slideforge.config.constants import (
    ACCENT,
    BODY_FONT,
    FORMULA_FONT,
    GHOST_TEXT,
    MPL_BODY_FONT,
    MPL_FORMULA_FONT,
    NAVY,
    OFFWHITE,
    SLATE,
    TITLE_PANEL_LINE,
)
from slideforge.config.paths import GENERATED_DIR
from slideforge.render.primitives import add_textbox
from slideforge.utils.units import inches


def _mpl(rgb) -> tuple[float, float, float]:
    return tuple(channel / 255 for channel in rgb)


PALETTES = {
    "dark_on_light": {
        "fg": _mpl(NAVY),
        "soft": _mpl(SLATE),
        "accent": _mpl(ACCENT),
        "ghost": _mpl(GHOST_TEXT),
        "bg_soft": (0.92, 0.95, 1.0, 0.16),
        "bg_alt": (0.88, 0.92, 1.0, 0.10),
        "panel": (0.94, 0.96, 1.0, 0.35),
    },
    "light_on_dark": {
        "fg": _mpl(OFFWHITE),
        "soft": _mpl(TITLE_PANEL_LINE),
        "accent": _mpl(TITLE_PANEL_LINE),
        "ghost": _mpl(GHOST_TEXT),
        "bg_soft": (1.0, 1.0, 1.0, 0.08),
        "bg_alt": (1.0, 1.0, 1.0, 0.05),
        "panel": (1.0, 1.0, 1.0, 0.10),
    },
}


_LATEX_TO_UNICODE = {
    r"\\alpha": "α",
    r"\\beta": "β",
    r"\\gamma": "γ",
    r"\\delta": "δ",
    r"\\theta": "θ",
    r"\\lambda": "λ",
    r"\\mu": "μ",
    r"\\pi": "π",
    r"\\sigma": "σ",
    r"\\phi": "φ",
    r"\\psi": "ψ",
    r"\\omega": "ω",
    r"\\cdot": "·",
    r"\\times": "×",
    r"\\sum": "Σ",
    r"\\perp": "⟂",
    r"\\iff": "⟺",
    r"\\to": "→",
    r"\\rightarrow": "→",
    r"\\leftarrow": "←",
    r"\\geq": "≥",
    r"\\leq": "≤",
    r"\\neq": "≠",
}

_SUBSCRIPT_MAP = str.maketrans(
    {
        "0": "₀",
        "1": "₁",
        "2": "₂",
        "3": "₃",
        "4": "₄",
        "5": "₅",
        "6": "₆",
        "7": "₇",
        "8": "₈",
        "9": "₉",
        "+": "₊",
        "-": "₋",
        "=": "₌",
        "(": "₍",
        ")": "₎",
        "i": "ᵢ",
        "j": "ⱼ",
        "n": "ₙ",
    }
)

_SUPERSCRIPT_MAP = str.maketrans(
    {
        "0": "⁰",
        "1": "¹",
        "2": "²",
        "3": "³",
        "4": "⁴",
        "5": "⁵",
        "6": "⁶",
        "7": "⁷",
        "8": "⁸",
        "9": "⁹",
        "+": "⁺",
        "-": "⁻",
        "=": "⁼",
        "(": "⁽",
        ")": "⁾",
        "i": "ⁱ",
        "n": "ⁿ",
    }
)


def palette_for(variant: str) -> dict:
    return PALETTES.get(variant, PALETTES["dark_on_light"])


def add_image(slide, image_path: Path, x: float, y: float, w: float, h: float) -> None:
    slide.shapes.add_picture(
        str(image_path),
        inches(x),
        inches(y),
        width=inches(w),
        height=inches(h),
    )


def _canvas(path: Path, figsize: tuple[float, float] = (4.2, 2.4)):
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_alpha(0.0)
    ax.set_facecolor((1, 1, 1, 0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    return fig, ax


def _save(fig, path: Path) -> Path:
    fig.tight_layout(pad=0.05)
    fig.savefig(path, dpi=260, bbox_inches="tight", transparent=True)
    plt.close(fig)
    return path


def _normalize_symbolic_text(text: str) -> str:
    """Normalize lightweight symbolic labels to Unicode for safer raster rendering.

    This helper is intentionally conservative. It is meant for short labels inside
    mini-visual PNGs, not for rich derivations. Dense formulas should be rendered
    as native PowerPoint text by the builder layer instead.
    """
    normalized = text.strip()
    for source, target in _LATEX_TO_UNICODE.items():
        normalized = normalized.replace(source, target)

    normalized = normalized.replace("**", "^")
    normalized = normalized.replace("<=>", "⟺")
    normalized = normalized.replace("->", "→")
    normalized = normalized.replace("<-", "←")

    def _sub_replace(match: re.Match[str]) -> str:
        base = match.group(1)
        suffix = match.group(2).translate(_SUBSCRIPT_MAP)
        return f"{base}{suffix}"

    def _sup_replace(match: re.Match[str]) -> str:
        base = match.group(1)
        suffix = match.group(2).translate(_SUPERSCRIPT_MAP)
        return f"{base}{suffix}"

    normalized = re.sub(r"([A-Za-zα-ωΑ-Ω])_\{?([0-9ijn+\-=()]+)\}?", _sub_replace, normalized)
    normalized = re.sub(r"([A-Za-zα-ωΑ-Ω])\^\{?([0-9in+\-=()]+)\}?", _sup_replace, normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def _is_rich_formula_text(text: str) -> bool:
    """Heuristic for formulas that should not live inside raster mini-visuals."""
    text = text.strip()
    if not text:
        return False

    rich_markers = (
        "=",
        "/",
        "Σ",
        "∑",
        "⟺",
        "⇔",
        "∀",
        "∈",
        "lim",
        "arccos",
        "sqrt",
        "√",
        "matrix",
        "[",
        "]",
        "{",
        "}",
    )
    if any(marker in text for marker in rich_markers):
        return True
    if " " in text and len(text) > 12:
        return True
    if len(text) > 18:
        return True
    return False


def _choose_label_font_family(text: str, *, formula: bool, rich_formula: bool) -> str:
    """Use the broadest-coverage font for PNG labels.

    DejaVu Sans renders Greek, subscripts/superscripts, and mixed symbolic labels
    more reliably than the previous formula-mono choice. We keep MPL_FORMULA_FONT
    only for very small/simple tokens when the text is not rich.
    """
    if not formula:
        return MPL_BODY_FONT
    if rich_formula:
        return MPL_BODY_FONT

    simple_token = (
        len(text) <= 6
        and " " not in text
        and not any(ch in text for ch in ("=", "/", "[", "]", "{", "}"))
    )
    return MPL_FORMULA_FONT if simple_token else MPL_BODY_FONT


def _label_text(
    ax,
    x: float,
    y: float,
    text: str,
    p,
    *,
    size: float = 8.0,
    formula: bool = False,
    ha: str = "center",
    va: str = "center",
    color=None,
    allow_rich_formula: bool = False,
    fallback_text: str | None = None,
) -> None:
    """Render a short label inside a mini-visual PNG.

    Rich derivations should not be placed in raster assets. If such a label slips
    through, we either swap to a caller-provided fallback or normalize the text and
    render it with the safer sans font stack.
    """
    render_text = _normalize_symbolic_text(text) if formula else text
    rich_formula = formula and _is_rich_formula_text(render_text)

    if rich_formula and not allow_rich_formula:
        render_text = fallback_text or _normalize_symbolic_text(render_text)

    font_family = _choose_label_font_family(render_text, formula=formula, rich_formula=rich_formula)
    fontsize = size * (0.94 if rich_formula else 1.0)

    ax.text(
        x,
        y,
        render_text,
        ha=ha,
        va=va,
        fontsize=fontsize,
        color=p["fg"] if color is None else color,
        fontfamily=font_family,
        fontstyle="normal",
        math_fontfamily="dejavusans",
        linespacing=1.0,
        clip_on=False,
    )


def _rounded_box(ax, x: float, y: float, w: float, h: float, p, *, lw: float = 1.3, fill=None) -> None:
    ax.add_patch(
        mpatches.FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.18",
            linewidth=lw,
            edgecolor=p["fg"],
            facecolor=p["panel"] if fill is None else fill,
        )
    )


def _soft_panel(ax, x: float, y: float, w: float, h: float, p) -> None:
    _rounded_box(ax, x, y, w, h, p, lw=1.1, fill=p["panel"])


def _movie_icon(ax, x: float, y: float, w: float, h: float, p) -> None:
    _rounded_box(ax, x, y, w, h, p, lw=1.5, fill=(0, 0, 0, 0))
    ax.plot([x + 0.20, x + w - 0.20], [y + h * 0.72, y + h * 0.72], color=p["soft"], lw=1.1)
    cx = x + w / 2
    cy = y + h * 0.34
    tri_w = w * 0.22
    tri_h = h * 0.24
    triangle = mpatches.Polygon(
        [
            (cx - tri_w * 0.40, cy - tri_h / 2),
            (cx - tri_w * 0.40, cy + tri_h / 2),
            (cx + tri_w * 0.60, cy),
        ],
        closed=True,
        edgecolor=p["accent"],
        facecolor=p["accent"],
        linewidth=1.0,
    )
    ax.add_patch(triangle)


def _digit_card_shape(ax, x: float, y: float, w: float, h: float, p, digit: str = "7") -> None:
    _rounded_box(ax, x, y, w, h, p, lw=1.5, fill=(0, 0, 0, 0))
    _label_text(ax, x + w / 2, y + h / 2, digit, p, size=20, formula=True, color=p["accent"])


def _vector_strip(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    p,
    values: list[str],
    *,
    labels: list[str] | None = None,
) -> None:
    gap = 0.12
    cell_w = (w - gap * (len(values) - 1)) / len(values)
    for i, v in enumerate(values):
        cell_x = x + i * (cell_w + gap)
        face = p["bg_soft"] if v not in {"1", "x"} else p["accent"]
        rect = mpatches.Rectangle(
            (cell_x, y),
            cell_w,
            h,
            linewidth=1.2,
            edgecolor=p["fg"],
            facecolor=face,
        )
        ax.add_patch(rect)
        txt_color = (1, 1, 1) if v in {"1", "x"} else p["fg"]
        _label_text(
            ax,
            cell_x + cell_w / 2,
            y + h / 2,
            v,
            p,
            size=10,
            formula=True,
            color=txt_color,
        )
        if labels and i < len(labels):
            _label_text(
                ax,
                cell_x + cell_w / 2,
                y - 0.16,
                labels[i],
                p,
                size=6.8,
                ha="center",
                va="top",
                color=p["soft"],
            )


def _axes_2d(ax, p) -> None:
    ax.plot([1.0, 1.0], [0.9, 5.1], color=p["ghost"], lw=1.0)
    ax.plot([1.0, 9.0], [0.9, 0.9], color=p["ghost"], lw=1.0)
    ax.annotate("", xy=(1.0, 5.1), xytext=(1.0, 0.9), arrowprops=dict(arrowstyle="-|>", lw=1.0, color=p["ghost"]))
    ax.annotate("", xy=(9.0, 0.9), xytext=(1.0, 0.9), arrowprops=dict(arrowstyle="-|>", lw=1.0, color=p["ghost"]))


def _axes_3d_fake(ax, p) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]]:
    origin = (1.4, 1.1)
    x_end = (8.6, 1.1)
    y_end = (4.4, 3.2)
    z_end = (1.4, 5.3)
    ax.annotate("", xy=x_end, xytext=origin, arrowprops=dict(arrowstyle="-|>", lw=1.1, color=p["ghost"]))
    ax.annotate("", xy=y_end, xytext=origin, arrowprops=dict(arrowstyle="-|>", lw=1.1, color=p["ghost"]))
    ax.annotate("", xy=z_end, xytext=origin, arrowprops=dict(arrowstyle="-|>", lw=1.1, color=p["ghost"]))
    return origin, x_end, y_end, z_end


def _vector_arrow(
    ax,
    start: tuple[float, float],
    end: tuple[float, float],
    p,
    *,
    color=None,
    lw: float = 2.2,
    label: str | None = None,
    label_dx: float = 0.12,
    label_dy: float = 0.12,
) -> None:
    use_color = p["accent"] if color is None else color
    ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="-|>", lw=lw, color=use_color))
    if label:
        _label_text(ax, end[0] + label_dx, end[1] + label_dy, label, p, size=8.8, formula=True, color=p["fg"])


def _draw_checkmark(ax, cx: float, cy: float, size: float, color, *, lw: float = 2.2) -> None:
    x1 = cx - size * 0.40
    y1 = cy - size * 0.02
    x2 = cx - size * 0.10
    y2 = cy - size * 0.28
    x3 = cx + size * 0.42
    y3 = cy + size * 0.28
    ax.plot([x1, x2], [y1, y2], color=color, lw=lw, solid_capstyle="round")
    ax.plot([x2, x3], [y2, y3], color=color, lw=lw, solid_capstyle="round")


def _tip_projection(point: tuple[float, float], line_start: tuple[float, float], line_end: tuple[float, float]) -> tuple[float, float]:
    px, py = point
    ax, ay = line_start
    bx, by = line_end
    vx, vy = bx - ax, by - ay
    wx, wy = px - ax, py - ay
    denom = vx * vx + vy * vy
    if denom == 0:
        return line_start
    t = (wx * vx + wy * vy) / denom
    return (ax + t * vx, ay + t * vy)

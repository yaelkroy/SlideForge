from __future__ import annotations

from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pptx.enum.text import PP_ALIGN

from slideforge.config.constants import (
    ACCENT,
    BODY_FONT,
    FORMULA_FONT,
    GHOST_TEXT,
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
    },
    "light_on_dark": {
        "fg": _mpl(OFFWHITE),
        "soft": _mpl(TITLE_PANEL_LINE),
        "accent": _mpl(TITLE_PANEL_LINE),
        "ghost": _mpl(GHOST_TEXT),
    },
}


def add_image(slide, image_path: Path, x: float, y: float, w: float, h: float) -> None:
    slide.shapes.add_picture(
        str(image_path),
        inches(x),
        inches(y),
        width=inches(w),
        height=inches(h),
    )


def _canvas(path: Path, figsize: tuple[float, float] = (3.6, 2.0)):
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


def _movie_icon(ax, x: float, y: float, w: float, h: float, p) -> None:
    body = mpatches.FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.22",
        linewidth=1.5,
        edgecolor=p["fg"],
        facecolor=(0, 0, 0, 0),
    )
    ax.add_patch(body)

    ax.plot(
        [x + 0.20, x + w - 0.20],
        [y + h * 0.72, y + h * 0.72],
        color=p["soft"],
        lw=1.1,
    )

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


def _digit_card(ax, x: float, y: float, w: float, h: float, p, digit: str = "7") -> None:
    body = mpatches.FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.20",
        linewidth=1.5,
        edgecolor=p["fg"],
        facecolor=(0, 0, 0, 0),
    )
    ax.add_patch(body)
    ax.text(
        x + w / 2,
        y + h / 2,
        digit,
        ha="center",
        va="center",
        fontsize=18,
        color=p["accent"],
        fontfamily=FORMULA_FONT,
    )


def _vector_strip(ax, x: float, y: float, w: float, h: float, p, values: list[str]) -> None:
    gap = 0.12
    cell_w = (w - gap * (len(values) - 1)) / len(values)
    for i, v in enumerate(values):
        cell_x = x + i * (cell_w + gap)
        face = p["accent"] if v in {"1", "x"} else (0, 0, 0, 0)
        rect = mpatches.Rectangle(
            (cell_x, y),
            cell_w,
            h,
            linewidth=1.25,
            edgecolor=p["fg"],
            facecolor=face,
        )
        ax.add_patch(rect)
        txt_color = (1, 1, 1) if v in {"1", "x"} else p["fg"]
        ax.text(
            cell_x + cell_w / 2,
            y + h / 2,
            v,
            ha="center",
            va="center",
            fontsize=10,
            color=txt_color,
            fontfamily=FORMULA_FONT,
        )


def _make_vector_point(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    ax.plot([1.2, 1.2], [1.0, 5.0], color=p["ghost"], lw=1.1)
    ax.plot([1.2, 8.8], [1.0, 1.0], color=p["ghost"], lw=1.1)
    ax.annotate(
        "",
        xy=(1.2, 5.0),
        xytext=(1.2, 1.0),
        arrowprops=dict(arrowstyle="-|>", lw=1.1, color=p["ghost"]),
    )
    ax.annotate(
        "",
        xy=(8.8, 1.0),
        xytext=(1.2, 1.0),
        arrowprops=dict(arrowstyle="-|>", lw=1.1, color=p["ghost"]),
    )
    ax.annotate(
        "",
        xy=(7.3, 4.2),
        xytext=(1.4, 1.2),
        arrowprops=dict(arrowstyle="-|>", lw=2.2, color=p["accent"]),
    )
    ax.add_patch(
        mpatches.Circle((7.3, 4.2), 0.20, edgecolor=p["fg"], facecolor=p["accent"], lw=1.0)
    )
    ax.text(7.75, 4.45, "x", fontsize=10, color=p["fg"], fontfamily=FORMULA_FONT)
    return _save(fig, path)


def _make_plane_slice(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    ax.plot([1.2, 8.7], [1.0, 5.0], color=p["fg"], lw=2.0)
    ax.annotate(
        "",
        xy=(4.7, 4.4),
        xytext=(5.8, 2.5),
        arrowprops=dict(arrowstyle="-|>", lw=2.0, color=p["accent"]),
    )
    ax.scatter([2.2, 3.0], [4.5, 3.8], s=42, facecolors="none", edgecolors=[p["accent"]], linewidths=1.5)
    ax.scatter([6.8, 7.6], [2.2, 1.5], s=46, marker="x", color=[p["soft"]], linewidths=1.8)
    return _save(fig, path)


def _make_loss_curve(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    x = np.linspace(1.2, 8.8, 300)
    y = 0.18 * (x - 5.4) ** 2 + 1.3
    ax.plot(x, y, color=p["fg"], lw=2.0)
    ax.annotate(
        "",
        xy=(5.45, 1.45),
        xytext=(2.8, 4.5),
        arrowprops=dict(arrowstyle="-|>", lw=2.2, color=p["accent"]),
    )
    ax.add_patch(
        mpatches.Circle((5.45, 1.45), 0.15, edgecolor=p["fg"], facecolor=p["accent"], lw=1.0)
    )
    return _save(fig, path)


def _make_scatter_boundary(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    pos = np.array([[2.1, 4.3], [3.0, 3.7], [4.0, 4.5]])
    neg = np.array([[6.3, 1.8], [7.0, 2.7], [8.0, 1.6]])
    ax.scatter(pos[:, 0], pos[:, 1], s=44, facecolors="none", edgecolors=[p["accent"]], linewidths=1.6)
    ax.scatter(neg[:, 0], neg[:, 1], s=48, marker="x", color=[p["soft"]], linewidths=1.9)
    ax.plot([4.7, 7.6], [5.2, 0.9], color=p["fg"], lw=1.8)
    ax.text(2.3, 4.95, "+1", fontsize=10, color=p["accent"], fontfamily=FORMULA_FONT)
    ax.text(7.55, 0.95, "-1", fontsize=10, color=p["soft"], fontfamily=FORMULA_FONT)
    return _save(fig, path)


def _make_gaussian(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    x = np.linspace(-3, 3, 300)
    y = np.exp(-(x**2) / 2)
    xx = 1.2 + (x + 3) / 6 * 7.4
    yy = 1.1 + y / y.max() * 3.4
    ax.plot(xx, yy, color=p["fg"], lw=2.0)
    ax.plot([5.0, 5.0], [1.1, 4.55], color=p["ghost"], lw=1.1, linestyle="--")
    return _save(fig, path)


def _make_array_glyph(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    ax.text(
        5.0,
        3.0,
        "[1, 0, 1]\n[0, 1, 1]",
        ha="center",
        va="center",
        fontsize=14,
        color=p["fg"],
        fontfamily="DejaVu Sans Mono",
    )
    return _save(fig, path)


def _make_movie_to_vector(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    _movie_icon(ax, 0.8, 1.4, 2.7, 3.1, p)
    ax.annotate(
        "",
        xy=(6.0, 3.0),
        xytext=(3.8, 3.0),
        arrowprops=dict(arrowstyle="-|>", lw=2.0, color=p["accent"]),
    )
    _vector_strip(ax, 6.2, 2.35, 3.1, 1.25, p, ["1", "0", "1", "1", "0"])
    return _save(fig, path)


def _make_raw_object_pair(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    _movie_icon(ax, 0.9, 1.4, 3.0, 3.0, p)
    _digit_card(ax, 6.0, 1.4, 2.5, 3.0, p, digit="7")
    ax.plot([5.0, 5.0], [1.2, 4.8], color=p["ghost"], lw=1.1)
    return _save(fig, path)


def _make_feature_vector_pair(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    _vector_strip(ax, 1.0, 3.3, 4.8, 1.0, p, ["1", "0", "1", "1", "0"])
    _vector_strip(ax, 2.4, 1.5, 4.0, 1.0, p, ["x", "x", "x", "x"])
    ax.text(7.0, 1.95, "[brightness, width]", fontsize=9, color=p["soft"], fontfamily=FORMULA_FONT)
    return _save(fig, path)


def _make_digit_to_label(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    _digit_card(ax, 0.9, 1.4, 2.6, 3.0, p, digit="7")
    ax.annotate(
        "",
        xy=(6.0, 3.0),
        xytext=(3.9, 3.0),
        arrowprops=dict(arrowstyle="-|>", lw=2.0, color=p["accent"]),
    )
    label_box = mpatches.FancyBboxPatch(
        (6.3, 2.15),
        2.6,
        1.7,
        boxstyle="round,pad=0.02,rounding_size=0.18",
        linewidth=1.3,
        edgecolor=p["fg"],
        facecolor=(0, 0, 0, 0),
    )
    ax.add_patch(label_box)
    ax.text(7.6, 3.0, "class = 7", ha="center", va="center", fontsize=11, color=p["fg"], fontfamily=FORMULA_FONT)
    return _save(fig, path)


def _make_prediction_error(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    pred = mpatches.FancyBboxPatch(
        (1.0, 2.1),
        2.5,
        1.4,
        boxstyle="round,pad=0.02,rounding_size=0.16",
        linewidth=1.3,
        edgecolor=p["fg"],
        facecolor=(0, 0, 0, 0),
    )
    truth = mpatches.FancyBboxPatch(
        (6.0, 2.1),
        2.5,
        1.4,
        boxstyle="round,pad=0.02,rounding_size=0.16",
        linewidth=1.3,
        edgecolor=p["fg"],
        facecolor=(0, 0, 0, 0),
    )
    ax.add_patch(pred)
    ax.add_patch(truth)
    ax.text(2.25, 2.8, "ŷ = like", ha="center", va="center", fontsize=12, color=p["accent"], fontfamily=FORMULA_FONT)
    ax.text(7.25, 2.8, "y = like", ha="center", va="center", fontsize=12, color=p["fg"], fontfamily=FORMULA_FONT)
    ax.annotate(
        "",
        xy=(5.45, 2.8),
        xytext=(3.75, 2.8),
        arrowprops=dict(arrowstyle="-|>", lw=1.9, color=p["accent"]),
    )
    ax.text(5.05, 3.25, "compare", ha="center", va="center", fontsize=9, color=p["soft"], fontfamily=BODY_FONT)
    ax.text(5.0, 1.4, "L(θ)", ha="center", va="center", fontsize=12, color=p["fg"], fontfamily=FORMULA_FONT)
    return _save(fig, path)


DRAWERS: dict[str, Callable[[Path, dict], Path]] = {
    "vector_arrow": _make_vector_point,
    "point_in_space": _make_vector_point,
    "plane_slice": _make_plane_slice,
    "line_to_boundary": _make_plane_slice,
    "loss_curve": _make_loss_curve,
    "scatter_boundary": _make_scatter_boundary,
    "gaussian_curve": _make_gaussian,
    "array_glyph": _make_array_glyph,
    "movie_to_vector": _make_movie_to_vector,
    "raw_object_pair": _make_raw_object_pair,
    "feature_vector_pair": _make_feature_vector_pair,
    "digit_to_label": _make_digit_to_label,
    "prediction_error": _make_prediction_error,
}

ALIASES = {
    "vector_point_plane_combo": "vector_arrow",
    "plane_slice_with_normal": "plane_slice",
    "loss_curve_with_descent_arrow": "loss_curve",
    "bowl_surface_with_downhill_arrow": "loss_curve",
    "scatter_with_boundary_and_classes": "scatter_boundary",
    "scatter_separator": "scatter_boundary",
    "array_or_code_brackets": "array_glyph",
    "decision_boundary": "scatter_boundary",
    "uncertainty_curve": "gaussian_curve",
    "feature_vector_strip": "feature_vector_pair",
}


def _render_visual(kind: str, suffix: str, variant: str) -> Path:
    canonical = ALIASES.get(kind, kind)
    if canonical not in DRAWERS:
        raise KeyError(f"Unknown mini visual kind: {kind}")
    palette = PALETTES.get(variant, PALETTES["dark_on_light"])
    safe_name = canonical.replace("/", "_").replace(" ", "_")
    path = GENERATED_DIR / f"{safe_name}_{variant}{suffix}.png"
    return DRAWERS[canonical](path, palette)


def add_mini_visual(
    slide,
    kind: str,
    x: float,
    y: float,
    w: float,
    h: float,
    suffix: str = "",
    variant: str = "dark_on_light",
) -> None:
    if not kind:
        return
    try:
        img = _render_visual(kind, suffix=suffix, variant=variant)
        add_image(slide, img, x, y, w, h)
    except Exception:
        add_textbox(
            slide,
            x=x,
            y=y,
            w=w,
            h=h,
            text=kind,
            font_name=FORMULA_FONT,
            font_size=10,
            color=SLATE if variant == "dark_on_light" else OFFWHITE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )


def add_visual_with_caption(
    slide,
    kind: str,
    x: float,
    y: float,
    w: float,
    h: float,
    caption: str = "",
    suffix: str = "",
    variant: str = "dark_on_light",
    caption_font_size: int = 9,
) -> None:
    if not caption:
        add_mini_visual(slide, kind=kind, x=x, y=y, w=w, h=h, suffix=suffix, variant=variant)
        return

    visual_h = max(0.1, h - 0.20)
    add_mini_visual(slide, kind=kind, x=x, y=y, w=w, h=visual_h, suffix=suffix, variant=variant)

    add_textbox(
        slide,
        x=x,
        y=y + visual_h + 0.02,
        w=w,
        h=0.18,
        text=caption,
        font_name=BODY_FONT,
        font_size=caption_font_size,
        color=SLATE if variant == "dark_on_light" else OFFWHITE,
        bold=False,
        align=PP_ALIGN.CENTER,
    )
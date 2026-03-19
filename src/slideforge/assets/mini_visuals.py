from __future__ import annotations

from pathlib import Path
from typing import Callable

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
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


# Use Matplotlib-safe fonts for generated PNG assets.
# PowerPoint text can still use the repo's Calibri/Cambria choices.
MPL_BODY_FONT = "DejaVu Sans"
MPL_FORMULA_FONT = "DejaVu Sans Mono"


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
    },
    "light_on_dark": {
        "fg": _mpl(OFFWHITE),
        "soft": _mpl(TITLE_PANEL_LINE),
        "accent": _mpl(TITLE_PANEL_LINE),
        "ghost": _mpl(GHOST_TEXT),
        "bg_soft": (1.0, 1.0, 1.0, 0.08),
        "bg_alt": (1.0, 1.0, 1.0, 0.05),
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


def _canvas(path: Path, figsize: tuple[float, float] = (4.0, 2.2)):
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


def _rounded_box(ax, x: float, y: float, w: float, h: float, p, *, lw: float = 1.3) -> None:
    ax.add_patch(
        mpatches.FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.18",
            linewidth=lw,
            edgecolor=p["fg"],
            facecolor=(0, 0, 0, 0),
        )
    )


def _movie_icon(ax, x: float, y: float, w: float, h: float, p) -> None:
    _rounded_box(ax, x, y, w, h, p, lw=1.5)
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
    _rounded_box(ax, x, y, w, h, p, lw=1.5)
    ax.text(
        x + w / 2,
        y + h / 2,
        digit,
        ha="center",
        va="center",
        fontsize=20,
        color=p["accent"],
        fontfamily=MPL_FORMULA_FONT,
    )


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
        ax.text(
            cell_x + cell_w / 2,
            y + h / 2,
            v,
            ha="center",
            va="center",
            fontsize=10,
            color=txt_color,
            fontfamily=MPL_FORMULA_FONT,
        )
        if labels and i < len(labels):
            ax.text(
                cell_x + cell_w / 2,
                y - 0.16,
                labels[i],
                ha="center",
                va="top",
                fontsize=6.8,
                color=p["soft"],
                fontfamily=MPL_BODY_FONT,
            )


def _axes_2d(ax, p) -> None:
    ax.plot([1.0, 1.0], [0.9, 5.1], color=p["ghost"], lw=1.0)
    ax.plot([1.0, 9.0], [0.9, 0.9], color=p["ghost"], lw=1.0)
    ax.annotate(
        "",
        xy=(1.0, 5.1),
        xytext=(1.0, 0.9),
        arrowprops=dict(arrowstyle="-|>", lw=1.0, color=p["ghost"]),
    )
    ax.annotate(
        "",
        xy=(9.0, 0.9),
        xytext=(1.0, 0.9),
        arrowprops=dict(arrowstyle="-|>", lw=1.0, color=p["ghost"]),
    )


def _draw_checkmark(ax, cx: float, cy: float, size: float, color, *, lw: float = 2.2) -> None:
    """
    Draw a checkmark with line segments instead of relying on a Unicode glyph.
    This avoids missing-glyph warnings from Matplotlib font resolution.
    """
    x1 = cx - size * 0.40
    y1 = cy - size * 0.02
    x2 = cx - size * 0.10
    y2 = cy - size * 0.28
    x3 = cx + size * 0.42
    y3 = cy + size * 0.28
    ax.plot([x1, x2], [y1, y2], color=color, lw=lw, solid_capstyle="round")
    ax.plot([x2, x3], [y2, y3], color=color, lw=lw, solid_capstyle="round")


def _make_point_in_space(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    _axes_2d(ax, p)
    ax.add_patch(mpatches.Circle((6.8, 4.0), 0.20, edgecolor=p["fg"], facecolor=p["accent"], lw=1.2))
    ax.text(7.15, 4.20, "x", fontsize=10, color=p["fg"], fontfamily=MPL_FORMULA_FONT)
    ax.plot([6.8, 6.8], [0.9, 4.0], color=p["ghost"], lw=0.9, linestyle="--")
    ax.plot([1.0, 6.8], [4.0, 4.0], color=p["ghost"], lw=0.9, linestyle="--")
    return _save(fig, path)


def _make_vector_arrow(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    _axes_2d(ax, p)
    ax.annotate(
        "",
        xy=(7.2, 4.1),
        xytext=(1.2, 1.1),
        arrowprops=dict(arrowstyle="-|>", lw=2.3, color=p["accent"]),
    )
    ax.text(7.45, 4.28, "x", fontsize=10, color=p["fg"], fontfamily=MPL_FORMULA_FONT)
    return _save(fig, path)


def _make_plane_slice(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    ax.add_patch(
        mpatches.Polygon(
            [(0.8, 5.7), (5.8, 5.7), (3.9, 0.5), (0.8, 0.5)],
            closed=True,
            facecolor=p["bg_soft"],
            edgecolor="none",
        )
    )
    ax.add_patch(
        mpatches.Polygon(
            [(5.8, 5.7), (9.2, 5.7), (9.2, 0.5), (3.9, 0.5)],
            closed=True,
            facecolor=p["bg_alt"],
            edgecolor="none",
        )
    )
    ax.plot([3.5, 6.7], [0.8, 5.2], color=p["fg"], lw=2.0)
    ax.annotate(
        "",
        xy=(5.4, 4.3),
        xytext=(6.25, 2.8),
        arrowprops=dict(arrowstyle="-|>", lw=2.0, color=p["accent"]),
    )
    pos = np.array([[1.8, 4.6], [2.6, 3.8], [3.0, 4.8]])
    neg = np.array([[7.1, 1.7], [7.8, 2.6], [8.5, 1.4]])
    ax.scatter(pos[:, 0], pos[:, 1], s=42, facecolors="none", edgecolors=[p["accent"]], linewidths=1.6)
    ax.scatter(neg[:, 0], neg[:, 1], s=46, marker="x", color=[p["soft"]], linewidths=1.8)
    return _save(fig, path)


def _make_loss_curve(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    xx = np.linspace(1.0, 9.0, 200)
    yy = np.linspace(0.8, 5.2, 160)
    X, Y = np.meshgrid(xx, yy)
    Z = ((X - 5.5) / 2.2) ** 2 + ((Y - 2.2) / 1.15) ** 2
    ax.contour(X, Y, Z, levels=[0.6, 1.2, 2.0, 3.0, 4.3], colors=[p["ghost"]], linewidths=1.0)

    path_pts = np.array([[2.5, 4.4], [3.4, 3.5], [4.3, 2.9], [5.0, 2.45], [5.45, 2.2]])
    ax.plot(path_pts[:, 0], path_pts[:, 1], color=p["accent"], lw=2.0)
    for i in range(len(path_pts) - 1):
        ax.annotate(
            "",
            xy=tuple(path_pts[i + 1]),
            xytext=tuple(path_pts[i]),
            arrowprops=dict(arrowstyle="-|>", lw=1.8, color=p["accent"]),
        )
    ax.add_patch(mpatches.Circle((5.45, 2.2), 0.14, edgecolor=p["fg"], facecolor=p["accent"], lw=1.0))
    ax.text(2.20, 4.78, "current", fontsize=8, color=p["soft"], fontfamily=MPL_BODY_FONT)
    ax.text(5.65, 1.85, "lower loss", fontsize=8, color=p["fg"], fontfamily=MPL_BODY_FONT)
    return _save(fig, path)


def _make_scatter_boundary(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    ax.add_patch(
        mpatches.Polygon(
            [(0.8, 5.6), (5.2, 5.6), (6.9, 0.6), (0.8, 0.6)],
            closed=True,
            facecolor=p["bg_soft"],
            edgecolor="none",
        )
    )
    ax.add_patch(
        mpatches.Polygon(
            [(5.2, 5.6), (9.2, 5.6), (9.2, 0.6), (6.9, 0.6)],
            closed=True,
            facecolor=p["bg_alt"],
            edgecolor="none",
        )
    )
    pos = np.array([[2.0, 4.4], [2.8, 3.8], [3.7, 4.7]])
    neg = np.array([[6.9, 1.7], [7.5, 2.6], [8.2, 1.5]])
    ax.scatter(pos[:, 0], pos[:, 1], s=46, facecolors="none", edgecolors=[p["accent"]], linewidths=1.7)
    ax.scatter(neg[:, 0], neg[:, 1], s=50, marker="x", color=[p["soft"]], linewidths=1.9)
    ax.plot([4.9, 7.0], [5.2, 0.9], color=p["fg"], lw=1.9)
    ax.text(1.8, 5.0, "+1 region", fontsize=8, color=p["accent"], fontfamily=MPL_BODY_FONT)
    ax.text(6.8, 0.9, "−1 region", fontsize=8, color=p["soft"], fontfamily=MPL_BODY_FONT)
    return _save(fig, path)


def _make_gaussian(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    x = np.linspace(-3, 3, 300)
    y = np.exp(-(x**2) / 2)
    xx = 1.1 + (x + 3) / 6 * 7.8
    yy = 1.1 + y / y.max() * 3.3
    ax.fill_between(xx, 1.1, yy, color=p["bg_soft"])
    ax.plot(xx, yy, color=p["fg"], lw=2.0)
    ax.plot([5.0, 5.0], [1.1, 4.5], color=p["fg"], lw=1.3, linestyle="--")
    ax.plot([3.7, 6.3], [1.55, 1.55], color=p["soft"], lw=2.0)
    ax.text(5.08, 4.35, "μ", fontsize=10, color=p["fg"], fontfamily=MPL_FORMULA_FONT)
    ax.text(4.75, 1.77, "spread", fontsize=8, color=p["soft"], fontfamily=MPL_BODY_FONT)
    return _save(fig, path)


def _make_array_glyph(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    _movie_icon(ax, 0.8, 1.55, 2.2, 2.7, p)
    ax.text(1.9, 1.10, "object", ha="center", va="center", fontsize=8, color=p["soft"], fontfamily=MPL_BODY_FONT)
    ax.annotate(
        "",
        xy=(5.2, 3.0),
        xytext=(3.25, 3.0),
        arrowprops=dict(arrowstyle="-|>", lw=1.9, color=p["accent"]),
    )

    ax.text(6.3, 4.0, "[1, 0, 1]", ha="center", va="center", fontsize=12, color=p["fg"], fontfamily=MPL_FORMULA_FONT)
    ax.text(6.3, 2.8, "[0, 1, 1]", ha="center", va="center", fontsize=12, color=p["fg"], fontfamily=MPL_FORMULA_FONT)
    ax.text(6.3, 1.6, "NumPy array / matrix", ha="center", va="center", fontsize=8.5, color=p["soft"], fontfamily=MPL_BODY_FONT)
    return _save(fig, path)


def _make_movie_card(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    _movie_icon(ax, 2.4, 1.35, 5.2, 3.25, p)
    ax.text(5.0, 1.00, "movie object", ha="center", va="center", fontsize=8.5, color=p["soft"], fontfamily=MPL_BODY_FONT)
    return _save(fig, path)


def _make_digit_card(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    _digit_card_shape(ax, 3.0, 1.2, 4.0, 3.6, p, digit="7")
    ax.text(5.0, 0.95, "digit image", ha="center", va="center", fontsize=8.5, color=p["soft"], fontfamily=MPL_BODY_FONT)
    return _save(fig, path)


def _make_movie_to_vector(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    _movie_icon(ax, 0.8, 1.55, 2.3, 2.7, p)
    ax.text(1.95, 1.12, "movie", ha="center", va="center", fontsize=8.5, color=p["soft"], fontfamily=MPL_BODY_FONT)
    ax.annotate(
        "",
        xy=(5.0, 3.0),
        xytext=(3.35, 3.0),
        arrowprops=dict(arrowstyle="-|>", lw=1.9, color=p["accent"]),
    )
    _vector_strip(
        ax,
        5.3,
        2.45,
        3.8,
        0.95,
        p,
        ["1", "0", "1", "1", "0"],
        labels=["act", "com", "rom", "long", "anim"],
    )
    ax.text(7.2, 4.25, "selected features", ha="center", va="center", fontsize=8.0, color=p["soft"], fontfamily=MPL_BODY_FONT)
    return _save(fig, path)


def _make_raw_object_pair(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    _movie_icon(ax, 0.9, 1.4, 3.0, 3.0, p)
    _digit_card_shape(ax, 6.0, 1.4, 2.5, 3.0, p, digit="7")
    ax.plot([5.0, 5.0], [1.1, 4.8], color=p["ghost"], lw=1.0)
    ax.text(2.4, 1.02, "movie", fontsize=8.3, color=p["soft"], fontfamily=MPL_BODY_FONT, ha="center")
    ax.text(7.25, 1.02, "digit", fontsize=8.3, color=p["soft"], fontfamily=MPL_BODY_FONT, ha="center")
    return _save(fig, path)


def _make_feature_vector_pair(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    _vector_strip(
        ax,
        1.0,
        3.35,
        4.8,
        0.95,
        p,
        ["1", "0", "1", "1", "0"],
        labels=["act", "com", "rom", "long", "anim"],
    )
    _vector_strip(
        ax,
        2.2,
        1.45,
        4.6,
        0.95,
        p,
        ["x", "x"],
        labels=["brightness", "width"],
    )
    ax.text(7.5, 1.92, "image features", fontsize=8.3, color=p["soft"], fontfamily=MPL_BODY_FONT)
    return _save(fig, path)


def _make_digit_to_label(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    _digit_card_shape(ax, 0.9, 1.4, 2.6, 3.0, p, digit="7")
    ax.annotate(
        "",
        xy=(6.0, 3.0),
        xytext=(3.9, 3.0),
        arrowprops=dict(arrowstyle="-|>", lw=1.9, color=p["accent"]),
    )
    _rounded_box(ax, 6.2, 2.1, 2.8, 1.8, p, lw=1.3)
    ax.text(7.6, 3.02, "class = 7", ha="center", va="center", fontsize=11.5, color=p["fg"], fontfamily=MPL_FORMULA_FONT)
    return _save(fig, path)


def _make_prediction_error(path: Path, p) -> Path:
    fig, ax = _canvas(path)
    _rounded_box(ax, 0.9, 2.0, 2.8, 1.5, p, lw=1.3)
    _rounded_box(ax, 6.3, 2.0, 2.8, 1.5, p, lw=1.3)
    ax.text(2.3, 2.95, "prediction", ha="center", va="center", fontsize=8.2, color=p["soft"], fontfamily=MPL_BODY_FONT)
    ax.text(2.3, 2.52, "ŷ = like", ha="center", va="center", fontsize=11.5, color=p["accent"], fontfamily=MPL_FORMULA_FONT)
    ax.text(7.7, 2.95, "truth", ha="center", va="center", fontsize=8.2, color=p["soft"], fontfamily=MPL_BODY_FONT)
    ax.text(7.7, 2.52, "y = like", ha="center", va="center", fontsize=11.5, color=p["fg"], fontfamily=MPL_FORMULA_FONT)
    ax.annotate(
        "",
        xy=(6.0, 2.75),
        xytext=(3.95, 2.75),
        arrowprops=dict(arrowstyle="-|>", lw=1.8, color=p["accent"]),
    )
    ax.text(5.0, 3.15, "compare", ha="center", va="center", fontsize=8.2, color=p["soft"], fontfamily=MPL_BODY_FONT)

    ax.add_patch(mpatches.Circle((5.0, 1.55), 0.24, edgecolor=p["fg"], facecolor=p["bg_soft"], lw=1.2))
    _draw_checkmark(ax, 5.0, 1.55, 0.42, p["accent"], lw=2.1)
    ax.text(5.0, 1.02, "agreement / loss check", ha="center", va="center", fontsize=8.0, color=p["soft"], fontfamily=MPL_BODY_FONT)
    return _save(fig, path)


DRAWERS: dict[str, Callable[[Path, dict], Path]] = {
    "point_in_space": _make_point_in_space,
    "vector_arrow": _make_vector_arrow,
    "plane_slice": _make_plane_slice,
    "line_to_boundary": _make_plane_slice,
    "loss_curve": _make_loss_curve,
    "scatter_boundary": _make_scatter_boundary,
    "gaussian_curve": _make_gaussian,
    "array_glyph": _make_array_glyph,
    "movie_card": _make_movie_card,
    "digit_card": _make_digit_card,
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
    "movie_icon": "movie_card",
    "digit_image": "digit_card",
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

    visual_h = max(0.1, h - 0.22)
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
from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches
import numpy as np

from slideforge.assets.mini_visuals_common import (
    _axes_2d,
    _canvas,
    _digit_card_shape,
    _draw_checkmark,
    _label_text,
    _movie_icon,
    _rounded_box,
    _save,
    _soft_panel,
    _vector_arrow,
    _vector_strip,
    palette_for,
)


def _make_point_in_space(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)
    _axes_2d(ax, p)
    ax.add_patch(mpatches.Circle((6.8, 4.0), 0.20, edgecolor=p["fg"], facecolor=p["accent"], lw=1.2))
    _label_text(ax, 7.15, 4.20, "x", p, size=10, formula=True, ha="left")
    ax.plot([6.8, 6.8], [0.9, 4.0], color=p["ghost"], lw=0.9, linestyle="--")
    ax.plot([1.0, 6.8], [4.0, 4.0], color=p["ghost"], lw=0.9, linestyle="--")
    return _save(fig, path)


def _make_vector_arrow(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)
    _axes_2d(ax, p)
    _vector_arrow(ax, (1.2, 1.1), (7.2, 4.1), p, label="x")
    return _save(fig, path)


def _make_plane_slice(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)
    ax.add_patch(mpatches.Polygon([(0.8, 5.7), (5.8, 5.7), (3.9, 0.5), (0.8, 0.5)], closed=True, facecolor=p["bg_soft"], edgecolor="none"))
    ax.add_patch(mpatches.Polygon([(5.8, 5.7), (9.2, 5.7), (9.2, 0.5), (3.9, 0.5)], closed=True, facecolor=p["bg_alt"], edgecolor="none"))
    ax.plot([3.5, 6.7], [0.8, 5.2], color=p["fg"], lw=2.0)
    _vector_arrow(ax, (6.25, 2.8), (5.4, 4.3), p, color=p["accent"], lw=2.0)
    pos = np.array([[1.8, 4.6], [2.6, 3.8], [3.0, 4.8]])
    neg = np.array([[7.1, 1.7], [7.8, 2.6], [8.5, 1.4]])
    ax.scatter(pos[:, 0], pos[:, 1], s=42, facecolors="none", edgecolors=[p["accent"]], linewidths=1.6)
    ax.scatter(neg[:, 0], neg[:, 1], s=46, marker="x", color=[p["soft"]], linewidths=1.8)
    return _save(fig, path)


def _make_loss_curve(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)
    xx = np.linspace(1.0, 9.0, 200)
    yy = np.linspace(0.8, 5.2, 160)
    X, Y = np.meshgrid(xx, yy)
    Z = ((X - 5.5) / 2.2) ** 2 + ((Y - 2.2) / 1.15) ** 2
    ax.contour(X, Y, Z, levels=[0.6, 1.2, 2.0, 3.0, 4.3], colors=[p["ghost"]], linewidths=1.0)
    path_pts = np.array([[2.5, 4.4], [3.4, 3.5], [4.3, 2.9], [5.0, 2.45], [5.45, 2.2]])
    ax.plot(path_pts[:, 0], path_pts[:, 1], color=p["accent"], lw=2.0)
    for i in range(len(path_pts) - 1):
        _vector_arrow(ax, tuple(path_pts[i]), tuple(path_pts[i + 1]), p, color=p["accent"], lw=1.8)
    ax.add_patch(mpatches.Circle((5.45, 2.2), 0.14, edgecolor=p["fg"], facecolor=p["accent"], lw=1.0))
    _label_text(ax, 2.20, 4.78, "current", p, size=8, ha="left", color=p["soft"])
    _label_text(ax, 5.65, 1.85, "lower loss", p, size=8, ha="left")
    return _save(fig, path)


def _make_scatter_boundary(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)
    ax.add_patch(mpatches.Polygon([(0.8, 5.6), (5.2, 5.6), (6.9, 0.6), (0.8, 0.6)], closed=True, facecolor=p["bg_soft"], edgecolor="none"))
    ax.add_patch(mpatches.Polygon([(5.2, 5.6), (9.2, 5.6), (9.2, 0.6), (6.9, 0.6)], closed=True, facecolor=p["bg_alt"], edgecolor="none"))
    pos = np.array([[2.0, 4.4], [2.8, 3.8], [3.7, 4.7]])
    neg = np.array([[6.9, 1.7], [7.5, 2.6], [8.2, 1.5]])
    ax.scatter(pos[:, 0], pos[:, 1], s=46, facecolors="none", edgecolors=[p["accent"]], linewidths=1.7)
    ax.scatter(neg[:, 0], neg[:, 1], s=50, marker="x", color=[p["soft"]], linewidths=1.9)
    ax.plot([4.9, 7.0], [5.2, 0.9], color=p["fg"], lw=1.9)
    _label_text(ax, 1.8, 5.0, "+1 region", p, size=8, ha="left", color=p["accent"])
    _label_text(ax, 6.8, 0.9, "−1 region", p, size=8, ha="left", color=p["soft"])
    return _save(fig, path)


def _make_gaussian(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)
    x = np.linspace(-3, 3, 300)
    y = np.exp(-(x**2) / 2)
    xx = 1.1 + (x + 3) / 6 * 7.8
    yy = 1.1 + y / y.max() * 3.3
    ax.fill_between(xx, 1.1, yy, color=p["bg_soft"])
    ax.plot(xx, yy, color=p["fg"], lw=2.0)
    ax.plot([5.0, 5.0], [1.1, 4.5], color=p["fg"], lw=1.3, linestyle="--")
    ax.plot([3.7, 6.3], [1.55, 1.55], color=p["soft"], lw=2.0)
    _label_text(ax, 5.08, 4.35, "μ", p, size=10, formula=True)
    _label_text(ax, 4.75, 1.77, "spread", p, size=8, color=p["soft"])
    return _save(fig, path)


def _make_array_glyph(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)
    _movie_icon(ax, 0.8, 1.55, 2.2, 2.7, p)
    _label_text(ax, 1.9, 1.10, "object", p, size=8, color=p["soft"])
    _vector_arrow(ax, (3.25, 3.0), (5.2, 3.0), p, color=p["accent"], lw=1.9)
    _label_text(ax, 6.3, 4.0, "[1, 0, 1]", p, size=12, formula=True)
    _label_text(ax, 6.3, 2.8, "[0, 1, 1]", p, size=12, formula=True)
    _label_text(ax, 6.3, 1.6, "NumPy array / matrix", p, size=8.5, color=p["soft"])
    return _save(fig, path)


def _make_movie_card(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)
    _movie_icon(ax, 2.4, 1.35, 5.2, 3.25, p)
    _label_text(ax, 5.0, 1.00, "movie object", p, size=8.5, color=p["soft"])
    return _save(fig, path)


def _make_digit_card(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)
    _digit_card_shape(ax, 3.0, 1.2, 4.0, 3.6, p, digit="7")
    _label_text(ax, 5.0, 0.95, "digit image", p, size=8.5, color=p["soft"])
    return _save(fig, path)


def _make_movie_to_vector(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)
    _movie_icon(ax, 0.8, 1.55, 2.3, 2.7, p)
    _label_text(ax, 1.95, 1.12, "movie", p, size=8.5, color=p["soft"])
    _vector_arrow(ax, (3.35, 3.0), (5.0, 3.0), p, color=p["accent"], lw=1.9)
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
    _label_text(ax, 7.2, 4.25, "selected features", p, size=8.0, color=p["soft"])
    return _save(fig, path)


def _make_raw_object_pair(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)
    _movie_icon(ax, 0.9, 1.4, 3.0, 3.0, p)
    _digit_card_shape(ax, 6.0, 1.4, 2.5, 3.0, p, digit="7")
    ax.plot([5.0, 5.0], [1.1, 4.8], color=p["ghost"], lw=1.0)
    _label_text(ax, 2.4, 1.02, "movie", p, size=8.3, color=p["soft"])
    _label_text(ax, 7.25, 1.02, "digit", p, size=8.3, color=p["soft"])
    return _save(fig, path)


def _make_feature_vector_pair(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)
    _vector_strip(ax, 1.0, 3.35, 4.8, 0.95, p, ["1", "0", "1", "1", "0"], labels=["act", "com", "rom", "long", "anim"])
    _vector_strip(ax, 2.2, 1.45, 4.6, 0.95, p, ["x", "x"], labels=["brightness", "width"])
    _label_text(ax, 7.5, 1.92, "image features", p, size=8.3, ha="left", color=p["soft"])
    return _save(fig, path)


def _make_digit_to_label(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)
    _digit_card_shape(ax, 0.9, 1.4, 2.6, 3.0, p, digit="7")
    _vector_arrow(ax, (3.9, 3.0), (6.0, 3.0), p, color=p["accent"], lw=1.9)
    _rounded_box(ax, 6.2, 2.1, 2.8, 1.8, p, lw=1.3, fill=(0, 0, 0, 0))
    _label_text(ax, 7.6, 3.02, "class = 7", p, size=11.5, formula=True)
    return _save(fig, path)


def _make_prediction_error(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)
    _rounded_box(ax, 0.9, 2.0, 2.8, 1.5, p, lw=1.3, fill=(0, 0, 0, 0))
    _rounded_box(ax, 6.3, 2.0, 2.8, 1.5, p, lw=1.3, fill=(0, 0, 0, 0))
    _label_text(ax, 2.3, 2.95, "prediction", p, size=8.2, color=p["soft"])
    _label_text(ax, 2.3, 2.52, "ŷ = like", p, size=11.5, formula=True, color=p["accent"])
    _label_text(ax, 7.7, 2.95, "truth", p, size=8.2, color=p["soft"])
    _label_text(ax, 7.7, 2.52, "y = like", p, size=11.5, formula=True)
    _vector_arrow(ax, (3.95, 2.75), (6.0, 2.75), p, color=p["accent"], lw=1.8)
    _label_text(ax, 5.0, 3.15, "compare", p, size=8.2, color=p["soft"])
    ax.add_patch(mpatches.Circle((5.0, 1.55), 0.24, edgecolor=p["fg"], facecolor=p["bg_soft"], lw=1.2))
    _draw_checkmark(ax, 5.0, 1.55, 0.42, p["accent"], lw=2.1)
    _label_text(ax, 5.0, 1.02, "agreement / loss check", p, size=8.0, color=p["soft"])
    return _save(fig, path)


DRAWERS_CORE = {
    "point_in_space": _make_point_in_space,
    "vector_arrow": _make_vector_arrow,
    "plane_slice": _make_plane_slice,
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

ALIASES_CORE = {
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
    "line_to_boundary": "plane_slice",
}
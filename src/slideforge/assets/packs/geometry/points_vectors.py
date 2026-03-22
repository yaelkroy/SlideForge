from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches

from slideforge.assets.mini_visuals_common import _canvas, _clean_origin_axes, _label_text, _mini_panel, _save, _vector_arrow, _axes_2d, palette_for


def _make_point_and_vector_same_coords(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.9, 2.8))
    _mini_panel(ax, 0.75, 0.92, 8.55, 4.28, p)
    ax.plot([1.65, 1.65], [1.45, 4.55], color=p["ghost"], lw=0.9)
    ax.plot([1.65, 4.70], [1.45, 1.45], color=p["ghost"], lw=0.9)
    ax.plot([3.55, 3.55], [1.45, 3.42], color=p["ghost"], lw=0.9, linestyle="--")
    ax.plot([1.65, 3.55], [3.42, 3.42], color=p["ghost"], lw=0.9, linestyle="--")
    ax.add_patch(mpatches.Circle((3.55, 3.42), 0.17, edgecolor=p["fg"], facecolor=p["accent"], lw=1.1))
    _label_text(ax, 2.70, 4.76, "point view", p, size=8.3, color=p["soft"])
    _label_text(ax, 3.54, 1.20, "x", p, size=8.7, formula=True)
    ax.plot([6.00, 6.00], [1.60, 4.45], color=p["ghost"], lw=0.9)
    ax.plot([6.00, 8.74], [1.60, 1.60], color=p["ghost"], lw=0.9)
    _vector_arrow(ax, (6.00, 1.60), (8.42, 4.02), p, color=p["accent"], lw=2.35, label="x")
    _label_text(ax, 7.35, 4.76, "vector view", p, size=8.3, color=p["soft"])
    _label_text(ax, 4.98, 3.02, "same coordinates", p, size=8.2, color=p["fg"])
    ax.plot([4.50, 5.22], [3.02, 3.02], color=p["accent"], lw=1.6)
    return _save(fig, path)


def _make_vector_difference_geometry(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)
    _axes_2d(ax, p)
    origin = (1.3, 1.1)
    a_tip = (4.0, 2.5)
    b_tip = (7.1, 4.0)
    _vector_arrow(ax, origin, a_tip, p, color=p["soft"], lw=2.1, label="A")
    _vector_arrow(ax, origin, b_tip, p, color=p["accent"], lw=2.4, label="B")
    _vector_arrow(ax, a_tip, b_tip, p, color=p["fg"], lw=2.2, label="C", label_dx=0.12, label_dy=0.08)
    _label_text(ax, 5.55, 1.06, "C = B − A", p, size=9.2, formula=True)
    return _save(fig, path)


def _make_displacement_geometry(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)
    _clean_origin_axes(ax, (1.0, 0.9), 8.8, 5.0, p)
    A = (2.6, 2.0)
    B = (6.7, 3.6)
    ax.add_patch(mpatches.Circle(A, 0.15, edgecolor=p["fg"], facecolor=p["soft"], lw=1.1))
    ax.add_patch(mpatches.Circle(B, 0.15, edgecolor=p["fg"], facecolor=p["accent"], lw=1.1))
    _vector_arrow(ax, A, B, p, color=p["accent"], lw=2.35, label="C", label_dx=0.14, label_dy=0.02)
    _label_text(ax, A[0] + 0.02, A[1] - 0.36, "A=(1,1)", p, size=8.1, formula=True)
    _label_text(ax, B[0] + 0.04, B[1] + 0.34, "B=(4,3)", p, size=8.1, formula=True)
    return _save(fig, path)


DRAWERS = {
    "point_and_vector_same_coords": _make_point_and_vector_same_coords,
    "vector_difference_geometry": _make_vector_difference_geometry,
    "displacement_geometry": _make_displacement_geometry,
}

ALIASES = {
    "same_coordinates_two_roles": "point_and_vector_same_coords",
    "difference_as_displacement": "vector_difference_geometry",
    "worked_displacement": "displacement_geometry",
    "displacement_worked_example": "displacement_geometry",
}

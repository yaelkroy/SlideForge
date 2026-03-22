from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches

from slideforge.assets.mini_visuals_common import _canvas, _clean_origin_axes, _label_text, _mini_panel, _save, _vector_arrow, _axes_2d, palette_for


def _make_point_and_vector_same_coords(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(5.25, 2.95))
    _mini_panel(ax, 0.70, 0.88, 8.80, 4.36, p)
    ax.plot([1.55, 1.55], [1.35, 4.48], color=p["ghost"], lw=0.95)
    ax.plot([1.55, 4.48], [1.35, 1.35], color=p["ghost"], lw=0.95)
    ax.plot([3.38, 3.38], [1.35, 3.28], color=p["ghost"], lw=0.90, linestyle="--")
    ax.plot([1.55, 3.38], [3.28, 3.28], color=p["ghost"], lw=0.90, linestyle="--")
    ax.add_patch(mpatches.Circle((3.38, 3.28), 0.18, edgecolor=p["fg"], facecolor=p["accent"], lw=1.1))
    _label_text(ax, 2.55, 4.66, "point view", p, size=8.5, color=p["soft"])
    _label_text(ax, 3.38, 1.06, "x", p, size=8.8, formula=True)
    ax.plot([6.05, 6.05], [1.50, 4.38], color=p["ghost"], lw=0.95)
    ax.plot([6.05, 8.92], [1.50, 1.50], color=p["ghost"], lw=0.95)
    _vector_arrow(ax, (6.05, 1.50), (8.55, 3.90), p, color=p["accent"], lw=2.55, label="x", label_dx=0.14, label_dy=0.10)
    _label_text(ax, 7.05, 4.66, "vector view", p, size=8.5, color=p["soft"])
    _label_text(ax, 5.00, 2.96, "same coordinates", p, size=8.1, color=p["fg"])
    return _save(fig, path)

def _make_vector_difference_geometry(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(5.1, 2.95))
    _axes_2d(ax, p)
    origin = (1.20, 1.05)
    a_tip = (4.10, 2.55)
    b_tip = (7.30, 3.98)
    _vector_arrow(ax, origin, a_tip, p, color=p["soft"], lw=2.10)
    _vector_arrow(ax, origin, b_tip, p, color=p["accent"], lw=2.45)
    _vector_arrow(ax, a_tip, b_tip, p, color=p["fg"], lw=2.25)
    _label_text(ax, 4.45, 2.72, "A", p, size=8.8, formula=True)
    _label_text(ax, 7.48, 4.06, "B", p, size=8.9, formula=True)
    _label_text(ax, 5.65, 1.18, "C = B − A", p, size=9.0, formula=True)
    return _save(fig, path)

def _make_displacement_geometry(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.9, 3.25))
    _clean_origin_axes(ax, (0.95, 0.95), 8.95, 5.15, p)
    A = (2.55, 2.15)
    B = (6.95, 3.85)
    ax.add_patch(mpatches.Circle(A, 0.16, edgecolor=p["fg"], facecolor=p["soft"], lw=1.15))
    ax.add_patch(mpatches.Circle(B, 0.16, edgecolor=p["fg"], facecolor=p["accent"], lw=1.15))
    _vector_arrow(ax, A, B, p, color=p["accent"], lw=2.55)
    _label_text(ax, A[0] - 0.22, A[1] - 0.36, "A=(1,1)", p, size=8.0, color=p["fg"])
    _label_text(ax, B[0] - 0.10, B[1] + 0.24, "B=(4,3)", p, size=8.0, color=p["fg"])
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

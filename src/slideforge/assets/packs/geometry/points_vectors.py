from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches

from slideforge.assets.mini_visuals_common import (
    _axes_2d,
    _canvas,
    _clean_origin_axes,
    _label_text,
    _mini_panel,
    _save,
    _vector_arrow,
    palette_for,
)


def _make_point_and_vector_same_coords(path: Path, variant: str) -> Path:
    """Two-panel comparison without a crossing bridge line through the center text."""
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(6.1, 3.55))

    left = (0.85, 1.02, 3.55, 4.15)
    right = (5.55, 1.02, 3.55, 4.15)
    _mini_panel(ax, *left, p, lw=1.0)
    _mini_panel(ax, *right, p, lw=1.0)

    # Left: point view.
    ax.plot([1.60, 1.60], [1.52, 4.45], color=p["ghost"], lw=0.95)
    ax.plot([1.60, 4.05], [1.52, 1.52], color=p["ghost"], lw=0.95)
    ax.plot([3.10, 3.10], [1.52, 3.30], color=p["ghost"], lw=0.90, linestyle="--")
    ax.plot([1.60, 3.10], [3.30, 3.30], color=p["ghost"], lw=0.90, linestyle="--")
    ax.add_patch(mpatches.Circle((3.10, 3.30), 0.16, edgecolor=p["fg"], facecolor=p["accent"], lw=1.1))
    _label_text(ax, 2.62, 4.73, "point view", p, size=8.8, color=p["soft"])
    _label_text(ax, 3.10, 1.18, "x", p, size=8.6, formula=True)

    # Right: vector view.
    ax.plot([6.25, 6.25], [1.62, 4.35], color=p["ghost"], lw=0.95)
    ax.plot([6.25, 8.72], [1.62, 1.62], color=p["ghost"], lw=0.95)
    _vector_arrow(ax, (6.25, 1.62), (8.55, 3.82), p, color=p["accent"], lw=2.65, label="x", label_dx=0.14, label_dy=0.10)
    _label_text(ax, 7.35, 4.73, "vector view", p, size=8.8, color=p["soft"])

    # Center text only, no line crossing it.
    _label_text(ax, 5.00, 2.95, "same coordinates", p, size=8.35, color=p["fg"])
    return _save(fig, path)



def _make_vector_difference_geometry(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(5.55, 3.25))
    _axes_2d(ax, p)
    origin = (1.30, 1.08)
    a_tip = (4.08, 2.36)
    b_tip = (7.72, 3.86)
    _vector_arrow(ax, origin, a_tip, p, color=p["soft"], lw=2.15)
    _vector_arrow(ax, origin, b_tip, p, color=p["accent"], lw=2.55)
    _vector_arrow(ax, a_tip, b_tip, p, color=p["fg"], lw=2.25)

    # Labels positioned off the lines to avoid overlap.
    _label_text(ax, 4.40, 2.55, "A", p, size=9.0, formula=True)
    _label_text(ax, 7.95, 4.08, "B", p, size=9.0, formula=True)
    _label_text(ax, 6.25, 1.30, "C = B − A", p, size=9.3, formula=True)
    return _save(fig, path)



def _make_displacement_geometry(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(5.3, 3.55))
    _clean_origin_axes(ax, (0.95, 0.95), 8.95, 5.25, p)
    A = (2.45, 2.10)
    B = (7.02, 4.02)
    ax.add_patch(mpatches.Circle(A, 0.16, edgecolor=p["fg"], facecolor=p["soft"], lw=1.15))
    ax.add_patch(mpatches.Circle(B, 0.16, edgecolor=p["fg"], facecolor=p["accent"], lw=1.15))
    _vector_arrow(ax, A, B, p, color=p["accent"], lw=2.65)
    _label_text(ax, A[0] - 0.12, A[1] - 0.42, "A=(1,1)", p, size=8.2, color=p["fg"])
    _label_text(ax, B[0] + 0.02, B[1] + 0.24, "B=(4,3)", p, size=8.2, color=p["fg"])
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

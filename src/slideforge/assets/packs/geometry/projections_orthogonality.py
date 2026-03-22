from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches

from slideforge.assets.mini_visuals_common import _canvas, _label_text, _mini_panel, _right_angle_marker, _save, _tip_projection, _vector_arrow, palette_for


def _make_orthogonal_vectors_geometry(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.9, 2.8))
    _mini_panel(ax, 0.90, 1.00, 8.15, 4.05, p)
    origin = (2.20, 1.60)
    x_tip = (6.55, 1.60)
    y_tip = (2.20, 4.55)
    _vector_arrow(ax, origin, x_tip, p, color=p["soft"], lw=2.15, label="x")
    _vector_arrow(ax, origin, y_tip, p, color=p["accent"], lw=2.20, label="y")
    _right_angle_marker(ax, 2.20, 1.60, 0.34, p)
    _mini_panel(ax, 6.95, 2.55, 1.55, 1.55, p, lw=0.9)
    _label_text(ax, 7.72, 3.35, "x·y", p, size=8.6, formula=True)
    _label_text(ax, 7.72, 2.65, "= 0", p, size=8.8, formula=True)
    _label_text(ax, 7.72, 4.52, "90°", p, size=8.9, formula=True, color=p["soft"])
    return _save(fig, path)


def _make_projection_geometry(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)
    origin = (1.5, 1.3)
    y_tip = (8.3, 2.25)
    x_tip = (5.7, 4.75)
    _vector_arrow(ax, origin, y_tip, p, color=p["soft"], lw=2.05, label="y")
    _vector_arrow(ax, origin, x_tip, p, color=p["accent"], lw=2.35, label="x")
    proj = _tip_projection(x_tip, origin, y_tip)
    ax.plot([x_tip[0], proj[0]], [x_tip[1], proj[1]], color=p["ghost"], lw=1.2, linestyle="--")
    _vector_arrow(ax, origin, proj, p, color=p["fg"], lw=2.1, label="p")
    return _save(fig, path)


def _make_projection_homework_geometry(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.95, 2.95))
    _mini_panel(ax, 0.90, 1.00, 8.15, 4.00, p)
    origin = (1.45, 1.62)
    y_tip = (8.05, 2.18)
    x_tip = (4.25, 4.25)
    proj = _tip_projection(x_tip, origin, y_tip)
    _vector_arrow(ax, origin, x_tip, p, color=p["accent"], lw=2.25, label="x")
    _vector_arrow(ax, origin, y_tip, p, color=p["soft"], lw=2.05, label="y")
    ax.plot([x_tip[0], proj[0]], [x_tip[1], proj[1]], color=p["ghost"], lw=1.0, linestyle="--")
    _vector_arrow(ax, origin, proj, p, color=p["fg"], lw=2.05, label="p")
    ax.add_patch(mpatches.Circle((proj[0], proj[1]), 0.11, edgecolor=p["fg"], facecolor=p["fg"], lw=0.8))
    _label_text(ax, 7.62, 4.45, "projection", p, size=7.7, color=p["soft"])
    return _save(fig, path)


DRAWERS = {
    "orthogonal_vectors_geometry": _make_orthogonal_vectors_geometry,
    "projection_geometry": _make_projection_geometry,
    "projection_homework_geometry": _make_projection_homework_geometry,
}

ALIASES = {
    "orthogonal_geometry_symbolic": "orthogonal_vectors_geometry",
    "orthogonal_vectors_symbolic": "orthogonal_vectors_geometry",
    "orthogonal_geometry_only": "orthogonal_vectors_geometry",
    "vector_projection": "projection_geometry",
    "homework_projection_symbolic": "projection_homework_geometry",
    "projection_symbolic_homework": "projection_homework_geometry",
    "homework_projection_geometry_only": "projection_homework_geometry",
}

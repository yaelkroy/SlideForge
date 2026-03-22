from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches

from slideforge.assets.mini_visuals_common import _axes_2d, _canvas, _label_text, _mini_panel, _right_angle_marker, _save, _vector_arrow, _vector_strip, palette_for


def _make_norm_triangle(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)
    _axes_2d(ax, p)
    origin = (1.3, 1.1)
    tip = (7.0, 4.0)
    foot = (7.0, 1.1)
    _vector_arrow(ax, origin, tip, p, color=p["accent"], lw=2.45, label="x")
    ax.plot([tip[0], foot[0]], [tip[1], foot[1]], color=p["ghost"], lw=1.1, linestyle="--")
    ax.plot([origin[0], foot[0]], [origin[1], foot[1]], color=p["ghost"], lw=1.1, linestyle="--")
    _right_angle_marker(ax, 6.68, 1.10, 0.30, p)
    _label_text(ax, 4.18, 0.72, "components", p, size=7.9, color=p["soft"])
    _label_text(ax, 5.00, 2.76, "‖x‖", p, size=10.0, formula=True)
    return _save(fig, path)


def _make_norm_worked_geometry(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.8, 2.8))
    _mini_panel(ax, 1.0, 0.95, 7.45, 4.05, p)
    origin = (1.85, 1.55)
    tip = (6.25, 4.02)
    foot = (6.25, 1.55)
    _vector_arrow(ax, origin, tip, p, color=p["accent"], lw=2.45, label="x")
    ax.plot([tip[0], foot[0]], [tip[1], foot[1]], color=p["ghost"], lw=1.0, linestyle="--")
    ax.plot([origin[0], foot[0]], [origin[1], foot[1]], color=p["ghost"], lw=1.0, linestyle="--")
    _right_angle_marker(ax, 5.96, 1.55, 0.27, p)
    _label_text(ax, 4.45, 0.95, "vector from the origin", p, size=7.8, color=p["soft"])
    return _save(fig, path)


def _make_dot_product_pairing(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.6, 2.6))
    _mini_panel(ax, 1.0, 1.0, 2.2, 4.2, p)
    _mini_panel(ax, 4.2, 1.0, 2.2, 4.2, p)
    ys = [4.35, 3.10, 1.85]
    for val, yy in zip(["x₁", "x₂", "x₃"], ys):
        _label_text(ax, 2.1, yy, val, p, size=10, formula=True)
    for val, yy in zip(["y₁", "y₂", "y₃"], ys):
        _label_text(ax, 5.3, yy, val, p, size=10, formula=True)
    for yy in ys:
        ax.plot([2.45, 4.95], [yy, yy], color=p["ghost"], lw=1.0)
    _label_text(ax, 7.8, 3.0, "pairwise", p, size=8.2, color=p["soft"])
    _label_text(ax, 7.8, 2.25, "products", p, size=8.4, color=p["fg"])
    return _save(fig, path)


def _make_dot_product_worked_geometry(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.9, 2.9))
    _mini_panel(ax, 0.85, 1.05, 4.10, 3.85, p)
    _mini_panel(ax, 5.30, 1.05, 3.85, 3.85, p)
    _vector_strip(ax, 1.20, 3.18, 3.35, 0.74, p, ["3", "2", "2"], labels=["x₁", "x₂", "x₃"])
    _vector_strip(ax, 1.20, 1.82, 3.35, 0.74, p, ["1", "1", "1"], labels=["y₁", "y₂", "y₃"])
    for x in [1.76, 2.88, 4.00]:
        ax.plot([x, 6.08], [2.55, 3.00], color=p["ghost"], lw=0.9)
    _label_text(ax, 7.22, 3.86, "matching entries", p, size=7.9, color=p["soft"])
    _label_text(ax, 7.22, 2.98, "multiply", p, size=8.7, color=p["fg"])
    _label_text(ax, 7.22, 2.20, "then add", p, size=8.0, color=p["soft"])
    return _save(fig, path)


def _make_dot_alignment_angle(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)
    origin = (2.0, 1.5)
    x_tip = (7.2, 2.0)
    y_tip = (6.2, 4.4)
    _vector_arrow(ax, origin, x_tip, p, color=p["soft"], lw=2.0, label="x")
    _vector_arrow(ax, origin, y_tip, p, color=p["accent"], lw=2.35, label="y")
    ax.add_patch(mpatches.Arc(origin, 1.6, 1.3, angle=0, theta1=5, theta2=48, color=p["ghost"], lw=1.1))
    _label_text(ax, 3.28, 2.00, "α", p, size=8.7, formula=True)
    _label_text(ax, 7.34, 5.00, "positive", p, size=8.0, color=p["accent"])
    _label_text(ax, 7.58, 4.33, "zero", p, size=8.0, color=p["soft"])
    _label_text(ax, 7.48, 3.66, "negative", p, size=8.0, color=p["fg"])
    return _save(fig, path)


def _make_angle_recovery_geometry(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.8, 2.8))
    _mini_panel(ax, 0.80, 1.00, 4.10, 4.15, p)
    _mini_panel(ax, 5.20, 1.00, 4.00, 4.15, p)
    origin = (1.75, 1.72)
    x_tip = (4.00, 2.95)
    y_tip = (2.90, 4.25)
    _vector_arrow(ax, origin, x_tip, p, color=p["soft"], lw=2.0, label="x")
    _vector_arrow(ax, origin, y_tip, p, color=p["accent"], lw=2.25, label="y")
    ax.add_patch(mpatches.Arc(origin, 1.25, 1.05, angle=0, theta1=22, theta2=70, color=p["ghost"], lw=1.0))
    _label_text(ax, 2.46, 2.34, "α", p, size=8.4, formula=True)
    center = (7.20, 3.02)
    ax.add_patch(mpatches.Circle(center, 0.92, fill=False, edgecolor=p["ghost"], linewidth=1.0))
    ax.plot([6.32, 8.08], [3.02, 3.02], color=p["ghost"], lw=0.95)
    ax.plot([7.20, 7.20], [2.14, 3.90], color=p["ghost"], lw=0.95)
    ax.add_patch(mpatches.Arc(center, 1.25, 1.25, angle=0, theta1=15, theta2=50, color=p["accent"], lw=1.2))
    _label_text(ax, 7.80, 3.56, "α", p, size=8.6, formula=True)
    _label_text(ax, 7.18, 4.42, "angle", p, size=7.8, color=p["soft"])
    return _save(fig, path)


def _make_angle_homework_geometry(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(5.55, 3.10))
    _mini_panel(ax, 0.70, 0.92, 8.80, 4.22, p)
    origin = (1.55, 1.34)
    x_tip = (5.92, 3.98)
    y_tip = (7.15, 1.34)
    _vector_arrow(ax, origin, x_tip, p, color=p["accent"], lw=2.30, label="x", label_dx=0.16, label_dy=0.08)
    _vector_arrow(ax, origin, y_tip, p, color=p["soft"], lw=2.10, label="y", label_dx=0.14, label_dy=0.02)
    ax.plot([x_tip[0], x_tip[0]], [x_tip[1], origin[1]], color=p["ghost"], lw=0.95, linestyle="--")
    _right_angle_marker(ax, 5.62, 1.34, 0.28, p)
    ax.add_patch(mpatches.Arc(origin, 1.70, 1.18, angle=0, theta1=7, theta2=32, color=p["ghost"], lw=1.05))
    _label_text(ax, 2.78, 1.78, "α", p, size=8.8, formula=True)
    return _save(fig, path)

def _make_unit_vector_normalization(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)
    _axes_2d(ax, p)
    origin = (1.2, 1.1)
    long_tip = (7.3, 4.1)
    short_tip = (4.9, 2.95)
    _vector_arrow(ax, origin, long_tip, p, color=p["soft"], lw=2.0, label="x")
    _vector_arrow(ax, origin, short_tip, p, color=p["accent"], lw=2.45, label="u")
    _label_text(ax, 6.55, 4.55, "same direction", p, size=8.1, color=p["soft"])
    _label_text(ax, 5.20, 2.26, "‖u‖=1", p, size=9.0, formula=True)
    return _save(fig, path)


DRAWERS = {
    "norm_triangle": _make_norm_triangle,
    "norm_worked_geometry": _make_norm_worked_geometry,
    "dot_product_pairing": _make_dot_product_pairing,
    "dot_product_worked_geometry": _make_dot_product_worked_geometry,
    "dot_alignment_angle": _make_dot_alignment_angle,
    "angle_recovery_geometry": _make_angle_recovery_geometry,
    "angle_homework_geometry": _make_angle_homework_geometry,
    "unit_vector_normalization": _make_unit_vector_normalization,
}

ALIASES = {
    "vector_norm_geometry": "norm_triangle",
    "worked_norm_geometry": "norm_worked_geometry",
    "norm_worked_example": "norm_worked_geometry",
    "worked_norm_geometry_only": "norm_worked_geometry",
    "dot_product_coordinates": "dot_product_pairing",
    "worked_dot_product": "dot_product_worked_geometry",
    "dot_product_worked_example": "dot_product_worked_geometry",
    "worked_dot_product_geometry_only": "dot_product_worked_geometry",
    "dot_product_alignment": "dot_alignment_angle",
    "angle_from_dot_product": "angle_recovery_geometry",
    "worked_angle_homework": "angle_homework_geometry",
    "angle_homework_worked": "angle_homework_geometry",
    "worked_angle_geometry_only": "angle_homework_geometry",
    "normalized_vector": "unit_vector_normalization",
}

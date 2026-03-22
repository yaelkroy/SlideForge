from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.patches as mpatches

from slideforge.assets.mini_visuals_common import (
    _axes_2d,
    _canvas,
    _label_text,
    _mini_panel,
    _right_angle_marker,
    _save,
    _vector_arrow,
    _vector_strip,
    palette_for,
)


VISUAL_METADATA: dict[str, dict[str, Any]] = {
    "norm_triangle": {
        "preferred_layout": "two_column",
        "min_width_in": 4.0,
        "min_height_in": 1.9,
        "preferred_aspect_ratio": 2.0,
        "label_density": "medium",
        "text_bearing": False,
        "allow_top_strip": False,
    },
    "norm_worked_geometry": {
        "preferred_layout": "two_column",
        "min_width_in": 4.0,
        "min_height_in": 2.3,
        "preferred_aspect_ratio": 1.62,
        "label_density": "medium",
        "text_bearing": False,
        "allow_top_strip": False,
    },
    "dot_product_pairing": {
        "preferred_layout": "two_column",
        "min_width_in": 3.8,
        "min_height_in": 2.1,
        "preferred_aspect_ratio": 1.8,
        "label_density": "high",
        "text_bearing": False,
        "allow_top_strip": False,
    },
    "dot_product_worked_geometry": {
        "preferred_layout": "two_column",
        "min_width_in": 4.4,
        "min_height_in": 2.35,
        "preferred_aspect_ratio": 1.7,
        "label_density": "high",
        "text_bearing": False,
        "allow_top_strip": False,
    },
    "dot_alignment_angle": {
        "preferred_layout": "either",
        "min_width_in": 3.9,
        "min_height_in": 2.0,
        "preferred_aspect_ratio": 1.9,
        "label_density": "medium",
        "text_bearing": False,
        "allow_top_strip": True,
    },
    "angle_recovery_geometry": {
        "preferred_layout": "two_column",
        "min_width_in": 4.1,
        "min_height_in": 2.15,
        "preferred_aspect_ratio": 1.75,
        "label_density": "medium",
        "text_bearing": False,
        "allow_top_strip": True,
    },
    "angle_homework_geometry": {
        "preferred_layout": "two_column",
        "min_width_in": 5.0,
        "min_height_in": 2.35,
        "preferred_aspect_ratio": 2.1,
        "label_density": "medium",
        "text_bearing": False,
        "allow_top_strip": False,
    },
    "unit_vector_normalization": {
        "preferred_layout": "two_column",
        "min_width_in": 4.0,
        "min_height_in": 2.0,
        "preferred_aspect_ratio": 1.9,
        "label_density": "medium",
        "text_bearing": False,
        "allow_top_strip": False,
    },
}


def get_visual_metadata(kind: str) -> dict[str, Any]:
    return dict(VISUAL_METADATA.get(str(kind or "").strip(), {}))


def _make_norm_triangle(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.8, 2.95))
    _axes_2d(ax, p)
    origin = (1.35, 1.10)
    tip = (7.10, 4.05)
    foot = (7.10, 1.10)
    _vector_arrow(ax, origin, tip, p, color=p["accent"], lw=2.55, label="x")
    ax.plot([tip[0], foot[0]], [tip[1], foot[1]], color=p["ghost"], lw=1.1, linestyle="--")
    ax.plot([origin[0], foot[0]], [origin[1], foot[1]], color=p["ghost"], lw=1.1, linestyle="--")
    _right_angle_marker(ax, 6.78, 1.10, 0.30, p)
    _label_text(ax, 4.20, 0.70, "components", p, size=8.0, color=p["soft"])
    _label_text(ax, 5.10, 2.82, "‖x‖", p, size=10.2, formula=True)
    return _save(fig, path)


def _make_norm_worked_geometry(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(5.45, 3.35))
    _mini_panel(ax, 0.70, 0.75, 8.35, 4.55, p)
    origin = (1.55, 1.42)
    tip = (6.85, 4.22)
    foot = (6.85, 1.42)
    _vector_arrow(ax, origin, tip, p, color=p["accent"], lw=2.65, label="x")
    ax.plot([tip[0], foot[0]], [tip[1], foot[1]], color=p["ghost"], lw=1.0, linestyle="--")
    ax.plot([origin[0], foot[0]], [origin[1], foot[1]], color=p["ghost"], lw=1.0, linestyle="--")
    _right_angle_marker(ax, 6.52, 1.42, 0.29, p)
    _label_text(ax, 4.60, 0.96, "vector from the origin", p, size=7.9, color=p["soft"])
    return _save(fig, path)


def _make_dot_product_pairing(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.8, 2.8))
    _mini_panel(ax, 0.95, 0.90, 2.35, 4.28, p)
    _mini_panel(ax, 4.20, 0.90, 2.35, 4.28, p)
    ys = [4.35, 3.10, 1.85]
    for val, yy in zip(["x₁", "x₂", "x₃"], ys):
        _label_text(ax, 2.12, yy, val, p, size=10.0, formula=True)
    for val, yy in zip(["y₁", "y₂", "y₃"], ys):
        _label_text(ax, 5.38, yy, val, p, size=10.0, formula=True)
    for yy in ys:
        ax.plot([2.50, 5.00], [yy, yy], color=p["ghost"], lw=1.0)
    _label_text(ax, 7.80, 3.05, "pairwise", p, size=8.35, color=p["soft"])
    _label_text(ax, 7.80, 2.25, "products", p, size=8.5, color=p["fg"])
    return _save(fig, path)


def _make_dot_product_worked_geometry(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(5.35, 3.15))
    _mini_panel(ax, 0.70, 0.86, 4.65, 4.32, p)
    _mini_panel(ax, 5.55, 0.86, 3.75, 4.32, p)
    _vector_strip(ax, 1.08, 3.26, 3.80, 0.76, p, ["3", "2", "2"], labels=["x₁", "x₂", "x₃"])
    _vector_strip(ax, 1.08, 1.80, 3.80, 0.76, p, ["1", "1", "1"], labels=["y₁", "y₂", "y₃"])
    for x in [1.76, 3.03, 4.30]:
        ax.plot([x, 6.12], [2.52, 2.98], color=p["ghost"], lw=0.9)
    _label_text(ax, 7.18, 3.88, "matching entries", p, size=7.9, color=p["soft"])
    _label_text(ax, 7.18, 3.00, "multiply", p, size=8.7, color=p["fg"])
    _label_text(ax, 7.18, 2.20, "then add", p, size=8.0, color=p["soft"])
    return _save(fig, path)


def _make_dot_alignment_angle(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.8, 3.0))
    origin = (2.0, 1.5)
    x_tip = (7.2, 2.0)
    y_tip = (6.2, 4.4)
    _vector_arrow(ax, origin, x_tip, p, color=p["soft"], lw=2.1, label="x")
    _vector_arrow(ax, origin, y_tip, p, color=p["accent"], lw=2.45, label="y")
    ax.add_patch(mpatches.Arc(origin, 1.6, 1.3, angle=0, theta1=5, theta2=48, color=p["ghost"], lw=1.1))
    _label_text(ax, 3.28, 2.00, "α", p, size=8.8, formula=True)
    _label_text(ax, 7.34, 5.00, "positive", p, size=8.0, color=p["accent"])
    _label_text(ax, 7.58, 4.33, "zero", p, size=8.0, color=p["soft"])
    _label_text(ax, 7.48, 3.66, "negative", p, size=8.0, color=p["fg"])
    return _save(fig, path)


def _make_angle_recovery_geometry(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(5.1, 3.05))
    _mini_panel(ax, 0.72, 0.90, 4.20, 4.22, p)
    _mini_panel(ax, 5.22, 0.90, 4.02, 4.22, p)
    origin = (1.72, 1.72)
    x_tip = (4.06, 3.06)
    y_tip = (2.86, 4.22)
    _vector_arrow(ax, origin, x_tip, p, color=p["soft"], lw=2.05, label="x")
    _vector_arrow(ax, origin, y_tip, p, color=p["accent"], lw=2.3, label="y")
    ax.add_patch(mpatches.Arc(origin, 1.35, 1.10, angle=0, theta1=22, theta2=70, color=p["ghost"], lw=1.0))
    _label_text(ax, 2.48, 2.36, "α", p, size=8.45, formula=True)
    center = (7.18, 3.02)
    ax.add_patch(mpatches.Circle(center, 0.96, fill=False, edgecolor=p["ghost"], linewidth=1.0))
    ax.plot([6.26, 8.10], [3.02, 3.02], color=p["ghost"], lw=0.95)
    ax.plot([7.18, 7.18], [2.10, 3.94], color=p["ghost"], lw=0.95)
    ax.add_patch(mpatches.Arc(center, 1.35, 1.35, angle=0, theta1=15, theta2=50, color=p["accent"], lw=1.2))
    _label_text(ax, 7.83, 3.60, "α", p, size=8.8, formula=True)
    _label_text(ax, 7.18, 4.45, "angle", p, size=7.9, color=p["soft"])
    return _save(fig, path)


def _make_angle_homework_geometry(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(6.2, 3.9))
    _mini_panel(ax, 0.48, 0.62, 9.15, 4.95, p)
    origin = (1.10, 1.18)
    x_tip = (5.95, 4.32)
    y_tip = (7.82, 1.18)
    _vector_arrow(ax, origin, x_tip, p, color=p["accent"], lw=2.5, label="x", label_dx=0.16, label_dy=0.08)
    _vector_arrow(ax, origin, y_tip, p, color=p["soft"], lw=2.25, label="y", label_dx=0.14, label_dy=0.02)
    ax.plot([x_tip[0], x_tip[0]], [x_tip[1], origin[1]], color=p["ghost"], lw=0.95, linestyle="--")
    _right_angle_marker(ax, 5.62, 1.18, 0.30, p)
    ax.add_patch(mpatches.Arc(origin, 1.88, 1.28, angle=0, theta1=8, theta2=33, color=p["ghost"], lw=1.05))
    _label_text(ax, 2.88, 1.82, "α", p, size=8.9, formula=True)
    return _save(fig, path)


def _make_unit_vector_normalization(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.8, 2.95))
    _axes_2d(ax, p)
    origin = (1.2, 1.1)
    long_tip = (7.3, 4.1)
    short_tip = (4.9, 2.95)
    _vector_arrow(ax, origin, long_tip, p, color=p["soft"], lw=2.0, label="x")
    _vector_arrow(ax, origin, short_tip, p, color=p["accent"], lw=2.45, label="u")
    _label_text(ax, 6.55, 4.55, "same direction", p, size=8.1, color=p["soft"])
    _label_text(ax, 5.20, 2.26, "‖u‖=1", p, size=9.1, formula=True)
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

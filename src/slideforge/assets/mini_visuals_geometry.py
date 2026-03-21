from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches

from slideforge.assets.mini_visuals_common import (
    _axes_2d,
    _axes_3d_fake,
    _canvas,
    _label_text,
    _save,
    _soft_panel,
    _tip_projection,
    _vector_arrow,
    _vector_strip,
    palette_for,
)


# NOTE:
# Dense worked-example and homework visuals in this module should stay mostly
# geometric. Long formulas and derivation steps should be rendered as native
# PowerPoint text by the builder layer, not rasterized into the PNG.


def _make_point_vector_projection_hero(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(7.2, 2.4))
    origin, _, _, _ = _axes_3d_fake(ax, p)

    x_tip = (6.7, 3.9)
    y_tip = (7.5, 2.2)

    _vector_arrow(ax, origin, x_tip, p, color=p["accent"], lw=2.5, label="x")
    _vector_arrow(ax, origin, y_tip, p, color=p["soft"], lw=2.1, label="y")

    proj = _tip_projection(x_tip, origin, y_tip)
    ax.plot([x_tip[0], proj[0]], [x_tip[1], proj[1]], color=p["ghost"], lw=1.2, linestyle="--")
    _vector_arrow(ax, origin, proj, p, color=p["fg"], lw=2.0, label="proj")

    ax.add_patch(mpatches.Arc(origin, 1.8, 1.2, angle=0, theta1=10, theta2=34, color=p["ghost"], lw=1.1))
    _label_text(ax, 2.45, 1.72, "α", p, size=9, formula=True)

    _label_text(ax, 6.15, 4.55, "x=(3,2,2)", p, size=8.5, formula=True)
    _label_text(ax, 7.65, 2.55, "y=(1,1,1)", p, size=8.5, formula=True, ha="left")
    return _save(fig, path)


def _make_point_and_vector_same_coords(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)

    _soft_panel(ax, 0.7, 1.1, 3.9, 3.9, p)
    _soft_panel(ax, 5.4, 1.1, 3.9, 3.9, p)

    ax.plot([1.3, 1.3], [1.6, 4.5], color=p["ghost"], lw=0.9)
    ax.plot([1.3, 4.1], [1.6, 1.6], color=p["ghost"], lw=0.9)
    ax.add_patch(mpatches.Circle((3.55, 3.45), 0.16, edgecolor=p["fg"], facecolor=p["accent"], lw=1.1))
    _label_text(ax, 2.65, 4.75, "point view", p, size=8.5, color=p["soft"])
    _label_text(ax, 3.55, 1.18, "x=(3,2,2)", p, size=8.5, formula=True)

    ax.plot([6.0, 6.0], [1.6, 4.5], color=p["ghost"], lw=0.9)
    ax.plot([6.0, 8.8], [1.6, 1.6], color=p["ghost"], lw=0.9)
    _vector_arrow(ax, (6.0, 1.6), (8.45, 4.05), p, color=p["accent"], lw=2.2, label="x")
    _label_text(ax, 7.35, 4.75, "vector view", p, size=8.5, color=p["soft"])

    _label_text(ax, 5.0, 3.05, "same coordinates", p, size=8.3, color=p["fg"])
    _vector_arrow(ax, (4.7, 3.0), (5.2, 3.0), p, color=p["accent"], lw=1.5)
    return _save(fig, path)


def _make_vector_difference_geometry(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)

    _axes_2d(ax, p)
    origin = (1.3, 1.1)
    a_tip = (4.0, 2.5)
    b_tip = (7.1, 4.0)

    _vector_arrow(ax, origin, a_tip, p, color=p["soft"], lw=2.0, label="A")
    _vector_arrow(ax, origin, b_tip, p, color=p["accent"], lw=2.3, label="B")
    _vector_arrow(ax, a_tip, b_tip, p, color=p["fg"], lw=2.1, label="C", label_dx=0.14, label_dy=0.06)

    _label_text(ax, 5.5, 1.0, "C = B − A", p, size=9, formula=True)
    return _save(fig, path)


def _make_displacement_worked_example(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)

    ax.plot([1.0, 1.0], [0.9, 5.0], color=p["ghost"], lw=1.0)
    ax.plot([1.0, 8.8], [0.9, 0.9], color=p["ghost"], lw=1.0)

    A = (2.6, 2.0)
    B = (6.7, 3.6)

    ax.add_patch(mpatches.Circle(A, 0.15, edgecolor=p["fg"], facecolor=p["soft"], lw=1.1))
    ax.add_patch(mpatches.Circle(B, 0.15, edgecolor=p["fg"], facecolor=p["accent"], lw=1.1))
    _vector_arrow(ax, A, B, p, color=p["accent"], lw=2.3, label="C", label_dx=0.18, label_dy=0.00)

    _label_text(ax, A[0], A[1] - 0.32, "A=(1,1)", p, size=8.2, formula=True)
    _label_text(ax, B[0], B[1] + 0.30, "B=(4,3)", p, size=8.2, formula=True)
    return _save(fig, path)


def _make_norm_triangle(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)

    _axes_2d(ax, p)
    origin = (1.3, 1.1)
    tip = (7.0, 4.0)
    foot = (7.0, 1.1)

    _vector_arrow(ax, origin, tip, p, color=p["accent"], lw=2.4, label="x")
    ax.plot([tip[0], foot[0]], [tip[1], foot[1]], color=p["ghost"], lw=1.1, linestyle="--")
    ax.plot([origin[0], foot[0]], [origin[1], foot[1]], color=p["ghost"], lw=1.1, linestyle="--")
    ax.add_patch(mpatches.Rectangle((6.7, 1.1), 0.3, 0.3, fill=False, edgecolor=p["ghost"], lw=0.9))

    _label_text(ax, 4.15, 0.75, "components", p, size=8, color=p["soft"])
    _label_text(ax, 4.95, 2.75, "‖x‖", p, size=10, formula=True)
    return _save(fig, path)


def _make_norm_worked_example(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.6, 2.6))

    _soft_panel(ax, 0.7, 0.9, 8.5, 4.2, p)

    origin = (1.7, 1.4)
    tip = (6.1, 4.0)
    foot = (6.1, 1.4)

    _vector_arrow(ax, origin, tip, p, color=p["accent"], lw=2.3, label="x")
    ax.plot([tip[0], foot[0]], [tip[1], foot[1]], color=p["ghost"], lw=1.0, linestyle="--")
    ax.plot([origin[0], foot[0]], [origin[1], foot[1]], color=p["ghost"], lw=1.0, linestyle="--")
    ax.add_patch(mpatches.Rectangle((5.8, 1.4), 0.3, 0.3, fill=False, edgecolor=p["ghost"], lw=0.9))

    _label_text(ax, 7.55, 4.2, "worked example", p, size=8.0, color=p["soft"], ha="center")
    _label_text(ax, 7.55, 3.2, "geometry only", p, size=8.2, color=p["fg"], ha="center")
    _label_text(ax, 7.55, 2.3, "steps in text", p, size=7.8, color=p["soft"], ha="center")
    return _save(fig, path)


def _make_dot_product_pairing(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.6, 2.6))

    _soft_panel(ax, 1.0, 1.0, 2.2, 4.2, p)
    _soft_panel(ax, 4.2, 1.0, 2.2, 4.2, p)

    left_vals = ["x₁", "x₂", "x₃"]
    right_vals = ["y₁", "y₂", "y₃"]
    ys = [4.35, 3.10, 1.85]

    for val, yy in zip(left_vals, ys):
        _label_text(ax, 2.1, yy, val, p, size=10, formula=True)
    for val, yy in zip(right_vals, ys):
        _label_text(ax, 5.3, yy, val, p, size=10, formula=True)

    for yy in ys:
        ax.plot([2.45, 4.95], [yy, yy], color=p["ghost"], lw=1.0)

    _label_text(ax, 7.8, 3.0, "pairwise", p, size=8.3, color=p["soft"])
    _label_text(ax, 7.8, 2.25, "multiply", p, size=8.6, color=p["fg"])
    return _save(fig, path)


def _make_dot_product_worked_example(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.8, 2.8))

    _soft_panel(ax, 0.7, 0.9, 8.6, 4.2, p)

    _vector_strip(ax, 1.0, 3.35, 3.0, 0.72, p, ["3", "2", "2"], labels=["x₁", "x₂", "x₃"])
    _vector_strip(ax, 1.0, 1.95, 3.0, 0.72, p, ["1", "1", "1"], labels=["y₁", "y₂", "y₃"])

    for x in [1.48, 2.49, 3.50]:
        ax.plot([x, x], [2.67, 3.35], color=p["ghost"], lw=0.9)

    _label_text(ax, 6.4, 3.95, "pairwise products", p, size=8.0, color=p["soft"], ha="center")
    _label_text(ax, 6.4, 2.95, "sum outside image", p, size=8.2, color=p["fg"], ha="center")
    _label_text(ax, 6.4, 1.95, "builder renders math", p, size=7.8, color=p["soft"], ha="center")
    return _save(fig, path)


def _make_dot_alignment_angle(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)

    origin = (2.0, 1.5)
    x_tip = (7.2, 2.0)
    y_tip = (6.2, 4.4)

    _vector_arrow(ax, origin, x_tip, p, color=p["soft"], lw=2.0, label="x")
    _vector_arrow(ax, origin, y_tip, p, color=p["accent"], lw=2.3, label="y")

    ax.add_patch(mpatches.Arc(origin, 1.6, 1.3, angle=0, theta1=5, theta2=48, color=p["ghost"], lw=1.1))
    _label_text(ax, 3.25, 2.0, "α", p, size=8.7, formula=True)

    _label_text(ax, 7.3, 5.0, "positive", p, size=8.0, color=p["accent"])
    _label_text(ax, 7.55, 4.35, "zero", p, size=8.0, color=p["soft"])
    _label_text(ax, 7.45, 3.70, "negative", p, size=8.0, color=p["fg"])
    return _save(fig, path)


def _make_angle_recovery_geometry(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.6, 2.6))

    _soft_panel(ax, 0.7, 1.0, 3.9, 4.2, p)
    _soft_panel(ax, 5.0, 1.0, 4.2, 4.2, p)

    origin = (1.6, 1.7)
    x_tip = (3.9, 3.0)
    y_tip = (2.9, 4.2)

    _vector_arrow(ax, origin, x_tip, p, color=p["soft"], lw=2.0, label="x")
    _vector_arrow(ax, origin, y_tip, p, color=p["accent"], lw=2.2, label="y")

    ax.add_patch(mpatches.Arc(origin, 1.3, 1.1, angle=0, theta1=22, theta2=70, color=p["ghost"], lw=1.0))
    _label_text(ax, 2.45, 2.35, "α", p, size=8.5, formula=True)

    _label_text(ax, 7.1, 3.45, "recover angle", p, size=8.2, color=p["soft"])
    _label_text(ax, 7.1, 2.35, "formula in text", p, size=8.4, color=p["fg"])
    return _save(fig, path)


def _make_angle_homework_worked(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.8, 2.8))

    _soft_panel(ax, 0.7, 0.8, 8.7, 4.5, p)

    origin = (2.0, 1.55)
    x_tip = (5.5, 4.15)
    y_tip = (6.45, 1.55)

    _vector_arrow(ax, origin, x_tip, p, color=p["accent"], lw=2.2, label="x")
    _vector_arrow(ax, origin, y_tip, p, color=p["soft"], lw=2.0, label="y")
    ax.add_patch(mpatches.Rectangle((5.28, 1.55), 0.27, 0.27, fill=False, edgecolor=p["ghost"], lw=0.9))

    ax.plot([x_tip[0], x_tip[0]], [x_tip[1], origin[1]], color=p["ghost"], lw=0.9, linestyle="--")
    _label_text(ax, 7.85, 3.65, "homework geometry", p, size=8.0, color=p["soft"], ha="center")
    _label_text(ax, 7.85, 2.65, "numeric steps", p, size=8.2, color=p["fg"], ha="center")
    _label_text(ax, 7.85, 1.75, "outside image", p, size=7.8, color=p["soft"], ha="center")
    return _save(fig, path)


def _make_orthogonal_vectors_symbolic(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.8, 2.6))

    _soft_panel(ax, 0.7, 0.9, 8.5, 4.2, p)

    origin = (2.1, 1.55)
    x_tip = (6.2, 1.55)
    y_tip = (2.1, 4.45)

    _vector_arrow(ax, origin, x_tip, p, color=p["soft"], lw=2.1, label="x")
    _vector_arrow(ax, origin, y_tip, p, color=p["accent"], lw=2.1, label="y")
    ax.add_patch(mpatches.Rectangle((2.1, 1.55), 0.38, 0.38, fill=False, edgecolor=p["ghost"], lw=0.9))

    ax.plot([6.55, 8.35], [1.55, 1.55], color=p["ghost"], lw=1.0)
    ax.plot([6.55, 6.55], [1.55, 3.85], color=p["ghost"], lw=1.0)
    _label_text(ax, 7.45, 4.25, "90°", p, size=9.0, formula=True)
    _label_text(ax, 7.45, 3.25, "orthogonal", p, size=8.1, color=p["soft"])
    _label_text(ax, 7.45, 2.25, "formula in text", p, size=7.9, color=p["fg"])
    return _save(fig, path)


def _make_unit_vector_normalization(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)

    _axes_2d(ax, p)
    origin = (1.2, 1.1)
    long_tip = (7.3, 4.1)
    short_tip = (4.9, 2.95)

    _vector_arrow(ax, origin, long_tip, p, color=p["soft"], lw=2.0, label="x")
    _vector_arrow(ax, origin, short_tip, p, color=p["accent"], lw=2.4, label="u")

    _label_text(ax, 6.55, 4.55, "same direction", p, size=8.2, color=p["soft"])
    _label_text(ax, 5.2, 2.3, "‖u‖=1", p, size=9, formula=True)
    return _save(fig, path)


def _make_projection_geometry(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)

    origin = (1.5, 1.3)
    y_tip = (8.3, 2.25)
    x_tip = (5.7, 4.75)

    _vector_arrow(ax, origin, y_tip, p, color=p["soft"], lw=2.0, label="y")
    _vector_arrow(ax, origin, x_tip, p, color=p["accent"], lw=2.3, label="x")

    proj = _tip_projection(x_tip, origin, y_tip)
    ax.plot([x_tip[0], proj[0]], [x_tip[1], proj[1]], color=p["ghost"], lw=1.2, linestyle="--")
    _vector_arrow(ax, origin, proj, p, color=p["fg"], lw=2.2, label="proj")
    return _save(fig, path)


def _make_projection_symbolic_homework(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.9, 2.8))

    _soft_panel(ax, 0.7, 0.9, 8.6, 4.2, p)

    origin = (1.5, 1.55)
    y_tip = (7.85, 2.1)
    x_tip = (4.15, 4.35)
    proj = _tip_projection(x_tip, origin, y_tip)

    _vector_arrow(ax, origin, x_tip, p, color=p["accent"], lw=2.2, label="x")
    _vector_arrow(ax, origin, y_tip, p, color=p["soft"], lw=2.0, label="y")
    ax.plot([x_tip[0], proj[0]], [x_tip[1], proj[1]], color=p["ghost"], lw=1.0, linestyle="--")
    _vector_arrow(ax, origin, proj, p, color=p["fg"], lw=2.0, label="p")

    _label_text(ax, 7.95, 4.15, "projection", p, size=8.0, color=p["soft"], ha="center")
    _label_text(ax, 7.95, 3.15, "onto a direction", p, size=8.2, color=p["fg"], ha="center")
    _label_text(ax, 7.95, 2.15, "formula in text", p, size=7.8, color=p["soft"], ha="center")
    return _save(fig, path)


def _make_ml_norm_bridge(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)

    _vector_strip(ax, 1.1, 2.65, 5.0, 0.9, p, ["1", "0", "1", "1", "0"], labels=["f1", "f2", "f3", "f4", "f5"])
    ax.add_patch(mpatches.Rectangle((1.3, 1.45), 3.8, 0.40, edgecolor=p["fg"], facecolor=(0, 0, 0, 0), linewidth=1.0))
    ax.add_patch(mpatches.Rectangle((1.3, 1.45), 2.5, 0.40, edgecolor="none", facecolor=p["accent"]))

    _label_text(ax, 6.8, 2.95, "size / magnitude", p, size=8.5, color=p["soft"], ha="left")
    _label_text(ax, 6.8, 2.15, "‖x‖", p, size=10, formula=True, ha="left")
    return _save(fig, path)


def _make_ml_dot_bridge(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)

    _vector_strip(ax, 0.9, 3.35, 3.5, 0.8, p, ["1", "0", "1", "1"])
    _vector_strip(ax, 0.9, 1.85, 3.5, 0.8, p, ["1", "1", "0", "1"])

    for x in [1.35, 2.23, 3.11, 3.99]:
        ax.plot([x, x], [2.65, 3.35], color=p["ghost"], lw=0.9)

    _label_text(ax, 6.1, 2.85, "alignment / score", p, size=8.4, color=p["soft"], ha="left")
    _label_text(ax, 6.1, 2.05, "x·y", p, size=10, formula=True, ha="left")
    return _save(fig, path)


def _make_ml_projection_bridge(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)

    origin = (1.3, 1.4)
    direction_tip = (8.2, 2.2)
    vector_tip = (5.7, 4.4)

    _vector_arrow(ax, origin, direction_tip, p, color=p["soft"], lw=2.0, label="feature dir")
    _vector_arrow(ax, origin, vector_tip, p, color=p["accent"], lw=2.3, label="x")

    proj = _tip_projection(vector_tip, origin, direction_tip)
    ax.plot([vector_tip[0], proj[0]], [vector_tip[1], proj[1]], color=p["ghost"], lw=1.0, linestyle="--")
    _vector_arrow(ax, origin, proj, p, color=p["fg"], lw=2.1, label="component")

    _label_text(ax, 6.4, 4.95, "directional component", p, size=8.2, color=p["soft"])
    return _save(fig, path)


DRAWERS_GEOMETRY = {
    "point_vector_projection_hero": _make_point_vector_projection_hero,
    "point_and_vector_same_coords": _make_point_and_vector_same_coords,
    "vector_difference_geometry": _make_vector_difference_geometry,
    "displacement_geometry": _make_displacement_worked_example,
    "norm_triangle": _make_norm_triangle,
    "norm_worked_geometry": _make_norm_worked_example,
    "dot_product_pairing": _make_dot_product_pairing,
    "dot_product_worked_geometry": _make_dot_product_worked_example,
    "dot_alignment_angle": _make_dot_alignment_angle,
    "angle_recovery_geometry": _make_angle_recovery_geometry,
    "angle_homework_geometry": _make_angle_homework_worked,
    "orthogonal_vectors_geometry": _make_orthogonal_vectors_symbolic,
    "unit_vector_normalization": _make_unit_vector_normalization,
    "projection_geometry": _make_projection_geometry,
    "projection_homework_geometry": _make_projection_symbolic_homework,
    "ml_norm_bridge": _make_ml_norm_bridge,
    "ml_dot_bridge": _make_ml_dot_bridge,
    "ml_projection_bridge": _make_ml_projection_bridge,
}

ALIASES_GEOMETRY = {
    "point_vector_hero": "point_vector_projection_hero",
    "same_coordinates_two_roles": "point_and_vector_same_coords",
    "difference_as_displacement": "vector_difference_geometry",
    "worked_displacement": "displacement_geometry",
    "displacement_worked_example": "displacement_geometry",
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
    "orthogonal_geometry_symbolic": "orthogonal_vectors_geometry",
    "orthogonal_vectors_symbolic": "orthogonal_vectors_geometry",
    "orthogonal_geometry_only": "orthogonal_vectors_geometry",
    "normalized_vector": "unit_vector_normalization",
    "vector_projection": "projection_geometry",
    "homework_projection_symbolic": "projection_homework_geometry",
    "projection_symbolic_homework": "projection_homework_geometry",
    "homework_projection_geometry_only": "projection_homework_geometry",
}

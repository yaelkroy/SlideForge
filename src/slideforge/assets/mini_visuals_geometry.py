from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches

from slideforge.assets.mini_visuals_common import (
    _axes_2d,
    _axes_3d_fake,
    _canvas,
    _label_text,
    _rounded_box,
    _save,
    _soft_panel,
    _tip_projection,
    _vector_arrow,
    _vector_strip,
    palette_for,
)


# Dense worked-example and homework visuals in this module must remain geometry-first.
# Builders should render readable formulas and derivation steps as native PowerPoint text.


PANEL_FILL_ALPHA = 0.06


def _clear_fill(p: dict) -> tuple[float, float, float, float]:
    return (*p["fg"][:3], PANEL_FILL_ALPHA)


def _mini_panel(ax, x: float, y: float, w: float, h: float, p, *, lw: float = 1.0) -> None:
    _rounded_box(ax, x, y, w, h, p, lw=lw, fill=_clear_fill(p))


def _right_angle_marker(ax, x: float, y: float, size: float, p) -> None:
    ax.add_patch(
        mpatches.Rectangle(
            (x, y),
            size,
            size,
            fill=False,
            edgecolor=p["ghost"],
            linewidth=0.9,
        )
    )


def _clean_origin_axes(ax, origin: tuple[float, float], x_to: float, y_to: float, p) -> None:
    ox, oy = origin
    ax.plot([ox, ox], [oy, y_to], color=p["ghost"], lw=0.9)
    ax.plot([ox, x_to], [oy, oy], color=p["ghost"], lw=0.9)



def _make_point_vector_projection_hero(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(7.6, 2.8))
    origin, _, _, _ = _axes_3d_fake(ax, p)

    x_tip = (6.95, 3.95)
    y_tip = (7.85, 2.15)
    proj = _tip_projection(x_tip, origin, y_tip)

    _vector_arrow(ax, origin, x_tip, p, color=p["accent"], lw=2.9, label="x", label_dx=0.18, label_dy=0.10)
    _vector_arrow(ax, origin, y_tip, p, color=p["soft"], lw=2.3, label="y", label_dx=0.18, label_dy=0.02)
    _vector_arrow(ax, origin, proj, p, color=p["fg"], lw=2.4, label="p", label_dx=0.12, label_dy=0.10)
    ax.plot([x_tip[0], proj[0]], [x_tip[1], proj[1]], color=p["ghost"], lw=1.2, linestyle="--")

    ax.add_patch(
        mpatches.Arc(
            origin,
            1.95,
            1.25,
            angle=0,
            theta1=9,
            theta2=34,
            color=p["ghost"],
            lw=1.1,
        )
    )
    _label_text(ax, 2.55, 1.73, "α", p, size=9.5, formula=True)
    return _save(fig, path)



def _make_point_and_vector_same_coords(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.7, 2.8))

    _mini_panel(ax, 0.70, 1.05, 3.95, 3.95, p)
    _mini_panel(ax, 5.35, 1.05, 3.95, 3.95, p)

    # left: point view
    ax.plot([1.35, 1.35], [1.60, 4.45], color=p["ghost"], lw=0.9)
    ax.plot([1.35, 4.05], [1.60, 1.60], color=p["ghost"], lw=0.9)
    ax.add_patch(mpatches.Circle((3.55, 3.42), 0.17, edgecolor=p["fg"], facecolor=p["accent"], lw=1.1))
    _label_text(ax, 2.70, 4.76, "point view", p, size=8.3, color=p["soft"])
    _label_text(ax, 3.54, 1.20, "x", p, size=8.7, formula=True)

    # right: vector view
    ax.plot([6.00, 6.00], [1.60, 4.45], color=p["ghost"], lw=0.9)
    ax.plot([6.00, 8.74], [1.60, 1.60], color=p["ghost"], lw=0.9)
    _vector_arrow(ax, (6.00, 1.60), (8.42, 4.02), p, color=p["accent"], lw=2.35, label="x")
    _label_text(ax, 7.35, 4.76, "vector view", p, size=8.3, color=p["soft"])

    # bridge between views
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



def _make_displacement_worked_example(path: Path, variant: str) -> Path:
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



def _make_norm_worked_example(path: Path, variant: str) -> Path:
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

    left_vals = ["x₁", "x₂", "x₃"]
    right_vals = ["y₁", "y₂", "y₃"]
    ys = [4.35, 3.10, 1.85]

    for val, yy in zip(left_vals, ys):
        _label_text(ax, 2.1, yy, val, p, size=10, formula=True)
    for val, yy in zip(right_vals, ys):
        _label_text(ax, 5.3, yy, val, p, size=10, formula=True)

    for yy in ys:
        ax.plot([2.45, 4.95], [yy, yy], color=p["ghost"], lw=1.0)

    _label_text(ax, 7.8, 3.0, "pairwise", p, size=8.2, color=p["soft"])
    _label_text(ax, 7.8, 2.25, "products", p, size=8.4, color=p["fg"])
    return _save(fig, path)



def _make_dot_product_worked_example(path: Path, variant: str) -> Path:
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

    # left panel: vectors and angle
    origin = (1.75, 1.72)
    x_tip = (4.00, 2.95)
    y_tip = (2.90, 4.25)
    _vector_arrow(ax, origin, x_tip, p, color=p["soft"], lw=2.0, label="x")
    _vector_arrow(ax, origin, y_tip, p, color=p["accent"], lw=2.25, label="y")
    ax.add_patch(mpatches.Arc(origin, 1.25, 1.05, angle=0, theta1=22, theta2=70, color=p["ghost"], lw=1.0))
    _label_text(ax, 2.46, 2.34, "α", p, size=8.4, formula=True)

    # right panel: recovery schematic with norm bars and cosine cue, still diagrammatic
    center = (7.20, 3.02)
    ax.add_patch(mpatches.Circle(center, 0.92, fill=False, edgecolor=p["ghost"], linewidth=1.0))
    ax.plot([6.32, 8.08], [3.02, 3.02], color=p["ghost"], lw=0.95)
    ax.plot([7.20, 7.20], [2.14, 3.90], color=p["ghost"], lw=0.95)
    ax.add_patch(mpatches.Arc(center, 1.25, 1.25, angle=0, theta1=15, theta2=50, color=p["accent"], lw=1.2))
    _label_text(ax, 7.80, 3.56, "α", p, size=8.6, formula=True)
    _label_text(ax, 7.20, 4.46, "recover angle", p, size=7.6, color=p["soft"])
    return _save(fig, path)



def _make_angle_homework_worked(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.9, 2.9))

    _mini_panel(ax, 0.90, 1.05, 8.20, 3.95, p)

    origin = (1.95, 1.62)
    x_tip = (5.55, 4.08)
    y_tip = (7.05, 1.62)

    _vector_arrow(ax, origin, x_tip, p, color=p["accent"], lw=2.25, label="x")
    _vector_arrow(ax, origin, y_tip, p, color=p["soft"], lw=2.05, label="y")
    ax.plot([x_tip[0], x_tip[0]], [x_tip[1], origin[1]], color=p["ghost"], lw=0.9, linestyle="--")
    _right_angle_marker(ax, 5.28, 1.62, 0.26, p)
    ax.add_patch(mpatches.Arc(origin, 1.45, 1.05, angle=0, theta1=7, theta2=34, color=p["ghost"], lw=1.0))
    _label_text(ax, 2.95, 1.95, "α", p, size=8.6, formula=True)
    return _save(fig, path)



def _make_orthogonal_vectors_symbolic(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.9, 2.8))

    _mini_panel(ax, 0.90, 1.00, 8.15, 4.05, p)

    origin = (2.20, 1.60)
    x_tip = (6.55, 1.60)
    y_tip = (2.20, 4.55)

    _vector_arrow(ax, origin, x_tip, p, color=p["soft"], lw=2.15, label="x")
    _vector_arrow(ax, origin, y_tip, p, color=p["accent"], lw=2.20, label="y")
    _right_angle_marker(ax, 2.20, 1.60, 0.34, p)

    # symbolic coordinate blocks, still short and readable
    _mini_panel(ax, 6.95, 2.55, 1.55, 1.55, p, lw=0.9)
    _label_text(ax, 7.72, 3.35, "x·y", p, size=8.6, formula=True)
    _label_text(ax, 7.72, 2.65, "= 0", p, size=8.8, formula=True)
    _label_text(ax, 7.72, 4.52, "90°", p, size=8.9, formula=True, color=p["soft"])
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



def _make_projection_symbolic_homework(path: Path, variant: str) -> Path:
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



def _make_ml_norm_bridge(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)

    _vector_strip(ax, 1.1, 2.65, 5.0, 0.9, p, ["1", "0", "1", "1", "0"], labels=["f1", "f2", "f3", "f4", "f5"])
    ax.add_patch(mpatches.Rectangle((1.3, 1.45), 3.8, 0.40, edgecolor=p["fg"], facecolor=(0, 0, 0, 0), linewidth=1.0))
    ax.add_patch(mpatches.Rectangle((1.3, 1.45), 2.5, 0.40, edgecolor="none", facecolor=p["accent"]))

    _label_text(ax, 6.8, 2.95, "size / magnitude", p, size=8.4, color=p["soft"], ha="left")
    _label_text(ax, 6.8, 2.15, "‖x‖", p, size=10, formula=True, ha="left")
    return _save(fig, path)



def _make_ml_dot_bridge(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)

    _vector_strip(ax, 0.9, 3.35, 3.5, 0.8, p, ["1", "0", "1", "1"])
    _vector_strip(ax, 0.9, 1.85, 3.5, 0.8, p, ["1", "1", "0", "1"])

    for x in [1.35, 2.23, 3.11, 3.99]:
        ax.plot([x, x], [2.65, 3.35], color=p["ghost"], lw=0.9)

    _label_text(ax, 6.1, 2.85, "alignment / score", p, size=8.3, color=p["soft"], ha="left")
    _label_text(ax, 6.1, 2.05, "x·y", p, size=10, formula=True, ha="left")
    return _save(fig, path)



def _make_ml_projection_bridge(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path)

    origin = (1.3, 1.4)
    direction_tip = (8.2, 2.2)
    vector_tip = (5.7, 4.4)

    _vector_arrow(ax, origin, direction_tip, p, color=p["soft"], lw=2.0, label="dir")
    _vector_arrow(ax, origin, vector_tip, p, color=p["accent"], lw=2.3, label="x")

    proj = _tip_projection(vector_tip, origin, direction_tip)
    ax.plot([vector_tip[0], proj[0]], [vector_tip[1], proj[1]], color=p["ghost"], lw=1.0, linestyle="--")
    _vector_arrow(ax, origin, proj, p, color=p["fg"], lw=2.1, label="p")

    _label_text(ax, 6.35, 4.95, "directional component", p, size=8.1, color=p["soft"])
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

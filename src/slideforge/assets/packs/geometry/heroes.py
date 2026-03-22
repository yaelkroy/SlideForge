from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches

from slideforge.assets.mini_visuals_common import (
    _axes_3d_fake,
    _canvas,
    _label_text,
    _save,
    _tip_projection,
    _vector_arrow,
    _vector_strip,
    palette_for,
)


def _make_point_vector_projection_hero(path: Path, variant: str) -> Path:
    """Large, sparse hero graphic for section-divider use.

    This visual deliberately avoids tiny coordinate labels and thin annotation clutter.
    The goal is legibility on dark title slides and in compressed PDF rendering.
    """
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(8.4, 3.7))
    origin, x_end, y_end, z_end = _axes_3d_fake(ax, p)

    # Push the geometry to occupy a much larger readable band.
    point = (6.35, 3.55)
    direction = (8.25, 2.10)
    proj = _tip_projection(point, origin, direction)

    # Main axes slightly emphasized for title-slide readability.
    ax.plot([origin[0], x_end[0]], [origin[1], x_end[1]], color=p["ghost"], lw=1.35)
    ax.plot([origin[0], y_end[0]], [origin[1], y_end[1]], color=p["ghost"], lw=1.35)
    ax.plot([origin[0], z_end[0]], [origin[1], z_end[1]], color=p["ghost"], lw=1.35)

    # Projection construction.
    ax.plot([point[0], proj[0]], [point[1], proj[1]], color=p["ghost"], lw=1.15, linestyle="--")
    ax.plot([point[0], point[0]], [point[1], origin[1]], color=p["ghost"], lw=1.0, linestyle="--")

    _vector_arrow(ax, origin, point, p, color=p["accent"], lw=3.4, label="x", label_dx=0.16, label_dy=0.08)
    _vector_arrow(ax, origin, proj, p, color=p["soft"], lw=2.8, label="p", label_dx=0.16, label_dy=0.08)

    ax.add_patch(mpatches.Circle(point, 0.19, edgecolor=p["fg"], facecolor=p["accent"], lw=1.4))
    ax.add_patch(
        mpatches.Arc(
            (3.15, 1.55),
            1.95,
            1.25,
            angle=0,
            theta1=7,
            theta2=31,
            color=p["ghost"],
            lw=1.2,
        )
    )
    _label_text(ax, 4.05, 2.10, "α", p, size=9.0, formula=True, color=p["soft"])

    # Only a few large labels. No tiny x1/x2/x3 clutter.
    _label_text(ax, 2.55, 4.95, "point", p, size=10.6, color=p["soft"])
    _label_text(ax, 8.65, 4.82, "vector", p, size=10.4, color=p["soft"])
    _label_text(ax, point[0] + 0.18, point[1] + 0.22, "p", p, size=9.2, formula=True)
    return _save(fig, path)


def _make_ml_norm_bridge(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.6, 2.7))
    _vector_strip(ax, 1.1, 2.75, 5.0, 0.92, p, ["1", "0", "1", "1", "0"], labels=["f1", "f2", "f3", "f4", "f5"])
    ax.add_patch(mpatches.Rectangle((1.3, 1.52), 3.8, 0.44, edgecolor=p["fg"], facecolor=(0, 0, 0, 0), linewidth=1.0))
    ax.add_patch(mpatches.Rectangle((1.3, 1.52), 2.5, 0.44, edgecolor="none", facecolor=p["accent"]))
    _label_text(ax, 6.95, 3.05, "size / magnitude", p, size=8.7, color=p["soft"], ha="left")
    _label_text(ax, 6.95, 2.18, "‖x‖", p, size=10.6, formula=True, ha="left")
    return _save(fig, path)



def _make_ml_dot_bridge(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.6, 2.7))
    _vector_strip(ax, 0.95, 3.42, 3.5, 0.82, p, ["1", "0", "1", "1"])
    _vector_strip(ax, 0.95, 1.84, 3.5, 0.82, p, ["1", "1", "0", "1"])
    for x in [1.40, 2.28, 3.16, 4.04]:
        ax.plot([x, x], [2.66, 3.42], color=p["ghost"], lw=0.95)
    _label_text(ax, 6.15, 2.95, "alignment / score", p, size=8.5, color=p["soft"], ha="left")
    _label_text(ax, 6.15, 2.05, "x·y", p, size=10.5, formula=True, ha="left")
    return _save(fig, path)



def _make_ml_projection_bridge(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(4.8, 2.8))
    origin = (1.2, 1.15)
    direction_tip = (8.1, 2.0)
    vector_tip = (5.65, 4.45)
    _vector_arrow(ax, origin, direction_tip, p, color=p["soft"], lw=2.2, label="dir")
    _vector_arrow(ax, origin, vector_tip, p, color=p["accent"], lw=2.55, label="x")
    proj = _tip_projection(vector_tip, origin, direction_tip)
    ax.plot([vector_tip[0], proj[0]], [vector_tip[1], proj[1]], color=p["ghost"], lw=1.05, linestyle="--")
    _vector_arrow(ax, origin, proj, p, color=p["fg"], lw=2.3, label="p")
    _label_text(ax, 6.35, 4.95, "directional component", p, size=8.35, color=p["soft"])
    return _save(fig, path)


DRAWERS = {
    "point_vector_projection_hero": _make_point_vector_projection_hero,
    "ml_norm_bridge": _make_ml_norm_bridge,
    "ml_dot_bridge": _make_ml_dot_bridge,
    "ml_projection_bridge": _make_ml_projection_bridge,
}

ALIASES = {
    "point_vector_hero": "point_vector_projection_hero",
}

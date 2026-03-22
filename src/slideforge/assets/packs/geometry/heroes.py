from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches

from slideforge.assets.mini_visuals_common import _axes_3d_fake, _canvas, _label_text, _mini_panel, _save, _vector_arrow, _vector_strip, palette_for


def _make_point_vector_projection_hero(path: Path, variant: str) -> Path:
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(6.8, 2.9))
    origin, x_end, y_end, z_end = _axes_3d_fake(ax, p)

    point = (6.15, 3.72)
    proj = (8.00, 2.26)

    ax.add_patch(mpatches.Circle(point, 0.20, edgecolor=p["fg"], facecolor=p["accent"], lw=1.35))
    ax.plot([point[0], point[0]], [point[1], origin[1]], color=p["ghost"], lw=1.15, linestyle="--")
    ax.plot([origin[0], point[0]], [origin[1], origin[1]], color=p["ghost"], lw=1.10, linestyle="--")

    _vector_arrow(ax, origin, point, p, color=p["accent"], lw=2.9, label="x", label_dx=0.18, label_dy=0.10)
    _vector_arrow(ax, origin, proj, p, color=p["soft"], lw=2.25, label="y", label_dx=0.16, label_dy=0.06)

    ax.add_patch(mpatches.Arc((3.10, 1.56), 1.55, 1.02, angle=0, theta1=7, theta2=34, color=p["ghost"], lw=1.10))

    _label_text(ax, 2.40, 5.02, "point", p, size=9.2, color=p["soft"])
    _label_text(ax, 8.15, 4.86, "vector", p, size=9.0, color=p["soft"])
    _label_text(ax, point[0] + 0.18, point[1] + 0.18, "p", p, size=8.8, formula=True)
    _label_text(ax, x_end[0] + 0.12, x_end[1] - 0.06, "x₁", p, size=8.4, formula=True)
    _label_text(ax, y_end[0] - 0.12, y_end[1] + 0.08, "x₂", p, size=8.4, formula=True)
    _label_text(ax, z_end[0] - 0.10, z_end[1] + 0.12, "x₃", p, size=8.4, formula=True)
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
    from slideforge.assets.mini_visuals_common import _tip_projection
    proj = _tip_projection(vector_tip, origin, direction_tip)
    ax.plot([vector_tip[0], proj[0]], [vector_tip[1], proj[1]], color=p["ghost"], lw=1.0, linestyle="--")
    _vector_arrow(ax, origin, proj, p, color=p["fg"], lw=2.1, label="p")
    _label_text(ax, 6.35, 4.95, "directional component", p, size=8.1, color=p["soft"])
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

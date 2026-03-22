from __future__ import annotations

from pathlib import Path
from typing import Any

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


VISUAL_METADATA: dict[str, dict[str, Any]] = {
    "point_vector_projection_hero": {
        "preferred_layout": "hero",
        "min_width_in": 7.6,
        "min_height_in": 2.15,
        "preferred_aspect_ratio": 3.8,
        "label_density": "low",
        "text_bearing": False,
        "allow_top_strip": True,
        "hero_simplify_labels": True,
    },
    "ml_norm_bridge": {
        "preferred_layout": "top_visual",
        "min_width_in": 3.8,
        "min_height_in": 1.6,
        "preferred_aspect_ratio": 2.2,
        "label_density": "medium",
        "text_bearing": False,
        "allow_top_strip": True,
    },
    "ml_dot_bridge": {
        "preferred_layout": "top_visual",
        "min_width_in": 3.8,
        "min_height_in": 1.6,
        "preferred_aspect_ratio": 2.2,
        "label_density": "medium",
        "text_bearing": False,
        "allow_top_strip": True,
    },
    "ml_projection_bridge": {
        "preferred_layout": "top_visual",
        "min_width_in": 4.0,
        "min_height_in": 1.7,
        "preferred_aspect_ratio": 2.3,
        "label_density": "medium",
        "text_bearing": False,
        "allow_top_strip": True,
    },
}


def get_visual_metadata(kind: str) -> dict[str, Any]:
    return dict(VISUAL_METADATA.get(str(kind or "").strip(), {}))


def _make_point_vector_projection_hero(path: Path, variant: str) -> Path:
    """True title-slide hero.

    This version intentionally suppresses instructional labels such as
    "point" / "vector" and instead shows one bold geometric relation with
    thicker strokes and a larger occupied band.
    """
    p = palette_for(variant)
    fig, ax = _canvas(path, figsize=(9.2, 3.9))
    origin, x_end, y_end, z_end = _axes_3d_fake(ax, p)

    point = (6.65, 3.70)
    direction = (8.95, 2.02)
    proj = _tip_projection(point, origin, direction)
    helper_tip = (4.55, 3.22)

    # Emphasized axes.
    ax.plot([origin[0], x_end[0]], [origin[1], x_end[1]], color=p["ghost"], lw=1.6)
    ax.plot([origin[0], y_end[0]], [origin[1], y_end[1]], color=p["ghost"], lw=1.55)
    ax.plot([origin[0], z_end[0]], [origin[1], z_end[1]], color=p["ghost"], lw=1.55)

    # Large hero vectors.
    _vector_arrow(ax, origin, point, p, color=p["fg"], lw=3.75, label="", label_dx=0.0, label_dy=0.0)
    _vector_arrow(ax, origin, proj, p, color=p["soft"], lw=3.15, label="", label_dx=0.0, label_dy=0.0)
    _vector_arrow(ax, origin, helper_tip, p, color=p["accent"], lw=2.1, label="", label_dx=0.0, label_dy=0.0)

    # Projection construction kept, but lighter and cleaner.
    ax.plot([point[0], proj[0]], [point[1], proj[1]], color=p["ghost"], lw=1.2, linestyle="--")
    ax.plot([point[0], point[0]], [point[1], origin[1]], color=p["ghost"], lw=1.05, linestyle="--")

    # Dominant point marker.
    ax.add_patch(mpatches.Circle(point, 0.21, edgecolor=p["fg"], facecolor=p["accent"], lw=1.4))

    # Simple angle cue only.
    ax.add_patch(
        mpatches.Arc(
            (3.45, 1.55),
            2.20,
            1.38,
            angle=0,
            theta1=7,
            theta2=31,
            color=p["ghost"],
            lw=1.25,
        )
    )
    _label_text(ax, 4.52, 2.08, "α", p, size=9.5, formula=True, color=p["soft"])

    # Only a couple of large labels.
    _label_text(ax, point[0] + 0.20, point[1] + 0.20, "P", p, size=9.8, formula=True)
    _label_text(ax, proj[0] + 0.16, proj[1] - 0.12, "p", p, size=9.0, formula=True)

    # Reduce empty padding so the visual occupies the hero band.
    ax.set_xlim(0.35, 10.0)
    ax.set_ylim(0.70, 5.55)
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

from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

from slideforge.config.constants import (
    ACCENT,
    BODY_FONT,
    FORMULA_FONT,
    GHOST_TEXT,
    MPL_BODY_FONT,
    MPL_FORMULA_FONT,
    NAVY,
    OFFWHITE,
    SLATE,
    TITLE_PANEL_LINE,
)
from slideforge.config.paths import GENERATED_DIR
from slideforge.render.primitives import add_textbox
from slideforge.utils.units import inches


def _mpl(rgb) -> tuple[float, float, float]:
    return tuple(channel / 255 for channel in rgb)


PALETTES = {
    "dark_on_light": {
        "fg": _mpl(NAVY),
        "soft": _mpl(SLATE),
        "accent": _mpl(ACCENT),
        "ghost": _mpl(GHOST_TEXT),
        "bg_soft": (0.92, 0.95, 1.0, 0.16),
        "bg_alt": (0.88, 0.92, 1.0, 0.10),
        "panel": (0.94, 0.96, 1.0, 0.35),
    },
    "light_on_dark": {
        "fg": _mpl(OFFWHITE),
        "soft": _mpl(TITLE_PANEL_LINE),
        "accent": _mpl(TITLE_PANEL_LINE),
        "ghost": _mpl(GHOST_TEXT),
        "bg_soft": (1.0, 1.0, 1.0, 0.08),
        "bg_alt": (1.0, 1.0, 1.0, 0.05),
        "panel": (1.0, 1.0, 1.0, 0.10),
    },
}


def palette_for(variant: str) -> dict:
    return PALETTES.get(variant, PALETTES["dark_on_light"])


def add_image(slide, image_path: Path, x: float, y: float, w: float, h: float) -> None:
    slide.shapes.add_picture(
        str(image_path),
        inches(x),
        inches(y),
        width=inches(w),
        height=inches(h),
    )


def _canvas(path: Path, figsize: tuple[float, float] = (4.2, 2.4)):
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_alpha(0.0)
    ax.set_facecolor((1, 1, 1, 0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    return fig, ax


def _save(fig, path: Path) -> Path:
    fig.tight_layout(pad=0.05)
    fig.savefig(path, dpi=260, bbox_inches="tight", transparent=True)
    plt.close(fig)
    return path


def _label_text(
    ax,
    x: float,
    y: float,
    text: str,
    p,
    *,
    size: float = 8.0,
    formula: bool = False,
    ha: str = "center",
    va: str = "center",
    color=None,
) -> None:
    ax.text(
        x,
        y,
        text,
        ha=ha,
        va=va,
        fontsize=size,
        color=p["fg"] if color is None else color,
        fontfamily=MPL_FORMULA_FONT if formula else MPL_BODY_FONT,
    )


def _rounded_box(ax, x: float, y: float, w: float, h: float, p, *, lw: float = 1.3, fill=None) -> None:
    ax.add_patch(
        mpatches.FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.18",
            linewidth=lw,
            edgecolor=p["fg"],
            facecolor=p["panel"] if fill is None else fill,
        )
    )


def _soft_panel(ax, x: float, y: float, w: float, h: float, p) -> None:
    _rounded_box(ax, x, y, w, h, p, lw=1.1, fill=p["panel"])


def _movie_icon(ax, x: float, y: float, w: float, h: float, p) -> None:
    _rounded_box(ax, x, y, w, h, p, lw=1.5, fill=(0, 0, 0, 0))
    ax.plot([x + 0.20, x + w - 0.20], [y + h * 0.72, y + h * 0.72], color=p["soft"], lw=1.1)
    cx = x + w / 2
    cy = y + h * 0.34
    tri_w = w * 0.22
    tri_h = h * 0.24
    triangle = mpatches.Polygon(
        [
            (cx - tri_w * 0.40, cy - tri_h / 2),
            (cx - tri_w * 0.40, cy + tri_h / 2),
            (cx + tri_w * 0.60, cy),
        ],
        closed=True,
        edgecolor=p["accent"],
        facecolor=p["accent"],
        linewidth=1.0,
    )
    ax.add_patch(triangle)


def _digit_card_shape(ax, x: float, y: float, w: float, h: float, p, digit: str = "7") -> None:
    _rounded_box(ax, x, y, w, h, p, lw=1.5, fill=(0, 0, 0, 0))
    _label_text(ax, x + w / 2, y + h / 2, digit, p, size=20, formula=True, color=p["accent"])


def _vector_strip(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    p,
    values: list[str],
    *,
    labels: list[str] | None = None,
) -> None:
    gap = 0.12
    cell_w = (w - gap * (len(values) - 1)) / len(values)
    for i, v in enumerate(values):
        cell_x = x + i * (cell_w + gap)
        face = p["bg_soft"] if v not in {"1", "x"} else p["accent"]
        rect = mpatches.Rectangle(
            (cell_x, y),
            cell_w,
            h,
            linewidth=1.2,
            edgecolor=p["fg"],
            facecolor=face,
        )
        ax.add_patch(rect)
        txt_color = (1, 1, 1) if v in {"1", "x"} else p["fg"]
        _label_text(
            ax,
            cell_x + cell_w / 2,
            y + h / 2,
            v,
            p,
            size=10,
            formula=True,
            color=txt_color,
        )
        if labels and i < len(labels):
            _label_text(
                ax,
                cell_x + cell_w / 2,
                y - 0.16,
                labels[i],
                p,
                size=6.8,
                ha="center",
                va="top",
                color=p["soft"],
            )


def _axes_2d(ax, p) -> None:
    ax.plot([1.0, 1.0], [0.9, 5.1], color=p["ghost"], lw=1.0)
    ax.plot([1.0, 9.0], [0.9, 0.9], color=p["ghost"], lw=1.0)
    ax.annotate("", xy=(1.0, 5.1), xytext=(1.0, 0.9), arrowprops=dict(arrowstyle="-|>", lw=1.0, color=p["ghost"]))
    ax.annotate("", xy=(9.0, 0.9), xytext=(1.0, 0.9), arrowprops=dict(arrowstyle="-|>", lw=1.0, color=p["ghost"]))


def _axes_3d_fake(ax, p) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]]:
    origin = (1.4, 1.1)
    x_end = (8.6, 1.1)
    y_end = (4.4, 3.2)
    z_end = (1.4, 5.3)
    ax.annotate("", xy=x_end, xytext=origin, arrowprops=dict(arrowstyle="-|>", lw=1.1, color=p["ghost"]))
    ax.annotate("", xy=y_end, xytext=origin, arrowprops=dict(arrowstyle="-|>", lw=1.1, color=p["ghost"]))
    ax.annotate("", xy=z_end, xytext=origin, arrowprops=dict(arrowstyle="-|>", lw=1.1, color=p["ghost"]))
    return origin, x_end, y_end, z_end


def _vector_arrow(
    ax,
    start: tuple[float, float],
    end: tuple[float, float],
    p,
    *,
    color=None,
    lw: float = 2.2,
    label: str | None = None,
    label_dx: float = 0.12,
    label_dy: float = 0.12,
) -> None:
    use_color = p["accent"] if color is None else color
    ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="-|>", lw=lw, color=use_color))
    if label:
        _label_text(ax, end[0] + label_dx, end[1] + label_dy, label, p, size=8.8, formula=True, color=p["fg"])


def _draw_checkmark(ax, cx: float, cy: float, size: float, color, *, lw: float = 2.2) -> None:
    x1 = cx - size * 0.40
    y1 = cy - size * 0.02
    x2 = cx - size * 0.10
    y2 = cy - size * 0.28
    x3 = cx + size * 0.42
    y3 = cy + size * 0.28
    ax.plot([x1, x2], [y1, y2], color=color, lw=lw, solid_capstyle="round")
    ax.plot([x2, x3], [y2, y3], color=color, lw=lw, solid_capstyle="round")


def _tip_projection(point: tuple[float, float], line_start: tuple[float, float], line_end: tuple[float, float]) -> tuple[float, float]:
    px, py = point
    ax, ay = line_start
    bx, by = line_end
    vx, vy = bx - ax, by - ay
    wx, wy = px - ax, py - ay
    denom = vx * vx + vy * vy
    if denom == 0:
        return line_start
    t = (wx * vx + wy * vy) / denom
    return (ax + t * vx, ay + t * vy)
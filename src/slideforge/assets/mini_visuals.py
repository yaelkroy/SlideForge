from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from pptx.enum.shapes import MSO_SHAPE

from slideforge.config.constants import ACCENT, FORMULA_FONT, SLATE
from slideforge.config.paths import GENERATED_DIR
from slideforge.render.primitives import add_arrow, add_textbox
from slideforge.utils.units import inches


def add_image(slide, image_path: Path, x: float, y: float, w: float, h: float) -> None:
    slide.shapes.add_picture(
        str(image_path),
        inches(x), inches(y),
        width=inches(w),
        height=inches(h),
    )


def create_gaussian_plot(filename: str = "gaussian_curve.png") -> Path:
    path = GENERATED_DIR / filename

    x = np.linspace(-4, 4, 400)
    y = (1 / np.sqrt(2 * np.pi)) * np.exp(-(x ** 2) / 2)

    fig, ax = plt.subplots(figsize=(4, 2.2))
    ax.plot(x, y)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight", transparent=True)
    plt.close(fig)

    return path


def create_loss_curve_plot(filename: str = "loss_curve.png") -> Path:
    path = GENERATED_DIR / filename

    x = np.linspace(-2.5, 2.5, 400)
    y = 0.5 * x**2 + 0.2 * x + 0.6

    fig, ax = plt.subplots(figsize=(4, 2.2))
    ax.plot(x, y)
    ax.scatter([0], [0.6], s=30)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight", transparent=True)
    plt.close(fig)

    return path


def create_scatter_separator_plot(filename: str = "scatter_separator_plot.png") -> Path:
    path = GENERATED_DIR / filename

    pos = np.array([[1.0, 2.1], [1.6, 2.5], [2.0, 2.0]])
    neg = np.array([[3.1, 0.9], [3.4, 1.4], [2.7, 1.0]])

    fig, ax = plt.subplots(figsize=(3.2, 1.8))
    ax.scatter(pos[:, 0], pos[:, 1], marker="o", s=28)
    ax.scatter(neg[:, 0], neg[:, 1], marker="x", s=28)
    xx = np.linspace(0.6, 3.8, 100)
    yy = -0.7 * xx + 3.45
    ax.plot(xx, yy, linewidth=1.4)
    ax.set_xlim(0.4, 4.0)
    ax.set_ylim(0.4, 3.0)
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ax.spines.values():
        side.set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=220, bbox_inches="tight", transparent=True)
    plt.close(fig)
    return path


def create_vector_point_plot(filename: str = "vector_point_plot.png") -> Path:
    path = GENERATED_DIR / filename

    fig, ax = plt.subplots(figsize=(3.2, 1.8))
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 3)
    ax.arrow(0.4, 0.4, 2.2, 1.4, head_width=0.12, head_length=0.16, length_includes_head=True)
    ax.scatter([2.6], [1.8], s=20)
    ax.plot([0.4, 2.6], [0.4, 1.8], linewidth=1.2)
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ax.spines.values():
        side.set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=220, bbox_inches="tight", transparent=True)
    plt.close(fig)
    return path


def create_plane_normal_plot(filename: str = "plane_normal_plot.png") -> Path:
    path = GENERATED_DIR / filename

    fig, ax = plt.subplots(figsize=(3.2, 1.8))
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 3)
    ax.plot([0.6, 3.3], [0.9, 2.2], linewidth=1.6)
    ax.arrow(2.0, 1.55, -0.45, 0.75, head_width=0.12, head_length=0.15, length_includes_head=True)
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ax.spines.values():
        side.set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=220, bbox_inches="tight", transparent=True)
    plt.close(fig)
    return path


def create_array_icon_plot(filename: str = "array_icon_plot.png") -> Path:
    path = GENERATED_DIR / filename

    fig, ax = plt.subplots(figsize=(3.2, 1.8))
    ax.axis("off")
    ax.text(
        0.5, 0.5,
        "[1, 0, 1]\n[0, 1, 1]",
        ha="center", va="center",
        fontsize=14,
        family="DejaVu Sans Mono",
    )
    fig.tight_layout()
    fig.savefig(path, dpi=220, bbox_inches="tight", transparent=True)
    plt.close(fig)
    return path


def add_mini_visual(slide, kind: str, x: float, y: float, w: float, h: float, suffix: str = "") -> None:
    if kind == "vector_point_plane_combo" or kind == "vector_arrow":
        img = create_vector_point_plot(f"vector_point{suffix}.png")
        add_image(slide, img, x, y, w, h)
    elif kind == "plane_slice_with_normal" or kind == "plane_slice":
        img = create_plane_normal_plot(f"plane_normal{suffix}.png")
        add_image(slide, img, x, y, w, h)
    elif kind == "loss_curve_with_descent_arrow" or kind == "bowl_surface_with_downhill_arrow":
        img = create_loss_curve_plot(f"loss_curve{suffix}.png")
        add_image(slide, img, x, y, w, h)
    elif kind == "scatter_with_boundary_and_classes" or kind == "scatter_separator":
        img = create_scatter_separator_plot(f"scatter_separator{suffix}.png")
        add_image(slide, img, x, y, w, h)
    elif kind == "array_or_code_brackets":
        img = create_array_icon_plot(f"array_icon{suffix}.png")
        add_image(slide, img, x, y, w, h)
    elif kind == "vector_arrow_and_plane_slice":
        add_arrow(slide, x + 0.15, y + h - 0.15, x + w - 0.2, y + 0.2, color=ACCENT)
        line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            inches(x + 0.15), inches(y + h * 0.65),
            inches(w - 0.3), inches(0.03)
        )
        line.fill.solid()
        line.fill.fore_color.rgb = SLATE
        line.line.color.rgb = SLATE
    elif kind == "gaussian_curve":
        img = create_gaussian_plot(f"gaussian_curve{suffix}.png")
        add_image(slide, img, x, y, w, h)
    else:
        add_textbox(
            slide,
            x=x, y=y, w=w, h=h,
            text=kind,
            font_name=FORMULA_FONT,
            font_size=10,
            color=SLATE,
            bold=False,
        )
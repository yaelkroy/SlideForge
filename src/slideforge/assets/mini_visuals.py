from __future__ import annotations

from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals_common import (
    BODY_FONT,
    FORMULA_FONT,
    OFFWHITE,
    SLATE,
    add_image,
    add_textbox,
    GENERATED_DIR,
)
from slideforge.assets.mini_visuals_core import ALIASES_CORE, DRAWERS_CORE
from slideforge.assets.mini_visuals_geometry import ALIASES_GEOMETRY, DRAWERS_GEOMETRY


DRAWERS = {
    **DRAWERS_CORE,
    **DRAWERS_GEOMETRY,
}

ALIASES = {
    **ALIASES_CORE,
    **ALIASES_GEOMETRY,
}


def _render_visual(kind: str, suffix: str, variant: str):
    canonical = ALIASES.get(kind, kind)
    if canonical not in DRAWERS:
        raise KeyError(f"Unknown mini visual kind: {kind}")
    safe_name = canonical.replace("/", "_").replace(" ", "_")
    path = GENERATED_DIR / f"{safe_name}_{variant}{suffix}.png"
    return DRAWERS[canonical](path, variant)


def add_mini_visual(
    slide,
    kind: str,
    x: float,
    y: float,
    w: float,
    h: float,
    suffix: str = "",
    variant: str = "dark_on_light",
) -> None:
    if not kind:
        return
    try:
        img = _render_visual(kind, suffix=suffix, variant=variant)
        add_image(slide, img, x, y, w, h)
    except Exception:
        add_textbox(
            slide,
            x=x,
            y=y,
            w=w,
            h=h,
            text=kind,
            font_name=FORMULA_FONT,
            font_size=10,
            color=SLATE if variant == "dark_on_light" else OFFWHITE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )


def add_visual_with_caption(
    slide,
    kind: str,
    x: float,
    y: float,
    w: float,
    h: float,
    caption: str = "",
    suffix: str = "",
    variant: str = "dark_on_light",
    caption_font_size: int = 9,
) -> None:
    if not caption:
        add_mini_visual(
            slide,
            kind=kind,
            x=x,
            y=y,
            w=w,
            h=h,
            suffix=suffix,
            variant=variant,
        )
        return

    visual_h = max(0.1, h - 0.22)
    add_mini_visual(
        slide,
        kind=kind,
        x=x,
        y=y,
        w=w,
        h=visual_h,
        suffix=suffix,
        variant=variant,
    )

    add_textbox(
        slide,
        x=x,
        y=y + visual_h + 0.02,
        w=w,
        h=0.18,
        text=caption,
        font_name=BODY_FONT,
        font_size=caption_font_size,
        color=SLATE if variant == "dark_on_light" else OFFWHITE,
        bold=False,
        align=PP_ALIGN.CENTER,
    )
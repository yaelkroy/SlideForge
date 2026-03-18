from __future__ import annotations

from typing import Any

from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import BODY_FONT, OFFWHITE, TITLE_FONT, TITLE_PANEL_LINE, WHITE
from slideforge.io.backgrounds import choose_background
from slideforge.render.primitives import (
    add_pill_tag,
    add_soft_connector,
    add_textbox,
    add_title_panel,
)


def _add_pill_row(slide, bullets: list[str], region: dict[str, float]) -> None:
    if not bullets:
        return

    x = region["x"]
    y = region["y"]
    w = region["w"]
    h = region["h"]

    visible = bullets[:3]
    gap = 0.18
    total_gap = gap * (len(visible) - 1)
    pill_w = (w - total_gap) / len(visible)

    for i, bullet in enumerate(visible):
        pill_x = x + i * (pill_w + gap)
        add_pill_tag(slide, pill_x, y, pill_w, h, bullet)


def build_title_composite_slide(prs, spec: dict[str, Any], counters: dict[str, int]) -> None:
    bg = spec.get("background") or choose_background("title", counters)
    slide = new_slide(prs, bg)

    layout = spec.get("layout", {})
    title_y = layout.get("title_y", 0.92)
    subtitle_y = layout.get("subtitle_y", 2.02)
    author_y = layout.get("author_y", 2.72)
    bullets_region = layout.get(
        "bullets_region",
        {"x": 3.0, "y": 5.42, "w": 7.4, "h": 0.34},
    )
    tiny_footer_region = layout.get(
        "tiny_footer_region",
        {"x": 2.0, "y": 6.36, "w": 9.35, "h": 0.22},
    )

    add_textbox(
        slide,
        x=0.75,
        y=title_y,
        w=11.8,
        h=1.0,
        text=spec["title"],
        font_name=TITLE_FONT,
        font_size=24,
        color=WHITE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )

    subtitle = spec.get("subtitle", "")
    if subtitle:
        add_textbox(
            slide,
            x=1.15,
            y=subtitle_y,
            w=11.0,
            h=0.4,
            text=subtitle,
            font_name=BODY_FONT,
            font_size=17,
            color=OFFWHITE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    if spec.get("show_author_line", True):
        add_textbox(
            slide,
            x=3.6,
            y=author_y,
            w=6.1,
            h=0.35,
            text=spec.get("author_line", "Dr. Yael Demedetskaya"),
            font_name=BODY_FONT,
            font_size=17,
            color=OFFWHITE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    composite = spec.get("composite_visual", {})
    panels = composite.get("panels", [])

    for idx, panel in enumerate(panels):
        add_title_panel(
            slide,
            x=panel["x"],
            y=panel["y"],
            w=panel["w"],
            h=panel["h"],
            title=panel["label"],
            embedded_label=panel.get("embedded_label", ""),
        )

        mini_kind = panel.get("mini_visual", "").strip()
        if mini_kind:
            add_mini_visual(
                slide,
                kind=mini_kind,
                x=panel["x"] + 0.22,
                y=panel["y"] + 0.28,
                w=panel["w"] - 0.44,
                h=0.66,
                suffix=f"_title_{idx}",
            )

    connectors = composite.get("connectors", [])
    for conn in connectors:
        p1 = panels[conn["from"]]
        p2 = panels[conn["to"]]
        add_soft_connector(
            slide,
            x1=p1["x"] + p1["w"],
            y1=p1["y"] + p1["h"] / 2,
            x2=p2["x"],
            y2=p2["y"] + p2["h"] / 2,
            color=TITLE_PANEL_LINE,
            width_pt=1.4,
        )

    _add_pill_row(slide, spec.get("bullets", []), bullets_region)

    tiny_footer = spec.get("tiny_footer", "")
    if tiny_footer:
        add_textbox(
            slide,
            x=tiny_footer_region["x"],
            y=tiny_footer_region["y"],
            w=tiny_footer_region["w"],
            h=tiny_footer_region["h"],
            text=tiny_footer,
            font_name=BODY_FONT,
            font_size=10,
            color=OFFWHITE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )
from __future__ import annotations

from typing import Any

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

from slideforge.config.constants import (
    TITLE_FONT,
    BODY_FONT,
    WHITE,
    OFFWHITE,
    TITLE_PANEL_LINE,
)
from slideforge.io.backgrounds import choose_background
from slideforge.render.primitives import (
    add_textbox,
    add_soft_connector,
    add_pill_tag,
    add_title_panel,
)
from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.basic import new_slide


def build_title_composite_slide(prs: Presentation, spec: dict[str, Any], counters: dict[str, int]) -> None:
    bg = spec.get("background") or choose_background("title", counters)
    slide = new_slide(prs, bg)

    add_textbox(
        slide,
        x=0.75,
        y=0.92,
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
            y=2.02,
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
            y=2.72,
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

        add_mini_visual(
            slide,
            kind=panel.get("mini_visual", ""),
            x=panel["x"] + 0.22,
            y=panel["y"] + 0.28,
            w=panel["w"] - 0.44,
            h=0.66,
            suffix=f"_title_{idx}",
        )

    for conn in composite.get("connectors", []):
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

    bullets = spec.get("bullets", [])
    if len(bullets) >= 3:
        tag_y = 5.42
        add_pill_tag(slide, 3.0, tag_y, 2.35, 0.34, bullets[0])
        add_pill_tag(slide, 5.52, tag_y, 2.28, 0.34, bullets[1])
        add_pill_tag(slide, 7.95, tag_y, 2.45, 0.34, bullets[2])

    tiny_footer = spec.get("tiny_footer", "")
    if tiny_footer:
        add_textbox(
            slide,
            x=2.0,
            y=6.36,
            w=9.35,
            h=0.22,
            text=tiny_footer,
            font_name=BODY_FONT,
            font_size=10,
            color=OFFWHITE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )
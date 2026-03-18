from __future__ import annotations

from typing import Any

from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_visual_with_caption
from slideforge.builders.common import new_slide
from slideforge.config.constants import ACCENT, BODY_FONT, BOX_LINE, LIGHT_BOX_FILL, NAVY, SLATE, TITLE_FONT
from slideforge.io.backgrounds import choose_background
from slideforge.render.primitives import (
    add_bullets_box,
    add_divider_line,
    add_footer,
    add_hub_box,
    add_node_box,
    add_rounded_box,
    add_soft_connector,
    add_textbox,
)


def build_dependency_map_slide(prs, spec: dict[str, Any], counters: dict[str, int]) -> None:
    theme = spec.get("theme", "concept")
    bg = spec.get("background") or choose_background(theme, counters)
    slide = new_slide(prs, bg)

    layout = spec.get("layout", {})
    title_y = layout.get("title_y", 0.42)

    add_textbox(
        slide,
        x=0.8,
        y=title_y,
        w=11.7,
        h=0.5,
        text=spec["title"],
        font_name=TITLE_FONT,
        font_size=24,
        color=NAVY,
        bold=True,
    )
    add_divider_line(slide, dark=False)

    diagram = spec["diagram"]
    center = diagram["center_node"]
    nodes = diagram["input_nodes"]

    for node in nodes:
        if node["x"] < center["x"]:
            x1 = node["x"] + node["w"]
            y1 = node["y"] + node["h"] / 2
            x2 = center["x"]
            y2 = center["y"] + center["h"] / 2
        else:
            x1 = node["x"]
            y1 = node["y"] + node["h"] / 2
            x2 = center["x"] + center["w"]
            y2 = center["y"] + center["h"] / 2

        add_soft_connector(slide, x1=x1, y1=y1, x2=x2, y2=y2, color=ACCENT, width_pt=1.35)

    add_hub_box(
        slide,
        x=center["x"],
        y=center["y"],
        w=center["w"],
        h=center["h"],
        text=center["label"],
    )

    for idx, node in enumerate(nodes):
        add_node_box(
            slide,
            x=node["x"],
            y=node["y"],
            w=node["w"],
            h=node["h"],
            text=node["label"],
            fill_color=LIGHT_BOX_FILL,
            line_color=BOX_LINE,
            text_color=NAVY,
            font_size=node.get("font_size", 14),
            bold=True,
        )

        mini_kind = node.get("mini_visual", "").strip()
        callout = node.get("callout", "").strip()

        if mini_kind:
            safe_suffix = f"_dep_{idx}"
            if node["y"] < center["y"]:
                visual_y = node["y"] - 0.60
            else:
                visual_y = node["y"] + node["h"] + 0.10

            add_visual_with_caption(
                slide,
                kind=mini_kind,
                x=node["x"] + 0.10,
                y=visual_y,
                w=node["w"] - 0.20,
                h=0.62,
                caption=callout,
                suffix=safe_suffix,
                variant="dark_on_light",
                caption_font_size=9,
            )

    exp = spec.get("explanation_box", {})
    exp_box = layout.get("explanation_box")
    if exp_box and exp and exp.get("text", "").strip():
        add_textbox(
            slide,
            x=exp_box["x"] + 0.03,
            y=exp_box["y"] - layout.get("box_title_gap", 0.34),
            w=exp_box["w"] - 0.06,
            h=layout.get("box_title_h", 0.24),
            text=exp.get("title", "Core idea"),
            font_name=BODY_FONT,
            font_size=layout.get("box_title_font_size", 13),
            color=SLATE,
            bold=True,
        )

        add_rounded_box(slide, exp_box["x"], exp_box["y"], exp_box["w"], exp_box["h"])

        add_textbox(
            slide,
            x=exp_box["x"] + layout.get("box_inner_pad_x", 0.16),
            y=exp_box["y"] + layout.get("box_inner_pad_y", 0.16),
            w=exp_box["w"] - 2 * layout.get("box_inner_pad_x", 0.16),
            h=exp_box["h"] - 2 * layout.get("box_inner_pad_y", 0.16),
            text=exp["text"],
            font_name=BODY_FONT,
            font_size=layout.get("note_text_font_size", 13),
            color=SLATE,
            bold=False,
        )

    right_bullets = spec.get("right_panel_bullets", [])
    bullets_box = layout.get("bullets_box")
    if bullets_box and right_bullets:
        add_textbox(
            slide,
            x=bullets_box["x"] + 0.03,
            y=bullets_box["y"] - layout.get("box_title_gap", 0.34),
            w=bullets_box["w"] - 0.06,
            h=layout.get("box_title_h", 0.24),
            text=spec.get("right_panel_title", "Why this matters"),
            font_name=BODY_FONT,
            font_size=layout.get("box_title_font_size", 13),
            color=SLATE,
            bold=True,
        )

        add_rounded_box(slide, bullets_box["x"], bullets_box["y"], bullets_box["w"], bullets_box["h"])

        add_bullets_box(
            slide,
            x=bullets_box["x"] + layout.get("box_inner_pad_x", 0.16),
            y=bullets_box["y"] + layout.get("box_inner_pad_y", 0.16),
            w=bullets_box["w"] - 2 * layout.get("box_inner_pad_x", 0.16),
            h=bullets_box["h"] - 2 * layout.get("box_inner_pad_y", 0.16),
            bullets=right_bullets,
            color=NAVY,
            top_font_size=layout.get("bullet_font_size", 11),
            sub_font_size=layout.get("bullet_sub_font_size", 10),
        )

    takeaway = spec.get("takeaway", "").strip()
    takeaway_box = layout.get("takeaway_box")
    if takeaway and takeaway_box:
        add_rounded_box(slide, takeaway_box["x"], takeaway_box["y"], takeaway_box["w"], takeaway_box["h"])
        add_textbox(
            slide,
            x=takeaway_box["x"] + 0.16,
            y=takeaway_box["y"] + 0.06,
            w=takeaway_box["w"] - 0.32,
            h=takeaway_box["h"] - 0.08,
            text=takeaway,
            font_name=BODY_FONT,
            font_size=layout.get("takeaway_font_size", 12),
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    add_footer(slide, dark=False)
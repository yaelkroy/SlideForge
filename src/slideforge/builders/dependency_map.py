from __future__ import annotations

from typing import Any

from pptx.enum.text import PP_ALIGN

from slideforge.assets.mini_visuals import add_mini_visual
from slideforge.builders.common import new_slide
from slideforge.config.constants import (
    ACCENT,
    BODY_FONT,
    BOX_LINE,
    LIGHT_BOX_FILL,
    NAVY,
    SLATE,
    TITLE_FONT,
)
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

    box_title_gap = layout.get("box_title_gap", 0.36)
    box_title_h = layout.get("box_title_h", 0.24)
    box_title_font_size = layout.get("box_title_font_size", 13)

    box_inner_pad_x = layout.get("box_inner_pad_x", 0.16)
    box_inner_pad_y = layout.get("box_inner_pad_y", 0.16)

    note_text_font_size = layout.get("note_text_font_size", 13)
    bullet_font_size = layout.get("bullet_font_size", 11)
    bullet_sub_font_size = layout.get("bullet_sub_font_size", 10)
    takeaway_font_size = layout.get("takeaway_font_size", 12)

    connector_width_pt = layout.get("connector_width_pt", 1.3)

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

        add_soft_connector(
            slide,
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2,
            color=ACCENT,
            width_pt=connector_width_pt,
        )

    add_hub_box(
        slide,
        x=center["x"],
        y=center["y"],
        w=center["w"],
        h=center["h"],
        text=center["label"],
    )

    for node in nodes:
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
        if mini_kind:
            safe_suffix = (
                node["label"]
                .replace("\n", "_")
                .replace("/", "_")
                .replace(" ", "_")
            )
            add_mini_visual(
                slide,
                kind=mini_kind,
                x=node["x"] + 0.18,
                y=node["y"] - 0.58,
                w=node["w"] - 0.36,
                h=0.42,
                suffix=f"_dep_{safe_suffix}",
            )

    exp = spec.get("explanation_box", {})
    exp_box = layout.get("explanation_box")
    if exp_box and exp and exp.get("text", "").strip():
        add_textbox(
            slide,
            x=exp_box["x"] + 0.03,
            y=exp_box["y"] - box_title_gap,
            w=exp_box["w"] - 0.06,
            h=box_title_h,
            text=exp.get("title", "Core idea"),
            font_name=BODY_FONT,
            font_size=box_title_font_size,
            color=SLATE,
            bold=True,
        )

        add_rounded_box(
            slide,
            exp_box["x"],
            exp_box["y"],
            exp_box["w"],
            exp_box["h"],
        )

        add_textbox(
            slide,
            x=exp_box["x"] + box_inner_pad_x,
            y=exp_box["y"] + box_inner_pad_y,
            w=exp_box["w"] - 2 * box_inner_pad_x,
            h=exp_box["h"] - 2 * box_inner_pad_y,
            text=exp["text"],
            font_name=BODY_FONT,
            font_size=note_text_font_size,
            color=SLATE,
            bold=False,
        )

    right_bullets = spec.get("right_panel_bullets", [])
    bullets_box = layout.get("bullets_box")
    if bullets_box and right_bullets:
        add_textbox(
            slide,
            x=bullets_box["x"] + 0.03,
            y=bullets_box["y"] - box_title_gap,
            w=bullets_box["w"] - 0.06,
            h=box_title_h,
            text=spec.get("right_panel_title", "Why this matters"),
            font_name=BODY_FONT,
            font_size=box_title_font_size,
            color=SLATE,
            bold=True,
        )

        add_rounded_box(
            slide,
            bullets_box["x"],
            bullets_box["y"],
            bullets_box["w"],
            bullets_box["h"],
        )

        add_bullets_box(
            slide,
            x=bullets_box["x"] + box_inner_pad_x,
            y=bullets_box["y"] + box_inner_pad_y,
            w=bullets_box["w"] - 2 * box_inner_pad_x,
            h=bullets_box["h"] - 2 * box_inner_pad_y,
            bullets=right_bullets,
            color=NAVY,
            top_font_size=bullet_font_size,
            sub_font_size=bullet_sub_font_size,
        )

    takeaway = spec.get("takeaway", "").strip()
    takeaway_box = layout.get("takeaway_box")
    if takeaway and takeaway_box:
        add_rounded_box(
            slide,
            takeaway_box["x"],
            takeaway_box["y"],
            takeaway_box["w"],
            takeaway_box["h"],
        )

        add_textbox(
            slide,
            x=takeaway_box["x"] + 0.16,
            y=takeaway_box["y"] + 0.06,
            w=takeaway_box["w"] - 0.32,
            h=takeaway_box["h"] - 0.08,
            text=takeaway,
            font_name=BODY_FONT,
            font_size=takeaway_font_size,
            color=SLATE,
            bold=False,
            align=PP_ALIGN.CENTER,
        )

    add_footer(slide, dark=False)
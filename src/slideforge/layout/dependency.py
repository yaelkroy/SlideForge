from __future__ import annotations

from dataclasses import dataclass

from slideforge.layout.base import Box, Unit


@dataclass
class DependencyMapLayoutResult:
    content_box: Box
    main_box: Box
    diagram_box: Box
    right_column_box: Box | None
    explanation_box: Box | None
    right_panel_box: Box | None
    center_box: Box
    input_boxes: list[Box]
    formula_box: Box | None
    takeaway_box: Box | None
    content_bottom_y: Unit


def layout_dependency_map(
    content_box: Box,
    *,
    has_explanation: bool = True,
    has_right_panel: bool = False,
    has_formulas: bool = False,
    has_takeaway: bool = False,
    top_pad: Unit = 0.06,
    bottom_pad: Unit = 0.08,
    side_gap: Unit = 0.38,
    right_column_w: Unit = 3.05,
    explanation_h: Unit = 1.18,
    right_panel_h: Unit = 1.40,
    right_column_inner_gap: Unit = 0.18,
    center_w: Unit = 2.10,
    center_h: Unit = 1.06,
    node_w: Unit = 2.20,
    node_h: Unit = 0.95,
    node_side_pad: Unit = 0.22,
    node_top_pad: Unit = 0.18,
    node_bottom_pad: Unit = 0.18,
    formula_h: Unit = 0.22,
    formula_gap_top: Unit = 0.18,
    takeaway_h: Unit = 0.40,
    takeaway_gap_top: Unit = 0.12,
    footer_clearance: Unit = 0.44,
    formula_side_pad: Unit = 0.12,
    takeaway_side_pad: Unit = 0.35,
) -> DependencyMapLayoutResult:
    """
    Compute a safer dependency-map layout with:
    - a dedicated diagram region
    - an optional right-side explanation column
    - bottom formula/takeaway bands placed below the lowest occupied region

    This is designed to prevent:
    - the explanation box from intruding into the diagram
    - the bottom formula ribbon from colliding with the takeaway
    - the takeaway from drifting into the footer zone
    """
    usable = content_box.inset(0.0, 0.0)

    bottom_reserved = bottom_pad + footer_clearance
    if has_formulas:
        bottom_reserved += formula_gap_top + formula_h
    if has_takeaway:
        bottom_reserved += takeaway_gap_top + takeaway_h

    main_h = max(1.80, usable.h - top_pad - bottom_reserved)
    main_box = Box(
        usable.x,
        usable.y + top_pad,
        usable.w,
        main_h,
    )

    right_column_box: Box | None = None
    explanation_box: Box | None = None
    right_panel_box: Box | None = None

    if has_explanation or has_right_panel:
        right_column_box = Box(
            max(usable.x, main_box.right - right_column_w),
            main_box.y,
            min(right_column_w, usable.w),
            main_box.h,
        )
        diagram_box = Box(
            usable.x,
            main_box.y,
            max(0.0, right_column_box.x - usable.x - side_gap),
            main_box.h,
        )

        if has_explanation:
            explanation_box = Box(
                right_column_box.x,
                right_column_box.y,
                right_column_box.w,
                min(explanation_h, right_column_box.h),
            )

        if has_right_panel:
            panel_y = (
                (explanation_box.bottom + right_column_inner_gap)
                if explanation_box is not None
                else right_column_box.y
            )
            available_panel_h = max(0.0, right_column_box.bottom - panel_y)
            right_panel_box = Box(
                right_column_box.x,
                panel_y,
                right_column_box.w,
                min(right_panel_h, available_panel_h),
            )
    else:
        diagram_box = main_box

    # Keep node widths realistic inside the diagram region.
    local_node_w = min(node_w, max(1.50, diagram_box.w * 0.28))
    local_center_w = min(center_w, max(1.65, diagram_box.w * 0.26))

    left_x = diagram_box.x + node_side_pad
    right_x = max(
        diagram_box.x + node_side_pad,
        diagram_box.right - node_side_pad - local_node_w,
    )
    center_x = diagram_box.center_x - local_center_w / 2

    # Ensure center does not collide with side nodes.
    min_center_x = left_x + local_node_w + 0.28
    max_center_x = right_x - local_center_w - 0.28
    if max_center_x >= min_center_x:
        center_x = min(max(center_x, min_center_x), max_center_x)

    center_y = diagram_box.center_y - center_h / 2

    upper_y = diagram_box.y + node_top_pad
    lower_y = diagram_box.bottom - node_bottom_pad - node_h

    # Prevent upper/lower nodes from colliding with center node vertically.
    upper_y = min(upper_y, center_y - node_h - 0.24)
    lower_y = max(lower_y, center_y + center_h + 0.24)

    # If the available diagram is tight, compress evenly but keep separation.
    if lower_y < upper_y:
        mid_gap = 0.30
        total_needed = node_h * 2 + center_h + mid_gap * 2
        available = max(1.40, diagram_box.h - node_top_pad - node_bottom_pad)
        scale = min(1.0, available / total_needed)
        scaled_node_h = node_h * scale
        scaled_center_h = center_h * scale
        upper_y = diagram_box.y + node_top_pad
        center_y = upper_y + scaled_node_h + mid_gap * scale
        lower_y = center_y + scaled_center_h + mid_gap * scale
        node_h = scaled_node_h
        center_h = scaled_center_h

    center_box = Box(center_x, center_y, local_center_w, center_h)

    input_boxes = [
        Box(left_x, upper_y, local_node_w, node_h),
        Box(left_x, lower_y, local_node_w, node_h),
        Box(right_x, upper_y, local_node_w, node_h),
        Box(right_x, lower_y, local_node_w, node_h),
    ]

    occupied_bottom = diagram_box.bottom
    if explanation_box is not None:
        occupied_bottom = max(occupied_bottom, explanation_box.bottom)
    if right_panel_box is not None:
        occupied_bottom = max(occupied_bottom, right_panel_box.bottom)

    formula_box: Box | None = None
    takeaway_box: Box | None = None
    current_y = occupied_bottom

    if has_formulas:
        current_y += formula_gap_top
        formula_box = Box(
            usable.x + formula_side_pad,
            current_y,
            max(0.0, usable.w - 2 * formula_side_pad),
            formula_h,
        )
        current_y = formula_box.bottom

    if has_takeaway:
        current_y += takeaway_gap_top
        takeaway_box = Box(
            usable.x + takeaway_side_pad,
            current_y,
            max(0.0, usable.w - 2 * takeaway_side_pad),
            takeaway_h,
        )
        current_y = takeaway_box.bottom

    return DependencyMapLayoutResult(
        content_box=content_box,
        main_box=main_box,
        diagram_box=diagram_box,
        right_column_box=right_column_box,
        explanation_box=explanation_box,
        right_panel_box=right_panel_box,
        center_box=center_box,
        input_boxes=input_boxes,
        formula_box=formula_box,
        takeaway_box=takeaway_box,
        content_bottom_y=current_y,
    )
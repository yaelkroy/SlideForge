from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from slideforge.layout.autofit import Box, distribute_columns


@dataclass(frozen=True)
class ConnectorSegment:
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(frozen=True)
class PipelineLayoutResult:
    region: Box
    stage_boxes: list[Box]
    connectors: list[ConnectorSegment]
    examples_label_box: Box | None
    example_boxes: list[Box]
    bullets_box: Box | None
    takeaway_box: Box | None



def _box_from_dict(raw: Mapping[str, Any], fallback: Box) -> Box:
    return Box(
        float(raw.get("x", fallback.x)),
        float(raw.get("y", fallback.y)),
        float(raw.get("w", fallback.w)),
        float(raw.get("h", fallback.h)),
    )


def default_pipeline_region(*, header_content_top_y: float, layout: Mapping[str, Any], variant: str, has_secondary: bool, has_takeaway: bool) -> Box:
    if variant == "example_pipeline":
        x = float(layout.get("pipeline_x", 0.82))
        y = float(layout.get("pipeline_y", header_content_top_y + float(layout.get("content_to_pipeline_gap", 0.20))))
        w = float(layout.get("pipeline_w", 11.32))
        if "pipeline_h" in layout:
            h = float(layout["pipeline_h"])
        else:
            if has_takeaway:
                bottom_limit = float(layout.get("pipeline_bottom_limit", 4.70))
            elif has_secondary:
                bottom_limit = float(layout.get("pipeline_bottom_limit", 4.95))
            else:
                bottom_limit = float(layout.get("pipeline_bottom_limit", 5.30))
            h = max(1.40, bottom_limit - y)
    else:
        x = float(layout.get("pipeline_x", 0.86))
        y = float(layout.get("pipeline_y", header_content_top_y + float(layout.get("content_to_pipeline_gap", 0.18))))
        w = float(layout.get("pipeline_w", 11.28))
        if "pipeline_h" in layout:
            h = float(layout["pipeline_h"])
        else:
            if has_takeaway:
                bottom_limit = float(layout.get("pipeline_bottom_limit", 4.30))
            elif has_secondary:
                bottom_limit = float(layout.get("pipeline_bottom_limit", 4.95))
            else:
                bottom_limit = float(layout.get("pipeline_bottom_limit", 5.30))
            h = max(1.25, bottom_limit - y)
    return Box(x, y, w, h)


def _build_connectors(stage_boxes: list[Box]) -> list[ConnectorSegment]:
    segments: list[ConnectorSegment] = []
    for idx in range(max(0, len(stage_boxes) - 1)):
        left = stage_boxes[idx]
        right = stage_boxes[idx + 1]
        segments.append(ConnectorSegment(
            x1=left.right,
            y1=left.y + left.h / 2,
            x2=right.x,
            y2=right.y + right.h / 2,
        ))
    return segments


def layout_pipeline_family(*, header_content_top_y: float, layout: Mapping[str, Any], variant: str, stage_count: int, example_count: int = 0, has_bullets: bool = False, has_takeaway: bool = False) -> PipelineLayoutResult:
    has_secondary = bool(example_count) if variant == "pipeline" else bool(has_bullets)
    fallback_region = default_pipeline_region(
        header_content_top_y=header_content_top_y,
        layout=layout,
        variant=variant,
        has_secondary=has_secondary,
        has_takeaway=has_takeaway,
    )
    region_raw = layout.get("pipeline_region")
    region = _box_from_dict(region_raw, fallback_region) if isinstance(region_raw, Mapping) else fallback_region

    gap_default = 0.30 if variant == "example_pipeline" else 0.22
    gap = float(layout.get("pipeline_gap", gap_default))
    stage_boxes = distribute_columns(region, max(1, stage_count), gap=gap)
    connectors = _build_connectors(stage_boxes)

    examples_label_box = None
    example_boxes: list[Box] = []
    bullets_box = None
    takeaway_box = None

    if variant == "pipeline" and example_count:
        examples_label_box = Box(
            float(layout.get("examples_label_x", 1.10)),
            float(layout.get("examples_label_y", region.bottom + 0.22)),
            float(layout.get("examples_label_w", 10.90)),
            float(layout.get("examples_label_h", 0.20)),
        )
        ex_y = float(layout.get("examples_y", examples_label_box.bottom + 0.04))
        ex_h = float(layout.get("examples_h", 0.98))
        ex_gap = float(layout.get("examples_gap", 0.38))
        ex_x = float(layout.get("examples_x", 1.18))
        count = min(example_count, int(layout.get("max_examples", 2)))
        if "examples_w" in layout:
            ex_w = float(layout["examples_w"])
            xs = [ex_x + idx * (ex_w + ex_gap) for idx in range(count)]
        else:
            total_w = float(layout.get("examples_total_w", 10.97))
            ex_w = (total_w - ex_gap * max(0, count - 1)) / max(1, count)
            xs = [ex_x + idx * (ex_w + ex_gap) for idx in range(count)]
        example_boxes = [Box(x, ex_y, ex_w, ex_h) for x in xs]

    if variant == "example_pipeline" and has_bullets:
        bullets_box = Box(
            float(layout.get("bullets_x", 1.00)),
            float(layout.get("bullets_y", region.bottom + 0.28)),
            float(layout.get("bullets_w", 11.00)),
            float(layout.get("bullets_h", 0.24)),
        )

    if has_takeaway:
        if variant == "pipeline":
            fallback_takeaway_box = Box(
                float(layout.get("takeaway_x", 1.00)),
                float(layout.get("takeaway_y", 5.40)),
                float(layout.get("takeaway_w", 10.90)),
                float(layout.get("takeaway_h", 0.70)),
            )
            takeaway_raw = layout.get("takeaway_box")
            takeaway_box = _box_from_dict(takeaway_raw, fallback_takeaway_box) if isinstance(takeaway_raw, Mapping) else fallback_takeaway_box
        else:
            takeaway_box = Box(
                float(layout.get("takeaway_x", 1.02)),
                float(layout.get("takeaway_y", region.bottom + 0.72)),
                float(layout.get("takeaway_w", 10.96)),
                float(layout.get("takeaway_h", 0.42)),
            )

    return PipelineLayoutResult(
        region=region,
        stage_boxes=stage_boxes,
        connectors=connectors,
        examples_label_box=examples_label_box,
        example_boxes=example_boxes,
        bullets_box=bullets_box,
        takeaway_box=takeaway_box,
    )

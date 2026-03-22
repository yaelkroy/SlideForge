from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from slideforge.layout.autofit import Box, distribute_columns


@dataclass(frozen=True)
class TitleCompositeLayout:
    title_box: Box
    subtitle_box: Box
    author_box: Box
    visual_region: Box
    panel_boxes: list[Box]
    bullets_box: Box
    tiny_footer_box: Box


_DEFAULT_REGIONS = {
    "title_box": {"x": 0.78, "y": 0.90, "w": 11.75, "h": 0.96},
    "subtitle_box": {"x": 1.10, "y": 2.02, "w": 10.90, "h": 0.42},
    "author_box": {"x": 2.80, "y": 2.70, "w": 7.80, "h": 0.24},
    "visual_region": {"x": 0.82, "y": 3.02, "w": 11.55, "h": 2.48},
    "bullets_box": {"x": 2.65, "y": 5.60, "w": 8.10, "h": 0.34},
    "tiny_footer_box": {"x": 2.00, "y": 6.36, "w": 9.35, "h": 0.22},
}


def _box_from_dict(raw: Mapping[str, Any] | None, fallback: Mapping[str, float]) -> Box:
    raw = raw or {}
    return Box(
        float(raw.get("x", fallback["x"])),
        float(raw.get("y", fallback["y"])),
        float(raw.get("w", fallback["w"])),
        float(raw.get("h", fallback["h"])),
    )


def _resolve_legacy_region(layout: Mapping[str, Any], key: str, fallback_key: str) -> Box:
    fallback = _DEFAULT_REGIONS[fallback_key]
    if isinstance(layout.get(key), Mapping):
        return _box_from_dict(layout.get(key), fallback)
    return Box(
        float(layout.get(fallback_key.replace("_box", "_x"), fallback["x"])),
        float(layout.get(fallback_key.replace("_box", "_y"), fallback["y"])),
        float(layout.get(fallback_key.replace("_box", "_w"), fallback["w"])),
        float(layout.get(fallback_key.replace("_box", "_h"), fallback["h"])),
    )


# Legacy scalar keys are preserved for compatibility with current specs.
def layout_title_composite(layout: Mapping[str, Any], *, panel_count: int) -> TitleCompositeLayout:
    title_box = _resolve_legacy_region(layout, "title_box", "title_box")
    subtitle_box = _resolve_legacy_region(layout, "subtitle_box", "subtitle_box")
    author_box = _resolve_legacy_region(layout, "author_box", "author_box")
    bullets_box = _resolve_legacy_region(layout, "bullets_region", "bullets_box")
    tiny_footer_box = _resolve_legacy_region(layout, "tiny_footer_region", "tiny_footer_box")
    visual_region = _box_from_dict(layout.get("visual_region"), _DEFAULT_REGIONS["visual_region"])

    panel_gap = float(layout.get("panel_gap", 0.25))
    panel_boxes = distribute_columns(visual_region, panel_count, gap=panel_gap) if panel_count > 0 else []

    return TitleCompositeLayout(
        title_box=title_box,
        subtitle_box=subtitle_box,
        author_box=author_box,
        visual_region=visual_region,
        panel_boxes=panel_boxes,
        bullets_box=bullets_box,
        tiny_footer_box=tiny_footer_box,
    )

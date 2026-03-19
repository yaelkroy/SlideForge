from __future__ import annotations

from typing import Iterable

from slideforge.layout.base import Box, Unit


def distribute_columns(
    container: Box,
    n: int,
    *,
    gap: Unit = 0.25,
    ratios: Iterable[float] | None = None,
) -> list[Box]:
    if n <= 0:
        return []

    if ratios is None:
        ratios = [1.0] * n
    ratios_list = list(ratios)
    if len(ratios_list) != n:
        raise ValueError("ratios length must equal n")

    total_gap = gap * (n - 1)
    usable_w = max(0.0, container.w - total_gap)
    ratio_sum = sum(ratios_list)
    if ratio_sum <= 0:
        ratio_sum = float(n)
        ratios_list = [1.0] * n

    boxes: list[Box] = []
    x = container.x
    for idx, r in enumerate(ratios_list):
        w = usable_w * (r / ratio_sum)
        if idx == n - 1:
            # Force last box to close floating-point drift.
            w = container.right - x
        boxes.append(Box(x, container.y, w, container.h))
        x += w + gap
    return boxes


def distribute_rows(
    container: Box,
    n: int,
    *,
    gap: Unit = 0.20,
    ratios: Iterable[float] | None = None,
) -> list[Box]:
    if n <= 0:
        return []

    if ratios is None:
        ratios = [1.0] * n
    ratios_list = list(ratios)
    if len(ratios_list) != n:
        raise ValueError("ratios length must equal n")

    total_gap = gap * (n - 1)
    usable_h = max(0.0, container.h - total_gap)
    ratio_sum = sum(ratios_list)
    if ratio_sum <= 0:
        ratio_sum = float(n)
        ratios_list = [1.0] * n

    boxes: list[Box] = []
    y = container.y
    for idx, r in enumerate(ratios_list):
        h = usable_h * (r / ratio_sum)
        if idx == n - 1:
            h = container.bottom - y
        boxes.append(Box(container.x, y, container.w, h))
        y += h + gap
    return boxes
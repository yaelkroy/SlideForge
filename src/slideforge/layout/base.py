from __future__ import annotations

from dataclasses import dataclass


Unit = float  # SlideForge currently uses inches in builders.


@dataclass(frozen=True)
class Box:
    """Axis-aligned rectangle in slide units (typically inches)."""

    x: Unit
    y: Unit
    w: Unit
    h: Unit

    @property
    def right(self) -> Unit:
        return self.x + self.w

    @property
    def bottom(self) -> Unit:
        return self.y + self.h

    @property
    def center_x(self) -> Unit:
        return self.x + self.w / 2

    @property
    def center_y(self) -> Unit:
        return self.y + self.h / 2

    def inset(self, pad_x: Unit = 0.0, pad_y: Unit | None = None) -> "Box":
        py = pad_x if pad_y is None else pad_y
        return Box(
            x=self.x + pad_x,
            y=self.y + py,
            w=max(0.0, self.w - 2 * pad_x),
            h=max(0.0, self.h - 2 * py),
        )

    def move(self, dx: Unit = 0.0, dy: Unit = 0.0) -> "Box":
        return Box(self.x + dx, self.y + dy, self.w, self.h)

    def with_height(self, h: Unit) -> "Box":
        return Box(self.x, self.y, self.w, h)

    def with_width(self, w: Unit) -> "Box":
        return Box(self.x, self.y, w, self.h)

    def with_x(self, x: Unit) -> "Box":
        return Box(x, self.y, self.w, self.h)

    def with_y(self, y: Unit) -> "Box":
        return Box(self.x, y, self.w, self.h)


@dataclass(frozen=True)
class SlideSize:
    width: Unit = 13.333
    height: Unit = 7.5


DEFAULT_WIDE_SLIDE = SlideSize()
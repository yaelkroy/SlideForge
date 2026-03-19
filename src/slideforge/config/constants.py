from __future__ import annotations

from pptx.dml.color import RGBColor


# ============================================================
# Slide size
# ============================================================

SLIDE_W = 13.333
SLIDE_H = 7.5


# ============================================================
# Fonts used in PowerPoint text
# ============================================================

TITLE_FONT = "Calibri"
BODY_FONT = "Calibri"
FORMULA_FONT = "Cambria"


# ============================================================
# Fonts used for Matplotlib-generated mini-visual PNGs
# ============================================================
# Keep these separate from PowerPoint fonts so special glyphs
# and diagram labels are more reliable during image generation.

MPL_BODY_FONT = "DejaVu Sans"
MPL_FORMULA_FONT = "DejaVu Sans Mono"


# ============================================================
# Colors
# ============================================================

NAVY = RGBColor(23, 36, 74)
SLATE = RGBColor(68, 78, 96)
MUTED = RGBColor(95, 102, 117)
ACCENT = RGBColor(120, 142, 205)

WHITE = RGBColor(255, 255, 255)
OFFWHITE = RGBColor(247, 249, 252)

BOX_LINE = RGBColor(173, 185, 220)
LIGHT_BOX_FILL = RGBColor(255, 255, 255)
DARK_BOX_FILL = RGBColor(23, 32, 56)

TITLE_PANEL_FILL = RGBColor(34, 46, 84)
TITLE_PANEL_LINE = RGBColor(198, 208, 236)
GHOST_TEXT = RGBColor(224, 230, 244)
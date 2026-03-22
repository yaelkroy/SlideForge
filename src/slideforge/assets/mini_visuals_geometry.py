from __future__ import annotations

"""Compatibility façade for geometry mini-visuals.

The geometry visuals now live in pack modules under ``assets/packs/geometry`` so the
engine core stays presentation-agnostic. This module preserves the old public import
surface used by ``mini_visuals.py`` and existing builder specs.
"""

from slideforge.assets.packs.geometry import ALIASES_GEOMETRY_PACK, DRAWERS_GEOMETRY_PACK

DRAWERS_GEOMETRY = dict(DRAWERS_GEOMETRY_PACK)
ALIASES_GEOMETRY = dict(ALIASES_GEOMETRY_PACK)

__all__ = ["DRAWERS_GEOMETRY", "ALIASES_GEOMETRY"]

from slideforge.assets.packs.geometry.heroes import ALIASES as HERO_ALIASES, DRAWERS as HERO_DRAWERS
from slideforge.assets.packs.geometry.norms_dots_angles import ALIASES as NDA_ALIASES, DRAWERS as NDA_DRAWERS
from slideforge.assets.packs.geometry.points_vectors import ALIASES as PV_ALIASES, DRAWERS as PV_DRAWERS
from slideforge.assets.packs.geometry.projections_orthogonality import ALIASES as PO_ALIASES, DRAWERS as PO_DRAWERS

DRAWERS_GEOMETRY_PACK = {
    **HERO_DRAWERS,
    **PV_DRAWERS,
    **NDA_DRAWERS,
    **PO_DRAWERS,
}

ALIASES_GEOMETRY_PACK = {
    **HERO_ALIASES,
    **PV_ALIASES,
    **NDA_ALIASES,
    **PO_ALIASES,
}

__all__ = ["DRAWERS_GEOMETRY_PACK", "ALIASES_GEOMETRY_PACK"]

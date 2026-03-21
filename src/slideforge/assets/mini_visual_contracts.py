from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class MiniVisualContract:
    requested_kind: str
    canonical_kind: str
    geometry_only: bool = True
    builder_should_render_formulas: bool = False
    notes: str = ""
    used_legacy_formula_alias: bool = False


LEGACY_FORMULA_ALIASES: dict[str, str] = {
    "worked_norm_geometry": "norm_worked_geometry",
    "norm_worked_example": "norm_worked_geometry",
    "worked_dot_product": "dot_product_worked_geometry",
    "dot_product_worked_example": "dot_product_worked_geometry",
    "worked_angle_homework": "angle_homework_geometry",
    "angle_homework_worked": "angle_homework_geometry",
    "orthogonal_geometry_symbolic": "orthogonal_vectors_geometry",
    "orthogonal_vectors_symbolic": "orthogonal_vectors_geometry",
    "homework_projection_symbolic": "projection_homework_geometry",
    "projection_symbolic_homework": "projection_homework_geometry",
}

FORMULA_OUTSIDE_IMAGE_KINDS: set[str] = {
    "norm_worked_geometry",
    "dot_product_worked_geometry",
    "angle_recovery_geometry",
    "angle_homework_geometry",
    "orthogonal_vectors_geometry",
    "projection_homework_geometry",
}


def normalize_visual_kind(kind: str) -> str:
    raw = str(kind or "").strip()
    if not raw:
        return ""
    return LEGACY_FORMULA_ALIASES.get(raw, raw)


def is_legacy_formula_alias(kind: str) -> bool:
    raw = str(kind or "").strip()
    return raw in LEGACY_FORMULA_ALIASES and LEGACY_FORMULA_ALIASES[raw] != raw


def get_visual_contract(kind: str) -> MiniVisualContract:
    requested = str(kind or "").strip()
    canonical = normalize_visual_kind(requested)
    return MiniVisualContract(
        requested_kind=requested,
        canonical_kind=canonical,
        geometry_only=True,
        builder_should_render_formulas=canonical in FORMULA_OUTSIDE_IMAGE_KINDS,
        notes=(
            "Keep the PNG visual-only. Render formulas, steps, and final results as native PowerPoint text."
            if canonical in FORMULA_OUTSIDE_IMAGE_KINDS else
            "Short labels are acceptable, but rich symbolic derivations belong in the builder/renderer."
        ),
        used_legacy_formula_alias=is_legacy_formula_alias(requested),
    )


def visual_requires_builder_text(kind: str) -> bool:
    return get_visual_contract(kind).builder_should_render_formulas


def normalize_visual_kinds(kinds: Iterable[str]) -> list[str]:
    return [normalize_visual_kind(kind) for kind in kinds if str(kind or "").strip()]


__all__ = [
    "MiniVisualContract",
    "LEGACY_FORMULA_ALIASES",
    "FORMULA_OUTSIDE_IMAGE_KINDS",
    "get_visual_contract",
    "is_legacy_formula_alias",
    "normalize_visual_kind",
    "normalize_visual_kinds",
    "visual_requires_builder_text",
]

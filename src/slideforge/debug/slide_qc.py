from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, Iterable, Mapping, Sequence

try:
    from slideforge.assets.mini_visual_contracts import get_visual_contract
except Exception:  # pragma: no cover - optional dependency while bootstrapping
    get_visual_contract = None



@dataclass(frozen=True)
class SlideQCIssue:
    code: str
    severity: str
    message: str
    slide_title: str = ""
    block_key: str = ""
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SlideQCThresholds:
    min_font_size: int = 12
    min_formula_box_height: float = 0.34
    min_result_box_height: float = 0.28
    duplicate_min_chars: int = 10


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_text(value: str) -> str:
    text = _clean_text(value)
    text = text.replace("−", "-")
    text = text.replace("·", "*")
    text = text.replace("⋅", "*")
    text = text.replace("⟂", "perp")
    text = text.replace("∥", "||")
    text = text.replace("→", "->")
    text = text.replace("ᵀ", "^t")
    text = re.sub(r"\s+", " ", text)
    return text.casefold()


def _get_attr_or_key(obj: Any, key: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, Mapping):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _extract_strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [_clean_text(value)] if _clean_text(value) else []
    if isinstance(value, Mapping):
        values: list[str] = []
        for item in value.values():
            values.extend(_extract_strings(item))
        return values
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        values: list[str] = []
        for item in value:
            values.extend(_extract_strings(item))
        return values
    return []


def check_text_fit_thresholds(
    text_fits: Mapping[str, Any] | None,
    *,
    slide_title: str = "",
    thresholds: SlideQCThresholds | None = None,
) -> list[SlideQCIssue]:
    thresholds = thresholds or SlideQCThresholds()
    issues: list[SlideQCIssue] = []

    for key, fit in (text_fits or {}).items():
        font_size = _get_attr_or_key(fit, "font_size")
        if font_size is None:
            continue
        if int(font_size) < thresholds.min_font_size:
            issues.append(
                SlideQCIssue(
                    code="font_below_threshold",
                    severity="warning",
                    message=(
                        f"Text fit for '{key}' fell below the minimum readable font size "
                        f"({font_size} < {thresholds.min_font_size})."
                    ),
                    slide_title=slide_title,
                    block_key=str(key),
                    context={"font_size": int(font_size)},
                )
            )
    return issues


def check_formula_box_thresholds(
    text_boxes: Mapping[str, Any] | None,
    *,
    slide_title: str = "",
    thresholds: SlideQCThresholds | None = None,
    formula_keys: Sequence[str] = ("formulas", "result", "result_box"),
) -> list[SlideQCIssue]:
    thresholds = thresholds or SlideQCThresholds()
    issues: list[SlideQCIssue] = []

    for key in formula_keys:
        box = (text_boxes or {}).get(key)
        if box is None:
            continue
        height = _get_attr_or_key(box, "h")
        if height is None:
            continue
        min_h = (
            thresholds.min_result_box_height
            if "result" in str(key)
            else thresholds.min_formula_box_height
        )
        if float(height) < min_h:
            issues.append(
                SlideQCIssue(
                    code="formula_box_too_short",
                    severity="warning",
                    message=(
                        f"Box '{key}' is too short for comfortable formula reading "
                        f"({height:.2f}in < {min_h:.2f}in)."
                    ),
                    slide_title=slide_title,
                    block_key=str(key),
                    context={"height": float(height), "min_height": float(min_h)},
                )
            )
    return issues


def check_duplicate_formula_payload(
    spec: Mapping[str, Any] | None,
    *,
    slide_title: str = "",
    thresholds: SlideQCThresholds | None = None,
    image_keys: Sequence[str] = (
        "image_formula_text",
        "mini_visual_formula",
        "mini_visual_formulas",
        "raster_formula_text",
        "embedded_formula_text",
        "visual_annotations",
        "image_labels",
        "raster_labels",
    ),
    text_keys: Sequence[str] = (
        "formulas",
        "formula_lines",
        "result",
        "steps",
        "takeaway",
        "visible_anchor_text",
    ),
) -> list[SlideQCIssue]:
    thresholds = thresholds or SlideQCThresholds()
    spec = spec or {}
    issues: list[SlideQCIssue] = []

    image_strings: list[str] = []
    for key in image_keys:
        image_strings.extend(_extract_strings(spec.get(key)))

    text_strings: list[str] = []
    for key in text_keys:
        text_strings.extend(_extract_strings(spec.get(key)))

    normalized_image = [
        _normalize_text(text)
        for text in image_strings
        if len(_normalize_text(text)) >= thresholds.duplicate_min_chars
    ]
    normalized_text = [
        _normalize_text(text)
        for text in text_strings
        if len(_normalize_text(text)) >= thresholds.duplicate_min_chars
    ]

    seen_pairs: set[tuple[str, str]] = set()
    for src in normalized_image:
        for dst in normalized_text:
            if not src or not dst:
                continue
            if src == dst or src in dst or dst in src:
                pair = tuple(sorted((src, dst)))
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                issues.append(
                    SlideQCIssue(
                        code="duplicate_formula_payload",
                        severity="warning",
                        message=(
                            "Formula-like text appears in both the raster/image payload and "
                            "native slide text. Keep the PNG geometry-only and render formulas "
                            "as PowerPoint text."
                        ),
                        slide_title=slide_title,
                        context={
                            "image_text": src[:120],
                            "slide_text": dst[:120],
                        },
                    )
                )
    return issues


def check_raster_symbol_health(
    raster_labels: Sequence[str] | None,
    *,
    slide_title: str = "",
) -> list[SlideQCIssue]:
    issues: list[SlideQCIssue] = []
    danger_chars = {"�", "□", "▯", "◻", "?"}
    latex_like = re.compile(r"\\[A-Za-z]+")
    ascii_math_markup = re.compile(r"(^|[^A-Za-z])(\^|_[A-Za-z0-9]|\*\*)([^A-Za-z]|$)")

    for raw_label in raster_labels or []:
        label = _clean_text(raw_label)
        if not label:
            continue

        if any(ch in label for ch in {"�", "□", "▯", "◻"}):
            issues.append(
                SlideQCIssue(
                    code="raster_glyph_substitution",
                    severity="error",
                    message=(
                        "Raster label contains replacement or missing-glyph characters. "
                        "Use safer glyphs or move the formula into native PowerPoint text."
                    ),
                    slide_title=slide_title,
                    context={"label": label},
                )
            )
            continue

        if latex_like.search(label):
            issues.append(
                SlideQCIssue(
                    code="latex_in_raster_label",
                    severity="warning",
                    message=(
                        "Raster label still contains LaTeX-like markup. Dense symbolic content "
                        "should not be baked into the PNG."
                    ),
                    slide_title=slide_title,
                    context={"label": label},
                )
            )

        if ascii_math_markup.search(label):
            issues.append(
                SlideQCIssue(
                    code="ascii_math_markup_in_raster",
                    severity="warning",
                    message=(
                        "Raster label contains caret/subscript-style math markup, which often "
                        "renders poorly in exported PDFs. Prefer native PowerPoint text."
                    ),
                    slide_title=slide_title,
                    context={"label": label},
                )
            )
    return issues




def check_visual_contracts(
    spec: Mapping[str, Any] | None,
    *,
    slide_title: str = "",
) -> list[SlideQCIssue]:
    issues: list[SlideQCIssue] = []
    if not spec or get_visual_contract is None:
        return issues

    candidate_keys = (
        "mini_visual",
        "visual_kind",
        "hero_visual",
        "diagram_kind",
        "panel_visual_kind",
    )
    visual_kinds: list[str] = []
    for key in candidate_keys:
        value = spec.get(key)
        if isinstance(value, str) and _clean_text(value):
            visual_kinds.append(_clean_text(value))

    panel_visuals = spec.get("panel_visuals")
    if isinstance(panel_visuals, Sequence) and not isinstance(panel_visuals, (str, bytes, bytearray)):
        for item in panel_visuals:
            if isinstance(item, Mapping):
                kind = _clean_text(item.get("kind") or item.get("mini_visual"))
                if kind:
                    visual_kinds.append(kind)
            else:
                kind = _clean_text(item)
                if kind:
                    visual_kinds.append(kind)

    text_fields = _extract_strings({
        "formulas": spec.get("formulas"),
        "formula_lines": spec.get("formula_lines"),
        "steps": spec.get("steps"),
        "result": spec.get("result"),
        "takeaway": spec.get("takeaway"),
        "explanation": spec.get("explanation"),
    })
    has_builder_text = any(_clean_text(t) for t in text_fields)

    for kind in visual_kinds:
        contract = get_visual_contract(kind)
        if contract.used_legacy_formula_alias:
            issues.append(
                SlideQCIssue(
                    code="legacy_formula_visual_alias",
                    severity="warning",
                    message=(
                        f"Mini visual '{kind}' uses a legacy formula-bearing alias. "
                        f"Prefer the geometry-only canonical kind '{contract.canonical_kind}'."
                    ),
                    slide_title=slide_title,
                    context={"requested_kind": kind, "canonical_kind": contract.canonical_kind},
                )
            )
        if contract.builder_should_render_formulas and not has_builder_text:
            issues.append(
                SlideQCIssue(
                    code="geometry_visual_missing_builder_text",
                    severity="warning",
                    message=(
                        f"Mini visual '{contract.canonical_kind}' is geometry-only and expects formulas/steps "
                        "to be rendered in native slide text, but no matching text blocks were detected."
                    ),
                    slide_title=slide_title,
                    context={"requested_kind": kind, "canonical_kind": contract.canonical_kind},
                )
            )
    return issues


def run_slide_qc(
    *,
    spec: Mapping[str, Any] | None = None,
    text_fits: Mapping[str, Any] | None = None,
    text_boxes: Mapping[str, Any] | None = None,
    raster_labels: Sequence[str] | None = None,
    slide_title: str = "",
    thresholds: SlideQCThresholds | None = None,
) -> list[SlideQCIssue]:
    """Run a lightweight QC pass over builder/layout/debug metadata."""
    thresholds = thresholds or SlideQCThresholds()
    issues: list[SlideQCIssue] = []
    issues.extend(check_text_fit_thresholds(text_fits, slide_title=slide_title, thresholds=thresholds))
    issues.extend(check_formula_box_thresholds(text_boxes, slide_title=slide_title, thresholds=thresholds))
    issues.extend(check_duplicate_formula_payload(spec, slide_title=slide_title, thresholds=thresholds))
    issues.extend(check_raster_symbol_health(raster_labels, slide_title=slide_title))
    issues.extend(check_visual_contracts(spec, slide_title=slide_title))
    return issues


def summarize_qc_issues(issues: Sequence[SlideQCIssue]) -> str:
    if not issues:
        return "No QC issues found."
    counts: dict[str, int] = {}
    for issue in issues:
        counts[issue.code] = counts.get(issue.code, 0) + 1
    parts = [f"{code}: {count}" for code, count in sorted(counts.items())]
    return "; ".join(parts)


__all__ = [
    "SlideQCIssue",
    "SlideQCThresholds",
    "check_text_fit_thresholds",
    "check_formula_box_thresholds",
    "check_duplicate_formula_payload",
    "check_raster_symbol_health",
    "check_visual_contracts",
    "run_slide_qc",
    "summarize_qc_issues",
]

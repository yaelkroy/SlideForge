from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, Iterable, Mapping, Sequence

try:
    from slideforge.assets.mini_visual_contracts import get_visual_contract
except Exception:  # pragma: no cover - optional dependency while bootstrapping
    get_visual_contract = None

try:
    from slideforge.assets.mini_visuals import resolve_visual_kind
except Exception:  # pragma: no cover - optional dependency while bootstrapping
    resolve_visual_kind = None

try:
    from slideforge.assets.packs.geometry.heroes import get_visual_metadata as _hero_visual_metadata
except Exception:  # pragma: no cover - optional dependency while bootstrapping
    _hero_visual_metadata = None

try:
    from slideforge.assets.packs.geometry.norms_dots_angles import get_visual_metadata as _nda_visual_metadata
except Exception:  # pragma: no cover - optional dependency while bootstrapping
    _nda_visual_metadata = None

try:
    from slideforge.layout.analytic_panel import layout_analytic_panel
    from slideforge.layout.autofit import Box as _QCBox
except Exception:  # pragma: no cover - optional dependency while bootstrapping
    layout_analytic_panel = None
    _QCBox = None


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
    max_visual_aspect_ratio_over_preferred: float = 1.18
    min_visual_preferred_height_ratio: float = 0.95
    max_visual_aspect_ratio_over_preferred: float = 1.18


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



def _lookup_visual_metadata(kind: str) -> dict[str, Any]:
    raw = str(kind or "").strip()
    if not raw:
        return {}
    canonical = resolve_visual_kind(raw) if resolve_visual_kind is not None else raw
    for getter in (_hero_visual_metadata, _nda_visual_metadata):
        if getter is None:
            continue
        try:
            metadata = getter(canonical)
        except Exception:
            metadata = {}
        if metadata:
            return dict(metadata)
    return {}


def _box_from_raw(raw: Mapping[str, Any] | None, fallback: Mapping[str, Any]) -> dict[str, float]:
    raw = raw or {}
    return {
        "x": float(raw.get("x", fallback["x"])),
        "y": float(raw.get("y", fallback["y"])),
        "w": float(raw.get("w", fallback["w"])),
        "h": float(raw.get("h", fallback["h"])),
    }


def check_section_visual_box_contracts(
    spec: Mapping[str, Any] | None,
    *,
    slide_title: str = "",
    thresholds: SlideQCThresholds | None = None,
) -> list[SlideQCIssue]:
    thresholds = thresholds or SlideQCThresholds()
    spec = spec or {}
    issues: list[SlideQCIssue] = []

    if _clean_text(spec.get("kind")) != "section_divider":
        return issues

    layout = dict(spec.get("layout", {}) or {})
    section_visual = dict(spec.get("section_visual", {}) or {})
    elements = list(section_visual.get("elements", []) or [])
    if not elements:
        return issues

    band_box = _box_from_raw(
        layout.get("band_region"),
        {"x": 0.90, "y": 3.52, "w": 11.55, "h": 1.52},
    )

    count = len(elements)
    side_pad = float(layout.get("band_side_pad", 0.35))
    inter_gap = float(layout.get("band_gap", 0.30))
    usable_w = band_box["w"] - 2 * side_pad - inter_gap * max(0, count - 1)
    default_elem_w = usable_w / count if count else usable_w
    default_elem_h = float(layout.get("element_h", min(1.24, band_box["h"] - 0.22)))
    label_h = float(layout.get("label_h", 0.22))
    label_gap = float(layout.get("label_gap", 0.06))

    for idx, elem in enumerate(elements):
        kind = _clean_text(elem.get("kind"))
        metadata = _lookup_visual_metadata(kind)
        if not metadata:
            continue

        label = _clean_text(elem.get("label"))
        has_explicit_box = all(key in elem for key in ("x", "y", "w", "h"))

        if has_explicit_box:
            box_w = float(elem["w"])
            box_h = float(elem["h"])
            source = "explicit_box"
        elif count == 1 and not label and bool(layout.get("expand_single_hero", True)):
            hero_pad_x = float(layout.get("hero_pad_x", 0.14))
            hero_pad_y = float(layout.get("hero_pad_y", 0.10))
            box_w = max(0.10, band_box["w"] - 2 * hero_pad_x)
            box_h = max(0.10, band_box["h"] - 2 * hero_pad_y)
            source = "hero_band"
        else:
            box_w = default_elem_w
            box_h = max(0.60, default_elem_h - label_h - label_gap) if label else default_elem_h
            source = "auto_row"

        min_width = float(metadata.get("min_width_in", 0.0) or 0.0)
        min_height = float(metadata.get("min_height_in", 0.0) or 0.0)
        preferred_height = float(metadata.get("preferred_height_in", 0.0) or 0.0)
        preferred_aspect_ratio = float(metadata.get("preferred_aspect_ratio", 0.0) or 0.0)
        actual_aspect_ratio = box_w / max(box_h, 0.01)

        if min_height > 0 and box_h + 1e-6 < min_height:
            issues.append(
                SlideQCIssue(
                    code="visual_box_below_contract",
                    severity="warning",
                    message=(
                        f"Section divider visual '{kind}' is too short for its contract "
                        f"({box_h:.2f}in < {min_height:.2f}in, source={source})."
                    ),
                    slide_title=slide_title,
                    block_key=f"section_visual.elements[{idx}]",
                    context={
                        "kind": kind,
                        "source": source,
                        "height": box_h,
                        "min_height": min_height,
                    },
                )
            )

        if min_width > 0 and box_w + 1e-6 < min_width:
            issues.append(
                SlideQCIssue(
                    code="visual_box_below_contract",
                    severity="warning",
                    message=(
                        f"Section divider visual '{kind}' is too narrow for its contract "
                        f"({box_w:.2f}in < {min_width:.2f}in, source={source})."
                    ),
                    slide_title=slide_title,
                    block_key=f"section_visual.elements[{idx}]",
                    context={
                        "kind": kind,
                        "source": source,
                        "width": box_w,
                        "min_width": min_width,
                    },
                )
            )


        if (
            preferred_height > 0
            and box_h + 1e-6 < preferred_height * thresholds.min_visual_preferred_height_ratio
        ):
            issues.append(
                SlideQCIssue(
                    code="visual_box_below_preferred_height",
                    severity="warning",
                    message=(
                        f"Section divider visual '{kind}' is below its preferred readable height "
                        f"({box_h:.2f}in < {preferred_height:.2f}in, source={source})."
                    ),
                    slide_title=slide_title,
                    block_key=f"section_visual.elements[{idx}]",
                    context={
                        "kind": kind,
                        "source": source,
                        "height": box_h,
                        "preferred_height": preferred_height,
                    },
                )
            )

        if (
            preferred_aspect_ratio > 0
            and actual_aspect_ratio > preferred_aspect_ratio * thresholds.max_visual_aspect_ratio_over_preferred
        ):
            issues.append(
                SlideQCIssue(
                    code="visual_aspect_too_wide",
                    severity="warning",
                    message=(
                        f"Section divider visual '{kind}' is allocated a box with aspect ratio "
                        f"{actual_aspect_ratio:.2f}, which is too wide for its preferred ratio "
                        f"{preferred_aspect_ratio:.2f} (source={source})."
                    ),
                    slide_title=slide_title,
                    block_key=f"section_visual.elements[{idx}]",
                    context={
                        "kind": kind,
                        "source": source,
                        "aspect_ratio": actual_aspect_ratio,
                        "preferred_aspect_ratio": preferred_aspect_ratio,
                    },
                )
            )

    return issues


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




def _qc_clean_steps_text(spec: Mapping[str, Any]) -> str:
    blocks: list[str] = []
    for idx, step in enumerate(spec.get("steps") or [], start=1):
        if isinstance(step, Mapping):
            parts = [
                _clean_text(step.get("title") or step.get("label") or f"Step {idx}"),
                _clean_text(step.get("body") or step.get("text") or step.get("explanation")),
                _clean_text(step.get("formula") or step.get("equation") or step.get("result")),
                _clean_text(step.get("note")),
            ]
        else:
            parts = [f"Step {idx}", _clean_text(step)]
        block = "\n".join(part for part in parts if part)
        if block:
            blocks.append(block)
    return "\n\n".join(blocks)


def check_analytic_panel_balance(
    spec: Mapping[str, Any] | None,
    *,
    slide_title: str = "",
) -> list[SlideQCIssue]:
    if not spec or layout_analytic_panel is None or _QCBox is None:
        return []

    kind = _clean_text(spec.get("kind"))
    if kind not in {"analytic_panel", "worked_example", "worked_example_panel"}:
        return []

    layout = dict(spec.get("layout", {}) or {})
    content_box = dict(layout.get("content_box", {}) or {})
    outer = _QCBox(
        float(content_box.get("x", 0.86)),
        float(content_box.get("y", 1.34)),
        float(content_box.get("w", 11.30)),
        float(content_box.get("h", 5.18)),
    )

    explanation = _clean_text(spec.get("text_explanation") or spec.get("explanation"))
    result = spec.get("result")
    if isinstance(result, Mapping):
        result_text = "\n".join([part for part in [
            _clean_text(result.get("body") or result.get("text") or result.get("explanation")),
            _clean_text(result.get("formula") or result.get("equation")),
            _clean_text(result.get("note")),
        ] if part])
    else:
        result_text = _clean_text(result)
    steps_text = _qc_clean_steps_text(spec)
    takeaway = _clean_text(spec.get("takeaway"))

    result_layout = layout_analytic_panel(
        outer,
        explanation_text=explanation,
        steps_text=steps_text,
        result_text=result_text,
        takeaway_text=takeaway,
        layout_mode=_clean_text(layout.get("worked_layout_mode") or layout.get("layout_mode") or "two_column") or "two_column",
        visual_kind=_clean_text(spec.get("mini_visual")),
        top_pad=float(layout.get("top_pad", 0.16)),
        bottom_pad=float(layout.get("bottom_pad", 0.14)),
        side_pad=float(layout.get("side_pad", 0.20)),
        gap=float(layout.get("gap", 0.10)),
        col_gap=float(layout.get("col_gap", layout.get("column_gap", 0.20))),
        min_steps_h=float(layout.get("min_steps_h", 2.0)),
        explanation_min_h=float(layout.get("explanation_min_h", 0.34)),
        explanation_max_h=float(layout.get("explanation_max_h", 0.62)),
        result_min_h=float(layout.get("result_min_h", 0.72)),
        result_max_h=float(layout.get("result_max_h", 1.08)),
        takeaway_min_h=float(layout.get("takeaway_min_h", 0.50)),
        takeaway_max_h=float(layout.get("takeaway_max_h", 0.84)),
    )

    issues: list[SlideQCIssue] = []
    metadata = _lookup_visual_metadata(_clean_text(spec.get("mini_visual")))
    preferred_aspect = float(metadata.get("preferred_aspect_ratio", 0.0) or 0.0)
    derivation_like = (not explanation) and bool(result_text.strip()) and (not takeaway)
    if derivation_like and 0.0 < preferred_aspect <= 1.15 and result_layout.diagram_share < 0.31:
        issues.append(
            SlideQCIssue(
                code="analytic_panel_diagram_share_too_small",
                severity="warning",
                message=(
                    f"Analytic-panel visual '{_clean_text(spec.get('mini_visual'))}' is likely too narrow "
                    f"for a derivation layout (diagram share {result_layout.diagram_share:.2f})."
                ),
                slide_title=slide_title,
                context={"diagram_share": result_layout.diagram_share, "candidate": result_layout.candidate_name},
            )
        )
    if any(note in {"diagram_share_too_small_for_square_derivation_visual", "hard_diagram_aspect_far_from_preference"} for note in result_layout.notes):
        issues.append(
            SlideQCIssue(
                code="analytic_panel_layout_balance_risk",
                severity="warning",
                message=(
                    "Analytic-panel layout has a diagram/text balance risk; consider giving the visual more width "
                    "or relaxing the text column density."
                ),
                slide_title=slide_title,
                context={"candidate": result_layout.candidate_name, "notes": list(result_layout.notes)},
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
    issues.extend(check_section_visual_box_contracts(spec, slide_title=slide_title, thresholds=thresholds))
    issues.extend(check_analytic_panel_balance(spec, slide_title=slide_title))
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
    "check_section_visual_box_contracts",
    "check_analytic_panel_balance",
    "run_slide_qc",
    "summarize_qc_issues",
]

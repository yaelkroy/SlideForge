from __future__ import annotations

import argparse
import importlib
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from slideforge.app.presentation_factory import create_presentation
from slideforge.builders.builder_registry import BUILDERS
from slideforge.config.paths import OUTPUT_FILE, ensure_runtime_dirs
from slideforge.debug.slide_qc import run_slide_qc
from slideforge.io.backgrounds import validate_backgrounds


PROJECT_TARGETS: dict[str, str] = {
    "ml_foundations": "slideforge.projects.ml_foundations:ML_FOUNDATIONS_SLIDES",
    "ml_foundations_part1": "slideforge.projects.ml_foundations:ML_FOUNDATIONS_PART1_SLIDES",
    "ml_foundations_part2": "slideforge.projects.ml_foundations:ML_FOUNDATIONS_PART2_SLIDES",
}


SlidesLike = Sequence[dict[str, Any]] | str


def _copy_slide_specs(slides: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    return [deepcopy(spec) for spec in slides]


def _parse_target(target: str) -> tuple[str, str]:
    cleaned = str(target or "").strip()
    if not cleaned:
        raise ValueError("Slide target cannot be empty.")
    resolved = PROJECT_TARGETS.get(cleaned, cleaned)
    if ":" not in resolved:
        raise ValueError(
            "Slide target must be a known project alias or use 'module.path:ATTRIBUTE' format. "
            f"Got: {target!r}"
        )
    module_name, attr_name = resolved.split(":", 1)
    return module_name.strip(), attr_name.strip()


def load_slides(target: SlidesLike) -> list[dict[str, Any]]:
    if isinstance(target, str):
        module_name, attr_name = _parse_target(target)
        module = importlib.import_module(module_name)
        if not hasattr(module, attr_name):
            raise AttributeError(
                f"Module {module_name!r} does not define slide attribute {attr_name!r}."
            )
        slides = getattr(module, attr_name)
    else:
        slides = target

    if not isinstance(slides, Sequence):
        raise TypeError("Slides must be a sequence of slide spec dictionaries.")

    copied = _copy_slide_specs(list(slides))
    for index, spec in enumerate(copied, start=1):
        if not isinstance(spec, dict):
            raise TypeError(f"Slide {index} is not a dict spec: {type(spec)!r}")
        if "kind" not in spec:
            raise KeyError(f"Slide {index} is missing required key 'kind'.")
    return copied


def _merge_dict(base: dict[str, Any], updates: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in updates.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = _merge_dict(dict(merged[key]), value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _apply_theme_override_to_spec(
    spec: dict[str, Any],
    *,
    slide_index: int,
    theme_overrides: Mapping[str, Any],
) -> dict[str, Any]:
    updated = dict(spec)

    default_theme = theme_overrides.get("theme")
    if default_theme is not None:
        updated["theme"] = str(default_theme)

    spec_theme_overrides = theme_overrides.get("theme_overrides")
    if isinstance(spec_theme_overrides, Mapping):
        existing = dict(updated.get("theme_overrides", {}) or {})
        updated["theme_overrides"] = _merge_dict(existing, spec_theme_overrides)

    by_kind = theme_overrides.get("by_kind")
    if isinstance(by_kind, Mapping):
        kind_update = by_kind.get(updated.get("kind"))
        if isinstance(kind_update, Mapping):
            updated = _merge_dict(updated, kind_update)

    by_index = theme_overrides.get("by_index")
    if isinstance(by_index, Mapping):
        index_update = by_index.get(slide_index)
        if isinstance(index_update, Mapping):
            updated = _merge_dict(updated, index_update)

    return updated


def apply_theme_overrides(
    slides: Sequence[dict[str, Any]],
    theme_overrides: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not theme_overrides:
        return _copy_slide_specs(slides)
    return [
        _apply_theme_override_to_spec(spec, slide_index=index, theme_overrides=theme_overrides)
        for index, spec in enumerate(_copy_slide_specs(slides), start=1)
    ]




def _emit_slide_qc_issues(
    slide_index: int,
    spec: Mapping[str, Any],
) -> None:
    slide_title = str(spec.get("title") or spec.get("slide_title") or f"Slide {slide_index}").strip()
    issues = run_slide_qc(spec=spec, slide_title=slide_title)
    for issue in issues:
        print(
            f"[slideqc][{issue.severity}] slide {slide_index} '{slide_title}': {issue.message}"
        )


def build_deck(
    slides: Sequence[dict[str, Any]],
    output_file: str | Path = OUTPUT_FILE,
    theme_overrides: Mapping[str, Any] | None = None,
    *,
    validate_assets: bool = True,
) -> Path:
    ensure_runtime_dirs()

    resolved_slides = apply_theme_overrides(slides, theme_overrides)
    if validate_assets:
        validate_backgrounds(resolved_slides)

    prs = create_presentation()
    counters: dict[str, int] = defaultdict(int)

    for idx, spec in enumerate(resolved_slides, start=1):
        kind = str(spec.get("kind", "")).strip()
        if kind not in BUILDERS:
            raise ValueError(f"Unknown slide kind on slide {idx}: {kind!r}")
        _emit_slide_qc_issues(idx, spec)
        BUILDERS[kind](prs, spec, counters)

    output_path = Path(output_file).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(output_path)
    return output_path


def _available_projects_text() -> str:
    return ", ".join(sorted(PROJECT_TARGETS))


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a SlideForge presentation from any registered project or module-based slide spec source."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--project",
        default="ml_foundations",
        help=f"Registered project alias. Available: {_available_projects_text()}",
    )
    group.add_argument(
        "--slides-target",
        help="Explicit slide target in 'module.path:ATTRIBUTE' format.",
    )
    parser.add_argument(
        "--output",
        default=str(OUTPUT_FILE),
        help="Output .pptx path.",
    )
    parser.add_argument(
        "--theme",
        help="Optional default slide theme override applied to every slide spec.",
    )
    parser.add_argument(
        "--skip-background-validation",
        action="store_true",
        help="Skip background asset validation before build.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> Path:
    args = parse_args(argv)
    target = args.slides_target or args.project
    slides = load_slides(target)

    theme_overrides: dict[str, Any] | None = None
    if args.theme:
        theme_overrides = {"theme": args.theme}

    output_path = build_deck(
        slides,
        output_file=args.output,
        theme_overrides=theme_overrides,
        validate_assets=not args.skip_background_validation,
    )
    print(f"Saved presentation: {output_path}")
    return output_path


__all__ = [
    "PROJECT_TARGETS",
    "apply_theme_overrides",
    "build_deck",
    "create_presentation",
    "load_slides",
    "main",
    "parse_args",
]

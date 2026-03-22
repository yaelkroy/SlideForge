from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class PipelineStage:
    title: str
    caption: str
    formula: str
    mini_visual: str
    visual_box: Mapping[str, Any] | None
    style: Mapping[str, Any]
    raw: Mapping[str, Any]


@dataclass(frozen=True)
class PipelineExample:
    mini_visual: str
    text: str
    visual_variant: str | None
    caption_font_size: int | None


@dataclass(frozen=True)
class PipelineFamilySpec:
    variant: str
    stages: list[PipelineStage]
    bullets: list[str]
    examples: list[PipelineExample]
    takeaway: str
    examples_label_text: str


_DEF_EXAMPLES_LABEL = "Running examples"


def _text(value: Any) -> str:
    return str(value or "").strip()


def _list_of_str(values: Any) -> list[str]:
    return [_text(v) for v in (values or []) if _text(v)]


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _normalize_stage_common(raw: Mapping[str, Any], *, caption_keys: tuple[str, ...], formula_keys: tuple[str, ...]) -> PipelineStage:
    caption = next((_text(raw.get(k)) for k in caption_keys if _text(raw.get(k))), "")
    formula = next((_text(raw.get(k)) for k in formula_keys if _text(raw.get(k))), "")
    visual_box = raw.get("visual_box") if isinstance(raw.get("visual_box"), Mapping) else None
    return PipelineStage(
        title=_text(raw.get("title")),
        caption=caption,
        formula=formula,
        mini_visual=_text(raw.get("mini_visual")),
        visual_box=visual_box,
        style=_mapping(raw.get("style")),
        raw=dict(raw),
    )


def _normalize_pipeline_steps(spec: Mapping[str, Any]) -> list[PipelineStage]:
    raw_steps = _mapping(spec.get("pipeline")).get("steps", []) or []
    return [
        _normalize_stage_common(_mapping(step), caption_keys=("body", "caption", "text"), formula_keys=("footer", "formula", "result"))
        for step in raw_steps
        if isinstance(step, Mapping)
    ]


def _normalize_example_stages(spec: Mapping[str, Any]) -> list[PipelineStage]:
    raw_stages = _mapping(spec.get("example_pipeline")).get("stages", []) or []
    return [
        _normalize_stage_common(_mapping(stage), caption_keys=("caption", "body", "text"), formula_keys=("formula", "footer", "result"))
        for stage in raw_stages
        if isinstance(stage, Mapping)
    ]


def _normalize_examples(spec: Mapping[str, Any]) -> list[PipelineExample]:
    results: list[PipelineExample] = []
    for item in spec.get("examples", []) or []:
        if isinstance(item, Mapping):
            results.append(PipelineExample(
                mini_visual=_text(item.get("mini_visual")),
                text=_text(item.get("text") or item.get("caption")),
                visual_variant=_text(item.get("visual_variant")) or None,
                caption_font_size=int(item.get("caption_font_size")) if item.get("caption_font_size") is not None else None,
            ))
        else:
            text = _text(item)
            if text:
                results.append(PipelineExample(mini_visual="", text=text, visual_variant=None, caption_font_size=None))
    return results


def normalize_pipeline_family_spec(spec: Mapping[str, Any], *, variant: str) -> PipelineFamilySpec:
    variant = str(variant or "pipeline").strip().lower()
    if variant == "example_pipeline":
        stages = _normalize_example_stages(spec)
        bullets = _list_of_str(spec.get("bullets"))
        examples: list[PipelineExample] = []
    else:
        stages = _normalize_pipeline_steps(spec)
        bullets = []
        examples = _normalize_examples(spec)
        variant = "pipeline"

    return PipelineFamilySpec(
        variant=variant,
        stages=stages,
        bullets=bullets,
        examples=examples,
        takeaway=_text(spec.get("takeaway")),
        examples_label_text=_text(_mapping(spec.get("layout")).get("examples_label_text")) or _DEF_EXAMPLES_LABEL,
    )

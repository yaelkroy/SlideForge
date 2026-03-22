from __future__ import annotations

from pathlib import Path
from typing import Any

from slideforge.builders.registry import (
    DEFAULT_REGISTRY,
    BuilderRegistry,
    SlideBuilder,
    load_registry_plugins,
    register_builder,
    registry_from_environment,
)

_DEFAULT_MANIFEST = Path(__file__).with_name("manifests") / "default.json"
_DEFAULTS_LOADED = False


def register_builtin_builders(*, replace: bool = False) -> BuilderRegistry:
    global _DEFAULTS_LOADED
    if _DEFAULTS_LOADED and not replace:
        return DEFAULT_REGISTRY
    DEFAULT_REGISTRY.load_manifest(_DEFAULT_MANIFEST, replace=replace)
    _DEFAULTS_LOADED = True
    return DEFAULT_REGISTRY


def get_builder_registry(
    *,
    include_environment: bool = True,
    plugin_modules: list[str] | None = None,
    replace: bool = False,
) -> BuilderRegistry:
    registry = register_builtin_builders(replace=replace)
    if include_environment:
        registry_from_environment(replace=replace)
    if plugin_modules:
        load_registry_plugins(plugin_modules, replace=replace)
    return registry


def get_builder(kind: str) -> SlideBuilder:
    return get_builder_registry().get(kind)


def get_builder_manifest() -> dict[str, dict[str, Any]]:
    return get_builder_registry().manifest()


def _export_builders() -> dict[str, SlideBuilder]:
    return get_builder_registry().as_builder_dict()


BUILDERS = _export_builders()


__all__ = [
    "BUILDERS",
    "BuilderRegistry",
    "SlideBuilder",
    "get_builder",
    "get_builder_manifest",
    "get_builder_registry",
    "load_registry_plugins",
    "register_builder",
    "register_builtin_builders",
]

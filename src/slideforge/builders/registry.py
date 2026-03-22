from __future__ import annotations

import importlib
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

SlideBuilder = Callable[[Any, dict[str, Any], dict[str, int]], None]


def _load_builder(import_path: str) -> SlideBuilder:
    module_name, _, attr_name = str(import_path).partition(":")
    if not module_name or not attr_name:
        raise ValueError(f"Invalid builder import path: {import_path!r}. Expected 'module.path:callable_name'.")
    module = importlib.import_module(module_name)
    builder = getattr(module, attr_name)
    if not callable(builder):
        raise TypeError(f"Imported builder {import_path!r} is not callable.")
    return builder


@dataclass
class BuilderRecord:
    kind: str
    builder: SlideBuilder
    import_path: str | None = None
    aliases: set[str] = field(default_factory=set)
    tags: set[str] = field(default_factory=set)
    description: str = ""

    def as_manifest_entry(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "kind": self.kind,
            "aliases": sorted(self.aliases),
            "tags": sorted(self.tags),
        }
        if self.import_path:
            data["import"] = self.import_path
        if self.description:
            data["description"] = self.description
        return data


class BuilderRegistry:
    def __init__(self) -> None:
        self._records: dict[str, BuilderRecord] = {}
        self._aliases: dict[str, str] = {}

    def register(
        self,
        kind: str,
        builder: SlideBuilder,
        *,
        import_path: str | None = None,
        aliases: list[str] | tuple[str, ...] | set[str] | None = None,
        tags: list[str] | tuple[str, ...] | set[str] | None = None,
        description: str = "",
        replace: bool = False,
    ) -> SlideBuilder:
        normalized = str(kind).strip()
        if not normalized:
            raise ValueError("Builder kind must be a non-empty string.")
        if normalized in self._records and not replace:
            raise ValueError(f"Builder kind already registered: {normalized}")

        record = BuilderRecord(
            kind=normalized,
            builder=builder,
            import_path=import_path,
            aliases=set(str(a).strip() for a in (aliases or []) if str(a).strip()),
            tags=set(str(t).strip() for t in (tags or []) if str(t).strip()),
            description=str(description or "").strip(),
        )
        self._records[normalized] = record
        # clear stale aliases pointing to replaced kind
        for alias, target in list(self._aliases.items()):
            if target == normalized:
                del self._aliases[alias]
        for alias in record.aliases:
            self.register_alias(alias, normalized, replace=replace)
        return builder

    def register_alias(self, alias: str, target_kind: str, *, replace: bool = False) -> None:
        alias_name = str(alias).strip()
        target = str(target_kind).strip()
        if not alias_name:
            raise ValueError("Alias must be a non-empty string.")
        if target not in self._records:
            raise KeyError(f"Cannot create alias {alias_name!r}; target builder {target!r} is not registered.")
        if alias_name in self._records and alias_name != target:
            raise ValueError(f"Alias {alias_name!r} conflicts with a registered builder kind.")
        if alias_name in self._aliases and not replace and self._aliases[alias_name] != target:
            raise ValueError(f"Alias already registered: {alias_name!r}")
        self._aliases[alias_name] = target
        self._records[target].aliases.add(alias_name)

    def resolve_kind(self, kind: str) -> str:
        requested = str(kind).strip()
        if requested in self._records:
            return requested
        if requested in self._aliases:
            return self._aliases[requested]
        raise KeyError(f"Unknown builder kind: {requested}")

    def get(self, kind: str) -> SlideBuilder:
        return self._records[self.resolve_kind(kind)].builder

    def manifest(self) -> dict[str, dict[str, Any]]:
        return {kind: record.as_manifest_entry() for kind, record in sorted(self._records.items())}

    def as_builder_dict(self) -> dict[str, SlideBuilder]:
        exported = {kind: record.builder for kind, record in self._records.items()}
        for alias, target in self._aliases.items():
            exported[alias] = self._records[target].builder
        return exported

    def load_manifest(self, manifest_path: str | Path, *, replace: bool = False) -> None:
        path = Path(manifest_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        for entry in data.get("builders", []):
            kind = str(entry["kind"])
            builder = _load_builder(str(entry["import"]))
            self.register(
                kind,
                builder,
                import_path=str(entry.get("import", "") or ""),
                aliases=list(entry.get("aliases", []) or []),
                tags=list(entry.get("tags", []) or []),
                description=str(entry.get("description", "") or ""),
                replace=replace,
            )


DEFAULT_REGISTRY = BuilderRegistry()


def register_builder(
    kind: str,
    *,
    registry: BuilderRegistry | None = None,
    aliases: list[str] | tuple[str, ...] | set[str] | None = None,
    tags: list[str] | tuple[str, ...] | set[str] | None = None,
    description: str = "",
    replace: bool = False,
) -> Callable[[SlideBuilder], SlideBuilder]:
    target_registry = registry or DEFAULT_REGISTRY

    def decorator(builder: SlideBuilder) -> SlideBuilder:
        import_path = f"{builder.__module__}:{builder.__name__}"
        target_registry.register(
            kind,
            builder,
            import_path=import_path,
            aliases=aliases,
            tags=tags,
            description=description,
            replace=replace,
        )
        return builder

    return decorator


def load_registry_plugins(module_names: list[str] | tuple[str, ...], *, replace: bool = False) -> BuilderRegistry:
    # replace is accepted for API compatibility; plugin modules are expected to call register_builder.
    _ = replace
    for module_name in module_names:
        name = str(module_name).strip()
        if name:
            importlib.import_module(name)
    return DEFAULT_REGISTRY


def registry_from_environment(*, replace: bool = False) -> BuilderRegistry:
    manifest_env = os.getenv("SLIDEFORGE_BUILDER_MANIFESTS", "")
    plugin_env = os.getenv("SLIDEFORGE_BUILDER_PLUGINS", "")

    for raw_path in manifest_env.split(os.pathsep):
        path = raw_path.strip()
        if path:
            DEFAULT_REGISTRY.load_manifest(path, replace=replace)

    plugin_modules = [item.strip() for item in plugin_env.split(",") if item.strip()]
    if plugin_modules:
        load_registry_plugins(plugin_modules, replace=replace)
    return DEFAULT_REGISTRY


__all__ = [
    "BuilderRegistry",
    "DEFAULT_REGISTRY",
    "SlideBuilder",
    "load_registry_plugins",
    "register_builder",
    "registry_from_environment",
]

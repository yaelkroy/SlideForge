# LLM_CONTEXT.md

## Project Identity

`LLM_CONTEXT.md` is the primary architecture and continuity guide for future development and LLM-assisted work on this repository.

- **Project name:** SlideForge
- **Project type:** Python presentation generation engine
- **Primary role:** general-purpose, spec-driven slide and presentation engine
- **Current example project:** Machine Learning Foundations lecture deck
- **Primary output today:** `.pptx`
- **Longer-term direction:** richer outputs may later include previews, images, diagrams, charts, and other media-oriented assets, but the repo should always be documented first in terms of the code that actually exists in the working tree.

---

## One-Sentence Mission

Build a **Python-native, spec-driven, modular presentation engine** that can generate polished presentations while staying easy for an LLM to understand, edit, extend, and recover with limited context.

---

## The Most Important Rule

This project must be designed for **small-context recovery**.

That means:
- many small modules
- stable file names
- one responsibility per file when practical
- explicit registries
- explicit project specs
- explicit documentation
- minimal hidden conventions
- minimal giant files
- minimal “magic” wiring that only makes sense after reading the entire repo

If something can be made more explicit for future LLM understanding, do it.

---

## Universal Platform Rule

SlideForge must be treated as a **general presentation engine**, not as a machine-learning-only product.

The ML lecture deck is the current example project in the repository, not the architectural boundary of the engine.

This means:
- builders should represent reusable composition families
- layout helpers should be domain-agnostic
- theme systems should remain presentation-agnostic
- render helpers should stay reusable across many deck types
- domain-specific visuals should be organized as packs
- project specs should live above the engine layer
- the app entrypoint should build arbitrary slide sequences, not one hardcoded deck

When a future change makes the engine more specific to one deck, pull that change back up into `projects/` or a project-local preset layer.

---

## Current Repository Truth

When editing this repo, describe it in terms of the **actual working tree first**.

Current repository facts reflected in the fresh tree:
- `src/slideforge/app/build_deck.py` is the generic build entrypoint
- `src/slideforge_app.py` is only an example launcher
- `build_deck(...)`, `load_slides(...)`, and project aliases under `PROJECT_TARGETS` are the current build-facing API
- the builder registry is now manifest-driven through `src/slideforge/builders/manifests/default.json`
- the real registry implementation lives in `src/slideforge/builders/registry.py`
- compatibility builder wrappers remain in the tree for migration safety
- geometry visuals have been split into pack modules under `src/slideforge/assets/packs/geometry/`
- the engine now includes `analytic_panel`, `annotated_pipeline`, and `multi_panel_summary` as primary composition-semantic families

Documentation should not pretend that current files are already gone if they still exist as wrappers.
If compatibility files remain in the tree, say so.

---

## File Size Rule

For **logic and engine files**, keep Python files under **500 lines when practical**.

This primarily applies to:
- builders
- layout helpers
- render helpers
- registry helpers
- style helpers
- asset-generation helpers
- normalization helpers

If a logic file drifts beyond 500 lines, that is a strong signal to split responsibilities.

Most engine files should preferably be around **200 lines** when practical.
That is a preference, not a rigid rule, but it should guide refactoring decisions.

### Important exception
This rule does **not** apply the same way to presentation-spec files such as:
- `slides_part1.py`
- `slides_part2.py`
- other future deck-spec modules

Those may legitimately be longer when they are mostly declarative content and splitting them would hurt readability.

---

## Documentation Sync Rule

Whenever the architecture, builder families, entrypoint, registry system, or project structure changes in a meaningful way, update:
- `README.md`
- `LLM_CONTEXT.md`
- `SLIDE_SPEC_RULES.md`

Do not let docs silently drift behind the code.

If a refactor changes naming, package layout, entrypoint usage, builder-family semantics, or registry behavior, the docs should be updated in the same working pass.

---

## Priority Rule for Docs

When there is tension between docs:
1. `LLM_CONTEXT.md` defines architectural intent and continuity rules
2. `README.md` explains the current repo to humans using the project
3. `SLIDE_SPEC_RULES.md` defines how slide specs should be written

These files should agree. If they do not, reconcile them instead of letting contradictions accumulate.

---

## Current Build Flow

The working mental model should be:

**slide specs -> build_deck -> builder registry -> builder family -> layout helpers -> render helpers / visual packs -> pptx output**

Current concrete pieces:
- `slideforge.app.build_deck.build_deck(...)`
- `slideforge.app.build_deck.load_slides(...)`
- `slideforge.builders.builder_registry.BUILDERS`
- builder manifest in `builders/manifests/default.json`
- compatibility wrapper `src/slideforge_app.py`

The app layer should stay generic. The engine should not become hard-coded to `ML_FOUNDATIONS_SLIDES` again.

---

## Builder Naming Rule

### Canonical composition families
Use composition-semantic names as the primary vocabulary:
- `analytic_panel`
- `multi_panel_summary`
- `annotated_pipeline`
- `concept_poster`
- `dependency_map`
- `notation_panel`
- `card_grid`
- `title_composite`
- `section_divider`
- `pipeline`

### Compatibility aliases
Legacy names may exist as aliases for backward compatibility:
- `worked_example_panel` -> `analytic_panel`
- `worked_example` -> `analytic_panel`
- `example_pipeline` -> `annotated_pipeline`
- `triple_role` -> `multi_panel_summary`

There are still compatibility wrapper files in the current tree. That is acceptable during migration.
When writing new specs or new docs, prefer the canonical composition name.

---

## Builder Family Rules

### Builders orchestrate only
A builder should mainly:
- resolve theme or family style
- normalize spec content if needed
- ask layout for boxes and candidate decisions
- call render helpers to draw blocks
- add footer and slide shell pieces

Builders should avoid growing into monoliths that also own:
- style preset engines disconnected from themes
- large text-fit subsystems
- layout solvers
- domain-specific normalization logic
- multiple unrelated rendering utilities

### Good split pattern
A builder family should trend toward:
- `builders/<family>.py`
- `layout/<family>.py`
- `render/<family>_blocks.py` or equivalent
- `style/<family>_style.py`
- `spec/<family>_normalization.py` when needed

Not every family needs all of these immediately, but this is the preferred direction.

---

## Registry Rule

The builder registry should move toward a declarative model.

Current preferred direction:
- compatibility façade in `builders/builder_registry.py`
- real registry class in `builders/registry.py`
- manifest-driven built-in builders
- alias support in manifests
- optional decorator registration
- optional plugin-pack loading

The long-term goal is to avoid a hardcoded central dict that must be manually edited forever.

---

## Assets Rule

Domain-specific visuals are allowed, but they must not become the conceptual core of the engine.

Preferred pattern:
- shared drawing primitives in `assets/mini_visuals_common.py`
- public visual dispatch in `assets/mini_visuals.py`
- domain packs in `assets/packs/<domain>/...`
- compatibility aggregation layers only when needed

Current example:
- geometry visuals live under `assets/packs/geometry/`
- `mini_visuals_geometry.py` exists as a compatibility façade/aggregation layer

That is the right direction.

---

## Visual Metadata Rule

Visual assets that materially affect layout should expose metadata the layout solver can use.

Useful metadata includes:
- preferred layout orientation
- minimum readable width
- minimum readable height
- preferred aspect ratio
- label density
- whether the visual is text-bearing
- whether shallow top-strip placement is allowed
- whether hero simplification is needed for divider/title use

Current geometry packs already follow this pattern in places. Continue it.

This is important because the layout engine should not treat every image as equally flexible.

---

## Layout Rule

Layout modules should allocate boxes and evaluate layout choices, not draw content.

### Layout modules should do:
- reserve regions
- compute box sizes and positions
- evaluate candidate layouts when needed
- enforce readability thresholds
- return a structured result the builder can render

### Layout modules should avoid:
- theme resolution
- direct drawing
- domain-specific wording
- project-specific content assumptions

This is especially important for:
- `layout/poster.py`
- `layout/analytic_panel.py`
- `layout/pipeline.py`
- `layout/multi_panel_summary.py`

---

## Readability and Auto-Split Rule

A slide should not be accepted just because a layout function returned boxes.

The engine should increasingly prefer:
- candidate-layout search instead of one fixed solve
- hard readability thresholds for text and image regions
- metadata-aware rejection of compressed visuals
- conservative bottom-line safety margins for text boxes
- automatic fallback from one orientation to another
- optional split recommendation or auto-split when all candidates fail

Current analytic-panel work is already moving in this direction. Keep pushing there rather than hardcoding slide-by-slide hacks.

---

## Render Rule

Render modules should draw reusable blocks only.

Examples:
- text blocks
- cards and surface panels
- connectors and arrows
- title panels
- pipeline blocks
- multi-panel cards
- formula and derivation blocks

They should not carry project semantics.

---

## Theme Rule

The theme system under `config/themes.py` is the primary styling layer.

Builder-family styling should prefer:
- theme-derived values
- family style helpers under `style/`
- explicit spec overrides

Avoid letting one builder family create an isolated parallel style system disconnected from the theme layer.

---

## Project Rule

The `projects/` package is where deck semantics belong.

Current example project:
- `projects/ml_foundations/slides_part1.py`
- `projects/ml_foundations/slides_part2.py`

Project modules may legitimately be long when they are mostly declarative content.
That is acceptable.

What should **not** happen is engine code silently absorbing ML-deck-specific assumptions that belong in project specs.

---

## Compatibility Rule

Compatibility aliases and wrapper files are acceptable when they reduce breakage during a family rename or architectural migration.

Examples currently present:
- legacy builder names resolved by manifest aliases
- compatibility wrapper files such as `worked_example_panel.py`, `example_pipeline.py`, and `triple_role.py`

However:
- new work should prefer the canonical names
- compatibility layers should stay thin
- docs should describe them honestly as compatibility layers, not as the preferred architecture

---

## Practical Recovery Rule

When making changes, prefer edits that improve future recoverability:
- split large files
- reduce duplicated helper logic
- keep imports easy to trace
- make global behavior explicit
- keep registries and manifests inspectable
- keep docs synchronized with the actual tree

The goal is not abstraction for its own sake.
The goal is to make the engine easier to understand, safer to evolve, and less likely to regress visually while being refactored.

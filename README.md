# SlideForge

SlideForge is a **Python-native, spec-driven presentation engine** for generating polished PowerPoint decks from structured Python slide specifications.

The repository’s current example project is a **Machine Learning Foundations** lecture deck, but the engine is intended to remain **general-purpose** rather than lecture-specific.

---

## What SlideForge is

SlideForge should be understood as a reusable presentation engine, not a one-off deck template.

It is built around a few core ideas:

- **project slide specs** define content declaratively
- a **builder registry** maps slide `kind` values to builder functions
- **builders** implement reusable slide patterns
- **theme, header, and layout layers** centralize styling and geometry
- **render primitives** and **mini-visuals** support diagrams, panels, and structured explanatory visuals
- the system generates a final `.pptx` deck from a selected project slide list

The current top-level executable path builds a combined Machine Learning Foundations deck from `ML_FOUNDATIONS_SLIDES`.

---

## Current status

The repository is no longer a single-script prototype. It is a working modular codebase under `src/slideforge/` with dedicated packages for application orchestration, assets, builders, configuration, layout, rendering, projects, and utilities.

Current package structure on `main`:

```text
SlideForge/
├─ README.md
├─ LLM_CONTEXT.md
├─ SLIDE_SPEC_RULES.md
├─ pyproject.toml
├─ ML_Foundations_Auto.pptx
├─ ML_Foundations_Auto.pdf
└─ src/
   ├─ slideforge_app.py
   └─ slideforge/
      ├─ app/
      ├─ assets/
      ├─ builders/
      ├─ config/
      ├─ io/
      ├─ layout/
      ├─ projects/
      ├─ render/
      └─ utils/
```

This means the repo should now be documented and extended as an actual engine with explicit layers, not as an ad hoc PowerPoint script.

---

## Current build flow

The current top-level entrypoint is:

```bash
python src/slideforge_app.py
```

At a practical level, the current build flow is:

```text
project slide specs
→ builder registry
→ slide builders
→ theme / header / layout helpers
→ render primitives / mini visuals
→ .pptx output
```

`src/slideforge_app.py` currently:

1. ensures runtime directories exist
2. validates backgrounds for the selected slide list
3. creates a presentation object
4. iterates through slide specs
5. dispatches each slide by `spec["kind"]` through `BUILDERS`
6. saves the resulting deck to the configured output path

---

## Installation

### Requirements

- Python **3.10+**

### Current project dependencies

Defined in `pyproject.toml`:

- `python-pptx`
- `matplotlib`
- `numpy`

### Recommended setup

```bash
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -U pip
pip install -e .
```

Then run:

```bash
python src/slideforge_app.py
```

---

## Repository layout

### `src/slideforge/app/`
Application-level orchestration.

Current files:
- `build_deck.py`
- `presentation_factory.py`
- `slide_utils.py`

Use this layer for deck assembly, presentation creation, and top-level orchestration helpers.

### `src/slideforge/assets/`
Reusable visual asset helpers and mini-visual generation.

Current files include:
- `mini_visuals.py`
- `mini_visuals_common.py`
- `mini_visuals_core.py`
- `mini_visuals_geometry.py`

These modules exist to support lightweight explanatory visuals rather than forcing every slide to rely on text alone.

### `src/slideforge/builders/`
Reusable slide-pattern builders.

Current files include:
- `basic.py`
- `builder_registry.py`
- `card_grid.py`
- `common.py`
- `concept_poster.py`
- `dependency_map.py`
- `example_pipeline.py`
- `notation_panel.py`
- `pipeline.py`
- `prereq_grid.py`
- `section_divider.py`
- `title_composite.py`
- `triple_role.py`
- `triple_role_bands.py`
- `triple_role_panels.py`
- `triple_role_style.py`

The registry currently maps slide kinds such as:
- `title`
- `title_composite`
- `section`
- `section_divider`
- `bullets`
- `formula`
- `two_column`
- `image`
- `dependency_map`
- `pipeline`
- `prereq_grid`
- `example_pipeline`
- `card_grid`
- `notation_panel`
- `triple_role`
- `integrated_bridge`
- `concept_poster`

### `src/slideforge/config/`
Cross-cutting configuration.

Current files include:
- `constants.py`
- `paths.py`
- `themes.py`

The theme layer is now a real part of the architecture, not just a future idea.

### `src/slideforge/io/`
I/O-oriented helpers.

Current file:
- `backgrounds.py`

### `src/slideforge/layout/`
Presentation geometry, spacing, and text-fit logic.

Current files include:
- `autofit.py`
- `base.py`
- `cards.py`
- `dependency.py`
- `grid.py`
- `poster.py`
- `stack.py`
- `table.py`
- `text_fit.py`

This package should be treated as a first-class layout layer rather than as a pile of ad hoc helper functions.

### `src/slideforge/projects/`
Project-level content definitions.

Current project package:
- `ml_foundations/`

Inside `ml_foundations/`:
- `slides_part1.py`
- `slides_part2.py`
- `__init__.py`

`__init__.py` exports:
- `ML_FOUNDATIONS_PART1_SLIDES`
- `ML_FOUNDATIONS_PART2_SLIDES`
- `ML_FOUNDATIONS_SLIDES`

### `src/slideforge/render/`
Reusable rendering logic for PowerPoint-level shapes, text, and shared visual structures.

### `src/slideforge/utils/`
Smaller general helpers.

Current files:
- `text_layout.py`
- `units.py`

---

## Current architectural model

### 1. Slide specs are data-first

Slides are currently defined as Python dictionaries inside project packages. Each slide spec declares its `kind` and the content expected by the selected builder.

### 2. Builders represent reusable patterns

A builder should represent a reusable slide family, not a single lecture topic. If a pattern repeats across multiple slides, that is a strong signal it deserves its own builder.

### 3. Layout is moving toward explicit geometry

The repo is increasingly treating layout as a geometry problem rather than manual coordinate tweaking repeated across files.

### 4. Theme and header systems are shared infrastructure

Color behavior, dark/light behavior, title treatment, divider handling, and subtitle placement should increasingly route through shared systems instead of being reimplemented inside each builder.

### 5. Mini-visuals are part of the engine

The engine supports lightweight explanatory diagrams and generated visuals as first-class components of slide composition.

---

## Theme system

`src/slideforge/config/themes.py` now contains a real theme layer built around `SlideTheme` plus named presets.

Current named presets include:
- `light_academic`
- `dark_hero`
- `dark_section`

When extending the repo, prefer theme-driven styling over builder-local hardcoded colors whenever practical.

---

## Header and layout direction

The repo now has explicit shared support for:

- title/subtitle/header layout
- text fitting
- card and poster layout
- dependency-map geometry
- table and stack distribution

That is an important architectural shift.

Future work should continue moving repeated spacing logic into shared layout helpers instead of scattering it back across many builder files.

---

## Project philosophy

SlideForge should remain a **universal presentation platform**.

That means:

- engine modules should stay reusable across many presentation domains
- builder names should describe reusable patterns, not one course only
- shared visual helpers should be organized by visual family
- project content should stay above the engine layer
- the Machine Learning Foundations deck should remain an example project, not the definition of the whole repo

---

## Development conventions

### Prefer explicit structure over hidden magic

This repo should remain easy to recover and extend with limited context. Favor:

- small focused modules
- stable import paths
- explicit registries
- explicit docs
- predictable package boundaries

### Keep logic files small

When practical:

- Python code files should stay under **500 lines**
- most logic, helper, builder, and layout files should preferably stay around **200 lines or less**

This guideline applies primarily to engine logic, not necessarily to longer declarative slide-spec files.

### Update docs when code structure changes

When architecture, module locations, builder inventory, slide-spec rules, or execution flow change, review and update:

- `README.md`
- `LLM_CONTEXT.md`
- `SLIDE_SPEC_RULES.md`

Documentation drift should be called out explicitly rather than silently ignored.

---

## Known repo consistency note

The current `main` branch shows one visible inconsistency that should be reconciled:

- `builder_registry.py` still registers and imports `integrated_bridge`
- the builders directory listing currently shows `integrated_bridge.py.bak`
- the direct `integrated_bridge.py` path currently returns 404 on GitHub raw/blob URLs

So the documentation should acknowledge that the repo is modular and working in direction, but still has at least one concrete registry/file-tree mismatch to clean up.

---

## Documentation map

Use the docs in this order:

- **`README.md`** — high-level repo overview, current structure, how to run, and current architecture summary
- **`LLM_CONTEXT.md`** — detailed architecture and continuity guide for future development and LLM-assisted work
- **`SLIDE_SPEC_RULES.md`** — authoring and design rules for writing slide specs

---

## Current scope and future direction

Today, SlideForge’s actual codebase is centered on generating `.pptx` decks.

Longer term, the design direction can support richer outputs and richer media workflows, but documentation should always describe the repo first in terms of what is **already present and real** in the current codebase.

That means the project should keep evolving incrementally:

- strengthen reusable builders
- continue splitting oversized logic files
- expand theme/header/layout reuse
- improve consistency between registry state and file tree
- keep project specs readable and declarative
- preserve the engine’s general-purpose identity

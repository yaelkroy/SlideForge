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
- domain visuals should be organized as packs
- project-specific content should live above the engine layer
- naming should support reuse across many kinds of presentations

Prefer composition-semantic names like:
- `analytic_panel`
- `multi_panel_summary`
- `annotated_pipeline`
- `concept_poster`
- `dependency_map`
- `notation_panel`
- `title_composite`

Compatibility aliases may exist for legacy decks, but they should not be treated as the long-term architectural vocabulary.

---

## Current Architectural Direction

The engine is moving toward a structure with four clear layers:

1. **builders/**
   - orchestration only
   - choose style, layout, and rendering helpers
   - no large embedded solver logic

2. **layout/**
   - box allocation only
   - no theme logic
   - no deck-semantic guessing

3. **render/**
   - reusable drawing primitives and block renderers
   - no project-specific behavior

4. **projects/**
   - slide specs and project-local content only
   - long declarative slide files are acceptable here

Additional support layers:
- **assets/** for visual packs and drawing helpers
- **style/** for builder-family style resolution layered on top of themes
- **spec/** for normalization of family-specific spec shapes
- **config/** for constants, theme system, and paths

---

## File Size and Responsibility Rules

### Hard limit rule
For **logic and engine files**, keep Python files under **500 lines when practical**.

This applies especially to:
- builders
- layout modules
- render modules
- style helpers
- registry modules
- spec normalizers
- asset generation helpers

### Preferred target
Most engine files should preferably be around **200 lines** when practical.

This is not a rigid aesthetic rule. It exists because smaller files improve:
- LLM recoverability
- reviewability
- refactor safety
- explicit separation of concerns

### Exception
Large declarative presentation-spec files are allowed when splitting them would hurt readability.

Examples:
- `slides_part1.py`
- `slides_part2.py`
- future long project deck specs

These are content files, not engine-logic files.

---

## No Semantic Guessing in Engine Modules

One of the main architectural corrections in this repo is:

**engine modules should not guess slide meaning when the spec can say it explicitly.**

Prefer explicit spec/profile selection like:
- `layout_profile="text_dominant"`
- `layout_profile="visual_dominant"`
- `poster_profile="compact_concept"`
- `poster_profile="analytic_steps"`

Avoid building more hidden heuristics like:
- infer “dense math mode” from formula count unless strictly necessary for backward compatibility
- infer “compact concept mode” from content density unless used only as a legacy fallback

Backward-compatible inference may temporarily exist, but explicit profiles should be the long-term direction.

---

## Current Repo Reality

Describe the repo according to the working tree that exists now or the intended post-refactor tree being actively maintained — not according to stale GitHub views, imagined future trees, or abandoned plans.

The modern codebase is a real modular repo under `src/slideforge/`, including:
- `app/`
- `assets/`
- `builders/`
- `config/`
- `io/`
- `layout/`
- `projects/`
- `render/`
- `spec/`
- `style/`
- `utils/`

This is not a one-file prototype anymore.

---

## Practical Repository Structure

```text
SlideForge/
├─ README.md
├─ LLM_CONTEXT.md
├─ SLIDE_SPEC_RULES.md
├─ pyproject.toml
└─ src/
   ├─ slideforge_app.py
   └─ slideforge/
      ├─ app/
      ├─ assets/
      │  └─ packs/
      ├─ builders/
      ├─ config/
      ├─ io/
      ├─ layout/
      ├─ projects/
      ├─ render/
      ├─ spec/
      ├─ style/
      └─ utils/
```

When documenting the repo, prefer this package-oriented structure over obsolete or overly narrow trees.

---

## Entrypoint Rule

SlideForge should not be hard-bound to one example deck.

Preferred engine API:
- `build_deck(slides, output_file, theme_overrides=None)`

Preferred launcher behavior:
- CLI or runner chooses a project alias or a module target
- `slideforge_app.py` acts as an example launcher, not the architectural core of the engine

The engine should be able to render **arbitrary slide lists** without recoding the app entrypoint.

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

### Compatibility aliases
Legacy names may exist as aliases for backward compatibility:
- `worked_example_panel` -> `analytic_panel`
- `worked_example` -> `analytic_panel`
- `example_pipeline` -> `annotated_pipeline`
- `triple_role` -> `multi_panel_summary`

When writing new specs or new docs, prefer the canonical composition name.

---

## Builder Family Rules

### Builders orchestrate only
A builder should mainly:
- resolve theme/family style
- normalize spec content if needed
- ask layout for boxes
- call render helpers to draw blocks
- add footer and slide shell pieces

Builders should avoid growing into monoliths that also own:
- style preset engines
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

Preferred direction:
- compatibility façade in `builders/builder_registry.py`
- real registry class in `builders/registry.py`
- manifest-driven built-in builders
- optional decorator registration
- optional plugin-pack loading

The long-term goal is to avoid a hardcoded central dict that must be manually edited forever.

---

## Assets Rule

Domain-specific visuals are welcome, but they should be organized as **packs**.

For example:
- `assets/packs/geometry/heroes.py`
- `assets/packs/geometry/points_vectors.py`
- `assets/packs/geometry/norms_dots_angles.py`
- `assets/packs/geometry/projections_orthogonality.py`

`mini_visuals_common.py` should remain focused on shared drawing helpers.

This keeps SlideForge universal while still supporting heavy domain packs for math, science, business diagrams, or other content families.

---

## Theme and Style Rule

The theme system under `config/themes.py` is the main styling layer.

Builder-family styling should preferably:
- derive from `SlideTheme`
- use family-specific helpers under `style/`
- support explicit spec overrides

Avoid creating detached local preset systems that duplicate theme logic and drift out of sync.

---

## Documentation Sync Rule

Whenever the architecture changes, update these files together:
- `README.md`
- `LLM_CONTEXT.md`
- `SLIDE_SPEC_RULES.md`

If builder names, registry behavior, entrypoint behavior, or repo structure changes, documentation must be updated in the same wave.

---

## Priority of Documentation Sources

When resolving documentation conflicts:

1. **The working code tree** is the source of truth.
2. `README.md` should describe the repo for a human reader.
3. `LLM_CONTEXT.md` should explain architecture, continuity, and design intent.
4. `SLIDE_SPEC_RULES.md` should define how slide specs are written and maintained.

Do not let older documentation override the real code.

---

## Compatibility Rule

Refactors should preserve compatibility when practical.

Good strategies:
- compatibility wrappers
- registry aliases
- façade modules that re-export moved functions
- compatibility import paths during renames

The goal is to improve architecture **without** forcing the entire project layer to be rewritten at once.

---

## Anti-Drift Reminder

Do not silently let the engine drift back toward:
- giant builders
- deck-specific logic inside engine modules
- hidden behavior heuristics
- one-off naming tied to one lecture deck
- duplicated local styling systems
- hardcoded app entrypoints for one project

SlideForge should stay understandable, recoverable, and reusable.

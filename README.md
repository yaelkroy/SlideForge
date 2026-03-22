# SlideForge

SlideForge is a **Python-native, spec-driven presentation engine** for generating polished PowerPoint decks from structured slide specifications.

It is designed to support many kinds of presentations, including:
- academic lecture decks
- technical presentations
- business presentations
- project kickoffs
- training materials
- research talks
- architecture and system-design decks
- roadmap and strategy decks
- educational visual explainers

The current example project in the repository is a machine-learning lecture deck, but that is only one example project. The engine itself is intended to remain **general-purpose**.

---

## Current Direction

SlideForge should be treated as a **universal presentation platform**.

That means:
- engine modules should be reusable across many domains
- builders should represent reusable composition families
- layouts should allocate regions generically instead of encoding deck semantics
- render helpers should stay reusable across many deck types
- domain visuals should be organized as packs
- project specs should live above the engine layer
- the entrypoint should render arbitrary slide specs, not one hardcoded deck

The ML lecture deck is the current example project, not the architectural boundary of the platform.

---

## Core Build Flow

The intended build flow is:

**project slide specs -> builder registry -> slide builders -> theme/header/layout helpers -> rendering helpers / mini visuals -> pptx output**

In the refactored architecture:
- `src/slideforge/app/build_deck.py` is the generic engine entrypoint
- `build_deck(slides, output_file, theme_overrides=None)` is the primary programmatic API
- the CLI or launcher chooses the project spec target
- `src/slideforge_app.py` becomes an example launcher, not the engine core
- builder dispatch is handled by a declarative registry with manifest support and compatibility aliases

---

## Repository Structure

```text
SlideForge/
├─ README.md
├─ LLM_CONTEXT.md
├─ SLIDE_SPEC_RULES.md
├─ pyproject.toml
├─ src/
│  ├─ slideforge_app.py
│  └─ slideforge/
│     ├─ app/
│     │  ├─ build_deck.py
│     │  ├─ presentation_factory.py
│     │  └─ slide_utils.py
│     ├─ assets/
│     │  ├─ mini_visuals.py
│     │  ├─ mini_visuals_common.py
│     │  ├─ mini_visuals_core.py
│     │  ├─ mini_visuals_geometry.py
│     │  └─ packs/
│     │     └─ geometry/
│     │        ├─ heroes.py
│     │        ├─ points_vectors.py
│     │        ├─ norms_dots_angles.py
│     │        └─ projections_orthogonality.py
│     ├─ builders/
│     │  ├─ analytic_panel.py
│     │  ├─ annotated_pipeline.py
│     │  ├─ basic.py
│     │  ├─ builder_registry.py
│     │  ├─ card_grid.py
│     │  ├─ common.py
│     │  ├─ concept_poster.py
│     │  ├─ dependency_map.py
│     │  ├─ multi_panel_summary.py
│     │  ├─ notation_panel.py
│     │  ├─ pipeline.py
│     │  ├─ prereq_grid.py
│     │  ├─ section_divider.py
│     │  ├─ title_composite.py
│     │  └─ compatibility aliases such as:
│     │     ├─ worked_example_panel.py
│     │     ├─ example_pipeline.py
│     │     └─ triple_role.py
│     ├─ config/
│     │  ├─ constants.py
│     │  ├─ paths.py
│     │  └─ themes.py
│     ├─ io/
│     │  └─ backgrounds.py
│     ├─ layout/
│     │  ├─ analytic_panel.py
│     │  ├─ poster.py
│     │  ├─ dependency.py
│     │  ├─ grid.py
│     │  ├─ stack.py
│     │  ├─ table.py
│     │  ├─ text_fit.py
│     │  └─ other generic layout helpers
│     ├─ projects/
│     │  └─ ml_foundations/
│     │     ├─ __init__.py
│     │     ├─ slides_part1.py
│     │     └─ slides_part2.py
│     ├─ render/
│     │  ├─ header.py
│     │  ├─ text.py
│     │  ├─ cards.py
│     │  ├─ connectors.py
│     │  ├─ decorations.py
│     │  ├─ primitives.py
│     │  ├─ title_panels.py
│     │  ├─ pipeline_blocks.py
│     │  ├─ multi_panel_cards.py
│     │  └─ math_blocks.py
│     ├─ spec/
│     │  ├─ pipeline_normalization.py
│     │  └─ other spec-normalization helpers
│     ├─ style/
│     │  ├─ title_style.py
│     │  ├─ multi_panel_summary_style.py
│     │  └─ other family style helpers
│     └─ utils/
│        ├─ text_layout.py
│        └─ units.py
```

This tree reflects the intended post-refactor organization: **generic engine modules first, project specs second, compatibility aliases where needed**.

---

## Composition Families

SlideForge should prefer **composition-semantic names** over lecture-semantic names.

### Primary composition names
- `title_composite`
- `section_divider`
- `concept_poster`
- `pipeline`
- `annotated_pipeline`
- `dependency_map`
- `notation_panel`
- `card_grid`
- `analytic_panel`
- `multi_panel_summary`

### Compatibility aliases
Old names may remain as compatibility wrappers so existing decks do not break:
- `worked_example_panel` -> `analytic_panel`
- `worked_example` -> `analytic_panel`
- `example_pipeline` -> `annotated_pipeline`
- `triple_role` -> `multi_panel_summary`

The universal name should be treated as canonical for all new work.

---

## Builder Registry

The builder registry is moving toward a more declarative system.

Current design direction:
- compatibility façade in `builders/builder_registry.py`
- real registry logic in `builders/registry.py`
- data-driven built-in registry through JSON manifests
- optional plugin-pack loading
- optional decorator-based builder registration

The goal is to avoid a future where every new builder family requires editing one central hardcoded dictionary forever.

---

## Assets and Visual Packs

SlideForge supports reusable mini visuals, but domain-specific visuals should be organized as **packs**, not treated as the engine core.

Example:
- geometry visuals live under `assets/packs/geometry/`
- `mini_visuals_common.py` stays focused on shared drawing helpers
- `mini_visuals_geometry.py` can remain as a compatibility façade or aggregation layer

This keeps the engine universal while still supporting geometry-heavy, math-heavy, or otherwise domain-specific projects.

---

## Themes and Styling

The theme system under `config/themes.py` remains the primary styling layer.

Builder-family styling should prefer:
- theme-derived style resolution
- family-specific style helpers under `style/`
- explicit overrides from slide specs

Avoid letting one builder family invent a parallel styling universe disconnected from the theme system.

---

## Programmatic Use

Typical generic usage should look like:

```python
from slideforge.app.build_deck import build_deck
from slideforge.projects.ml_foundations import ML_FOUNDATIONS_PART1_SLIDES

build_deck(ML_FOUNDATIONS_PART1_SLIDES, "out/part1.pptx")
```

Or by project/target selection from the launcher:

```bash
python src/slideforge_app.py --project ml_foundations
python src/slideforge_app.py --slides-target slideforge.projects.ml_foundations:ML_FOUNDATIONS_PART2_SLIDES
```

The engine should be able to render **arbitrary slide lists** without being hard-wired to the ML deck.

---

## Dependencies

The current `pyproject.toml` defines the engine runtime.

At minimum, the repo is built around:
- Python `>=3.10`
- `python-pptx`
- `matplotlib`
- `numpy`

---

## Documentation

The repository includes:
- `README.md` — user-facing repo overview
- `LLM_CONTEXT.md` — architecture and continuity guide for future development and LLM-assisted work
- `SLIDE_SPEC_RULES.md` — rules for writing and maintaining slide specs

These files should be updated **together** whenever the engine architecture, naming, or project structure changes.

---

## Important Practical Rule

SlideForge should evolve without losing recoverability.

That means:
- prefer many small modules
- keep responsibilities explicit
- keep registries and project specs easy to trace
- keep compatibility aliases when renaming a family
- make global behavior opt-in through specs or profiles rather than hidden heuristics

The goal is not to create framework theater.
The goal is to make the engine easier to extend, safer to edit, and less likely to break one deck while fixing another.

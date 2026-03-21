# SlideForge

SlideForge is a Python-native, spec-driven presentation engine for generating polished PowerPoint decks.

It is designed to generate many kinds of presentations, including:
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

## Current Status

SlideForge is a real modular deck-generation codebase, not just a static template repo.

The current architecture already includes:
- project slide specs under `src/slideforge/projects/`
- explicit builder dispatch through a builder registry
- reusable theme, header, layout, and primitive rendering layers
- reusable mini-visual generation for diagrams and concept visuals
- modular builder families for repeated slide patterns
- generation of a final `.pptx` deck from Python slide specs

The repo is also still mid-refactor. Some proposed cleanup work has not yet landed in `main`, so the documentation below is written to match the code that actually exists now.

---

## Repository Structure

```text
SlideForge/
├─ README.md
├─ LLM_CONTEXT.md
├─ SLIDE_SPEC_RULES.md
├─ pyproject.toml
├─ ML_Foundations_Auto.pdf
├─ ML_Foundations_Auto.pptx
└─ src/
   ├─ slideforge_app.py
   ├─ slideforge.egg-info/
   └─ slideforge/
      ├─ app/
      │  ├─ build_deck.py
      │  ├─ presentation_factory.py
      │  └─ slide_utils.py
      ├─ assets/
      │  ├─ mini_visuals.py
      │  ├─ mini_visuals_common.py
      │  ├─ mini_visuals_core.py
      │  └─ mini_visuals_geometry.py
      ├─ builders/
      │  ├─ basic.py
      │  ├─ builder_registry.py
      │  ├─ card_grid.py
      │  ├─ common.py
      │  ├─ concept_poster.py
      │  ├─ dependency_map.py
      │  ├─ example_pipeline.py
      │  ├─ notation_panel.py
      │  ├─ pipeline.py
      │  ├─ prereq_grid.py
      │  ├─ section_divider.py
      │  ├─ title_composite.py
      │  ├─ triple_role.py
      │  ├─ triple_role_bands.py
      │  ├─ triple_role_panels.py
      │  ├─ triple_role_style.py
      │  └─ integrated_bridge.py.bak
      ├─ config/
      │  ├─ constants.py
      │  ├─ paths.py
      │  └─ themes.py
      ├─ io/
      │  └─ backgrounds.py
      ├─ layout/
      │  ├─ autofit.py
      │  ├─ base.py
      │  ├─ cards.py
      │  ├─ dependency.py
      │  ├─ grid.py
      │  ├─ poster.py
      │  ├─ stack.py
      │  ├─ table.py
      │  └─ text_fit.py
      ├─ projects/
      │  └─ ml_foundations/
      │     ├─ __init__.py
      │     ├─ slides_part1.py
      │     └─ slides_part2.py
      ├─ render/
      │  ├─ header.py
      │  └─ primitives.py
      └─ utils/
         ├─ text_layout.py
         └─ units.py
```

---

## Core Principle

SlideForge should be treated as a universal presentation platform.

That means:
- engine modules should be reusable across many domains
- builder families should represent reusable slide patterns
- shared visual modules should be organized by visual family, not one deck section
- project specs should live above the engine layer
- machine learning is an example project, not the boundary of the platform

---

## How It Works

The intended build flow is:

**project slide specs -> builder registry -> slide builders -> theme/header/layout helpers -> rendering primitives / mini visuals -> pptx output**

In the current repo:
- `src/slideforge_app.py` is the executable entrypoint
- `builder_registry.py` maps slide `kind` values to concrete builder functions
- project content lives in `src/slideforge/projects/`
- headers, themes, and layout helpers are increasingly centralized rather than reimplemented in every builder

---

## Current Builder Families

The active builder registry currently supports these slide kinds:
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
- `concept_poster`

Important current note:
- `integrated_bridge` is not currently active in the registry
- there is no dedicated `worked_example` builder in the current pushed repo

---

## Dependencies

The current `pyproject.toml` defines:
- Python `>=3.10`
- `python-pptx`
- `matplotlib`
- `numpy`

---

## How to Run

From the repo root:

```bash
python src/slideforge_app.py
```

---

## Honest Current Note

The current repo has an important inconsistency:

- `src/slideforge_app.py` imports `ML_FOUNDATIONS_SLIDES`
- `src/slideforge/projects/ml_foundations/__init__.py` currently exports only `ML_FOUNDATIONS_PART1_SLIDES`

So the intended entrypoint is clear, but the current pushed state should be treated as needing one cleanup step before the package export path is fully consistent.

Also:
- `slides_part2.py` exists in the repo
- but Part II is not currently exported through the package `__init__.py`

This README is intentionally honest about that instead of pretending the refactor is already complete.

---

## Current Design Direction

The repo is moving toward:
- builder-driven slide generation
- reusable rendering primitives
- reusable mini-visual families
- shared theme and header systems
- reusable layout and text-fit helpers
- clearer project-level slide spec organization
- many small files with explicit responsibilities

At the same time, the project should avoid unnecessary churn. The goal is not a giant framework rewrite. The goal is to keep presentation generation working while making the codebase easier to extend, safer to edit, and easier for future LLM sessions to recover.

---

## Documentation

The repository includes:
- `README.md` — user-facing repo overview
- `LLM_CONTEXT.md` — architecture and continuity guide for future development and LLM-assisted work
- `SLIDE_SPEC_RULES.md` — rules for writing and maintaining slide specs

When the repo structure changes, these files should be checked together so they do not drift out of sync.

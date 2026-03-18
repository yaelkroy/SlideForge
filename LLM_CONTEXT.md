# LLM_CONTEXT.md

## Project Identity

`LLM_CONTEXT.md` is the primary architecture and continuity guide for future
development and for LLM-assisted work on this repository.

**Project name:** SlideForge  
**Project type:** Python presentation generation engine  
**Primary domain:** Academic lecture slides for machine learning, mathematics,
geometry, optimization, probability, statistics, programming, and technical education  
**Primary output today:** `.pptx`  
**Planned future outputs:** `.pptx`, `.pdf`, preview images, AI-generated images,
diagrams, charts, and richer media assets

---

## One-Sentence Mission

Build a **Python-native, spec-driven, modular presentation engine** that can
generate polished academic slides while staying easy for an LLM to understand,
edit, and extend across long-running development.

---

## The Most Important Rule

This project must be designed for **small-context recovery**.

That means:

- many small modules
- stable file names
- one responsibility per file
- explicit registries
- explicit project specs
- explicit docs
- minimal hidden conventions
- minimal giant files

If something can be made more explicit for future LLM understanding, do it.

---

## Documentation Sync Rule

This project must keep its documentation synchronized with the actual codebase.

Whenever the code structure, module responsibilities, file layout, build flow,
naming conventions, or project architecture changes in a way that affects repo
understanding, the LLM should explicitly check whether the following files also
need updates:

- `README.md`
- `LLM_CONTEXT.md`

### Required LLM behavior

When making or proposing meaningful repo changes, the LLM should also:

1. determine whether the change affects user-facing or contributor-facing documentation
2. determine whether the change affects architecture or repo understanding
3. explicitly propose corresponding updates to `README.md`
4. explicitly propose corresponding updates to `LLM_CONTEXT.md`
5. mention documentation drift if code and docs no longer match

### Practical rule

Update `README.md` when the change affects:

- how to run the project
- current folder structure
- current entrypoints
- current workflow
- current module locations
- current project status

Update `LLM_CONTEXT.md` when the change affects:

- architecture
- module responsibilities
- design rules
- refactoring direction
- project conventions
- future roadmap assumptions

### Anti-drift rule

The LLM should never assume documentation is still correct after a refactor.
It should actively compare the intended architecture with the actual code organization
and call out mismatches.

### Priority rule

If there is a conflict:

- `README.md` should describe the repo as it currently exists
- `LLM_CONTEXT.md` should describe the intended architecture, governing rules,
  and long-term structure

---

## Current Repo Reality

The repository already has a working modular split, but it is still mid-refactor.

### Current practical build flow

Current build flow is:

**project slide specs -> builder registry -> slide builders -> pptx output**

At the moment:

- `src/slideforge_app.py` is the executable deck-building entrypoint
- it imports `create_presentation()` from `slideforge.app.build_deck`
- `slideforge.app.build_deck` should remain a compatibility wrapper
- `slideforge.app.presentation_factory` should remain the single source of truth
  for presentation creation
- slide content is still stored as Python dictionaries inside `projects/`
- builders are still explicit functions, one per slide family
- coordinates are still mostly hand-authored
- the system already produces useful slides and should be extended incrementally,
  not rewritten wholesale

### Current active modules

Important current modules include:

- `src/slideforge_app.py`
- `src/slideforge/config/constants.py`
- `src/slideforge/config/paths.py`
- `src/slideforge/io/backgrounds.py`
- `src/slideforge/render/primitives.py`
- `src/slideforge/assets/mini_visuals.py`
- `src/slideforge/app/build_deck.py`
- `src/slideforge/app/presentation_factory.py`
- `src/slideforge/app/slide_utils.py`
- `src/slideforge/builders/basic.py`
- `src/slideforge/builders/common.py`
- `src/slideforge/builders/builder_registry.py`
- `src/slideforge/builders/title_composite.py`
- `src/slideforge/builders/section_divider.py`
- `src/slideforge/builders/dependency_map.py`
- `src/slideforge/projects/ml_foundations/slides_part1.py`

### Current builder model

The active architecture is builder-driven.

The builder registry maps `kind` values from slide specs to builder functions.
That is the preferred extension point.

When extending the system, prefer:

- adding a new small builder file for a new slide family
- registering it in `builder_registry.py`
- adding specs in `projects/...`
- reusing rendering primitives
- avoiding logic growth in `slideforge_app.py`

Do **not** move slide-specific rendering logic back into the top-level app entrypoint.

---

## Architecture Principles

### 1. Separate concerns

Always separate:

- **what** the slide says
- **where** elements go
- **how** they are drawn
- **which** assets they use
- **which** style/theme is applied
- **which** output backend is used

### 2. Prefer explicit structure over cleverness

The repo should favor:

- explicit modules
- explicit registries
- explicit project slide lists
- explicit helper functions
- explicit naming
- explicit docs

over compact but opaque abstractions.

### 3. Prefer many small files

Target:

- most files under ~200 lines when practical
- many files in predictable directories
- one concept or subsystem per file

Avoid:

- giant utility files
- giant builder files
- giant config files
- giant schema files

### 4. Prefer registries over branching logic

Use registries for:

- slide builders
- asset generators
- visual generators
- renderers
- themes
- validators
- exporters

### 5. Prefer compatibility shims during refactors

When a module path is already used by the app, prefer a small compatibility wrapper
instead of breaking imports immediately.

This is especially appropriate for:
- renamed factory modules
- extracted helpers
- temporary migration layers

### 6. Prefer progressive hardening

The next architectural improvements should usually be:

- reduce helper duplication
- make imports more consistent
- extract reusable layout families
- normalize repeated slide-spec patterns
- add validation gradually

Do not pause useful slide generation work for a massive framework rewrite.

---

## Current Known Cleanup Priorities

These are good cleanup targets because they improve clarity without destabilizing the repo:

1. **Helper deduplication**
   - keep one canonical `create_presentation()` implementation
   - keep one canonical `new_slide()` helper location if possible

2. **Builder family growth**
   - add new small builders when a slide pattern repeats
   - avoid overloading a single builder with many unrelated layouts

3. **Project spec organization**
   - keep deck-specific slide specs inside `projects/`
   - split large slide lists if they become too long

4. **Documentation coherence**
   - README should match actual current repo behavior
   - this file should reflect actual architectural direction

---

## Extension Rules for Future LLM Sessions

When continuing work in this repo:

- first inspect current builders and project specs
- extend the builder layer rather than bypassing it
- reuse existing primitives before adding new drawing helpers
- prefer introducing a new `kind` over making one builder excessively branchy
- keep project-specific content in `projects/`
- keep generated artifacts out of source directories
- check whether `README.md` and `LLM_CONTEXT.md` need updates after any structural change

If the user asks to continue slide generation, the default assumption should be:

- keep the existing architecture
- improve it only where it meaningfully reduces duplication or friction
- avoid unnecessary churn

---

## Long-Term Target Architecture

The long-term pipeline should be:

**source content -> normalized content spec -> layout plan -> asset generation -> renderer output -> validation -> export**

### Long-term architectural layers

1. **Domain**
2. **Project Config**
3. **Content Parsing**
4. **Content Transformation**
5. **Theme System**
6. **Layout System**
7. **Asset System**
8. **Rendering System**
9. **Validation System**
10. **Orchestration**
11. **Interfaces**
12. **Documentation / Context Bundles**

Not all of these need to exist yet. They are the north star, not a demand for premature abstraction.

---

## Short Guidance for Contributors

If you are unsure what to do next, choose the smallest useful improvement that satisfies both:

- it helps generate the next slides
- it leaves the repo easier to understand than before

That is the correct default direction for SlideForge.
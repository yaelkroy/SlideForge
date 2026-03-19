
---

# `LLM_CONTEXT.md`

```md
# LLM_CONTEXT.md

## Project Identity

`LLM_CONTEXT.md` is the primary architecture and continuity guide for future development and for LLM-assisted work on this repository.

**Project name:** SlideForge  
**Project type:** Python presentation generation engine  
**Primary role:** Universal presentation engine  
**Current example domain:** Machine learning and mathematics lecture slides  
**Primary output today:** `.pptx`  
**Planned future outputs:** `.pptx`, `.pdf`, preview images, AI-generated images, diagrams, charts, and richer media assets

---

## One-Sentence Mission

Build a **Python-native, spec-driven, modular presentation engine** that can generate **any kind of presentation**, while staying easy for an LLM to understand, edit, and extend across long-running development.

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

## Universal Platform Rule

SlideForge must be treated as a **general presentation engine**, not as a machine-learning-specific product.

Machine learning is the current example deck, not the architectural boundary.

### This means

- builders should represent reusable slide patterns
- layout helpers should be domain-agnostic
- theme systems should be presentation-agnostic
- asset modules should be organized by visual family
- projects should live above the engine layer, not inside it
- naming should support reuse across many deck types

### Good engine-oriented naming

Prefer names like:

- `concept_poster`
- `pipeline`
- `dependency_map`
- `mini_visuals_geometry`
- `mini_visuals_probability`
- `mini_visuals_architecture`

Avoid shared engine names like:

- `mini_visuals_part2`
- `ml_section_bridge`
- `week3_slide_assets`

---

## Documentation Sync Rule

This project must keep documentation synchronized with the actual codebase.

Whenever the code structure, module responsibilities, file layout, build flow, naming conventions, builder inventory, theme system, header/layout behavior, slide-spec rules, project architecture, or asset-generation rules change in a way that affects repo understanding, the LLM should explicitly check whether the following files also need updates:

- `README.md`
- `LLM_CONTEXT.md`
- `SLIDE_SPEC_RULES.md`

### Required LLM behavior

When making or proposing meaningful repo changes, the LLM should also:

1. determine whether the change affects user-facing or contributor-facing documentation
2. determine whether the change affects architecture or repo understanding
3. explicitly propose corresponding updates to `README.md`
4. explicitly propose corresponding updates to `LLM_CONTEXT.md`
5. explicitly propose corresponding updates to `SLIDE_SPEC_RULES.md` when slide-spec writing or visual design rules changed
6. mention documentation drift if code and docs no longer match

### Practical rule

Update `README.md` when the change affects:

- how to run the project
- current folder structure
- current entrypoints
- current workflow
- current module locations
- current builder inventory
- current project status
- the stated platform scope

Update `LLM_CONTEXT.md` when the change affects:

- architecture
- module responsibilities
- design rules
- refactoring direction
- project conventions
- future roadmap assumptions
- engine scope

Update `SLIDE_SPEC_RULES.md` when the change affects:

- how slide spec files should be written
- visual density expectations
- readability rules
- builder selection rules
- anti-patterns in slide structure
- how metadata/guidance fields should behave

### Anti-drift rule

The LLM should never assume documentation is still correct after a refactor.  
It should actively compare intended architecture with actual code organization and call out mismatches.

---

## Current Repo Reality

The repository is working, modular, and mid-refactor.

### Current practical build flow

Current build flow is:

**project slide specs -> builder registry -> slide builders -> theme/header/layout helpers -> rendering primitives / mini visuals -> pptx output**

At the moment:

- `src/slideforge_app.py` is the executable deck-building entrypoint
- slide content is stored as Python dictionaries inside `projects/`
- builders are explicit functions, one per slide family
- the system already produces useful slides and should be extended incrementally, not rewritten wholesale
- layout is increasingly being treated as a measurable geometry problem rather than repeated manual tweaking
- visual styling is increasingly being treated as a theme/token problem rather than hardcoded builder-local colors
- generated PNG mini-visuals use a separate font policy from PowerPoint text

### Current important principle

The repo currently contains an ML example project, but the engine must remain suitable for:

- academic decks
- technical decks
- business decks
- architecture decks
- onboarding decks
- training decks
- research decks
- mixed storytelling presentations

---

## Current Active Modules

Important current modules include:

- `src/slideforge_app.py`
- `src/slideforge/config/constants.py`
- `src/slideforge/config/paths.py`
- `src/slideforge/config/themes.py`
- `src/slideforge/io/backgrounds.py`
- `src/slideforge/render/primitives.py`
- `src/slideforge/render/header.py`
- `src/slideforge/assets/mini_visuals.py`
- `src/slideforge/assets/mini_visuals_common.py`
- `src/slideforge/assets/mini_visuals_core.py`
- `src/slideforge/assets/mini_visuals_geometry.py`
- `src/slideforge/layout/base.py`
- `src/slideforge/layout/text_fit.py`
- `src/slideforge/layout/grid.py`
- `src/slideforge/layout/stack.py`
- `src/slideforge/layout/poster.py`
- `src/slideforge/layout/table.py`
- `src/slideforge/layout/cards.py`
- `src/slideforge/layout/dependency.py`
- `src/slideforge/layout/autofit.py`
- `src/slideforge/app/build_deck.py`
- `src/slideforge/app/presentation_factory.py`
- `src/slideforge/app/slide_utils.py`
- `src/slideforge/builders/basic.py`
- `src/slideforge/builders/common.py`
- `src/slideforge/builders/builder_registry.py`
- `src/slideforge/builders/title_composite.py`
- `src/slideforge/builders/section_divider.py`
- `src/slideforge/builders/dependency_map.py`
- `src/slideforge/builders/pipeline.py`
- `src/slideforge/builders/prereq_grid.py`
- `src/slideforge/builders/example_pipeline.py`
- `src/slideforge/builders/card_grid.py`
- `src/slideforge/builders/notation_panel.py`
- `src/slideforge/builders/triple_role.py`
- `src/slideforge/builders/integrated_bridge.py`
- `src/slideforge/builders/concept_poster.py`
- `src/slideforge/projects/ml_foundations/slides_part1.py`
- `src/slideforge/projects/ml_foundations/slides_part2.py`
- `src/slideforge/projects/ml_foundations/__init__.py`
- `SLIDE_SPEC_RULES.md`

---

## Builder Model

The active architecture is builder-driven.

The builder registry maps `kind` values from slide specs to builder functions.  
That is the preferred extension point.

When extending the system, prefer:

- adding a new small builder file for a new slide family
- registering it in `builder_registry.py`
- adding specs in `projects/...`
- reusing rendering primitives
- reusing mini-visual motifs
- reusing layout helpers
- reusing theme/header helpers
- avoiding logic growth in `slideforge_app.py`

Do **not** move slide-specific rendering logic back into the top-level app entrypoint.

### Current builder families

The builder registry is expected to include reusable slide-pattern builders such as:

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

### Builder rule

When a new slide pattern repeats, prefer adding a new builder rather than overloading one builder with many unrelated branches.

### Platform rule

A builder should correspond to a **reusable presentation pattern**, not to a single domain-specific slide.

---

## Theme System

A major design direction is the theme layer in:

- `src/slideforge/config/themes.py`

This layer exists because many prior builder issues came from hardcoded colors, fills, text colors, divider colors, and dark/light assumptions scattered across builders.

### Design rule

Builders should increasingly consume a theme object or theme-derived style map rather than hardcoding colors directly.

### Theme responsibilities

The theme layer should define and normalize:

- title color
- subtitle color
- body color
- muted/footer color
- divider color
- connector color
- box fill and line colors
- panel fill and line colors
- pill/callout/ghost label colors
- dark/light footer behavior
- mini-visual variant defaults such as:
  - `dark_on_light`
  - `light_on_dark`

### Preferred usage

Builders should prefer:

- `get_theme(...)`
- theme-level defaults
- spec-level style overrides

Avoid:

- builder-local raw RGB values
- hidden assumptions that all cards are light
- hidden assumptions that all text is dark navy
- repeating identical style maps across many builders

---

## Shared Header Layer

A major design direction is the shared header layer in:

- `src/slideforge/render/header.py`

This layer exists because many slide failures are header geometry failures rather than content failures.

Examples:

- title collides with divider
- divider crosses subtitle
- long title wraps into the content area
- one builder uses a safe header stack while another reintroduces overlap
- subtitle placement differs unpredictably across builders

### Design rule

Header layout should be computed once and reused, not manually reimplemented in every builder.

### Preferred usage

Builders that have a standard header should prefer:

- `render_header_from_spec(...)`

Avoid:

- manually drawing title, divider, subtitle in each builder
- fixed divider Y values unrelated to actual title height
- repeated title-box logic across many builder files

---

## Layout Layer

The layout layer has been deliberately split to keep files below the repo file-size threshold and to keep responsibilities explicit.

### `base.py`

Shared geometry primitives such as:

- `Box`
- `SlideSize`

### `text_fit.py`

Handles:

- wrapping
- line counts
- height estimation
- font-size fitting
- note-height heuristics

### `grid.py`

Handles:

- row distribution
- column distribution

### `stack.py`

Handles:

- vertical stacking of text blocks
- auto-sized stacked text regions

### `poster.py`

Handles:

- concept-poster visual/text balancing

### `table.py`

Handles:

- notation-table geometry
- row-based body/header sizing

### `cards.py`

Handles:

- centered visuals inside card-like layouts
- note box estimation

### `dependency.py`

Handles:

- dependency-map geometry
- right-column reservation
- explanation box placement
- formula/takeaway placement below the lowest occupied region

### `autofit.py`

This is a compatibility/export layer that re-exports the split layout API so builders can continue importing from one stable module path.

### Layout rule

The layout layer should stay **presentation-agnostic**.

It should solve geometry problems, not encode one course’s content assumptions.

---

## Reusable Mini-Visual Layer

A central design direction is the reusable mini-visual system.

### Why it exists

Slides fail when they rely only on text boxes and labels.

This repo explicitly supports explanatory diagrams and reusable motifs.

### Design rule

Mini visuals should be:

- reusable
- lightweight
- transparent-background assets
- style-consistent
- explanatory
- builder-agnostic when possible

### Asset organization rule

Mini-visual modules should be organized by **visual family**, not by **deck section**.

Good examples:

- `mini_visuals_geometry.py`
- `mini_visuals_probability.py`
- `mini_visuals_architecture.py`

Bad examples:

- `mini_visuals_part2.py`
- `mini_visuals_ml_section_b.py`

### Font rule for generated assets

PowerPoint text fonts and Matplotlib-generated asset fonts are separate concerns.

Prefer:

- PowerPoint text fonts for `.pptx` text
- Matplotlib-safe fonts for generated PNGs:
  - `DejaVu Sans`
  - `DejaVu Sans Mono`

Avoid relying on fragile special glyphs in generated assets unless the font is explicitly controlled.

---

## One Slide = One Dominant Idea

The preferred slide philosophy remains:

**One slide = one dominant idea + one dominant visual**

This applies across many presentation types, not only academic decks.

That means:

- concept slide -> one large explanatory visual
- comparison slide -> one strong structured comparison
- workflow slide -> one readable process picture
- business summary slide -> one dominant structural takeaway
- example slide -> one main example

---

## Slide Metadata vs Visible Content Rule

Some slide-spec fields are content.  
Some are guidance.  
They must not be treated the same.

### Usually metadata only

Examples:

- `purpose`
- `visual`
- `speaker_intent`
- `concrete_example_anchor`

These fields are usually for:

- the human author
- the LLM
- future editing continuity
- design guidance

They should **not automatically become visible slide text**.

### Visible-content rule

A guidance field should only be rendered when explicitly intended.

Preferred explicit mechanisms:

- `visible_anchor_text`
- `show_anchor_text: True`

---

## Current Project-Spec Reality

Slide content is currently stored as Python dictionaries in `projects/...`.

That is acceptable and still the active model.

### Current practical rule for project specs

Project spec files should contain:

- declarative slide content
- builder `kind`
- explicit layout overrides only where needed
- explicit theme/style overrides only where needed

### Project rule

Projects are examples or applications of the engine.  
They are **not** the engine itself.

The engine should remain reusable even when one current project dominates repo activity.

---

## File Size and Refactoring Rule

This repository should avoid oversized Python source files and oversized documentation files where practical.

### Hard guideline

- **Python files with code should stay under 500 lines whenever practical.**
- If a Python file grows large or starts mixing multiple responsibilities, it should be refactored into several smaller modules.

### Preferred split patterns

When refactoring, prefer splitting by:

- responsibility
- builder family
- asset family
- rendering primitive family
- project deck or deck part
- helper type

### Anti-monolith rule

Do not allow a Python file to become a dumping ground for:

- unrelated helpers
- multiple rendering systems
- multiple deck definitions
- several distinct builder families
- ad hoc experiments that should become their own module

---

## Architecture Principles

### 1. Separate concerns

Always separate:

- what the slide says
- where elements go
- how elements are drawn
- which assets or mini visuals they use
- which layout logic computes spacing and fit
- which style or theme is applied
- which output backend is used

### 2. Prefer explicit structure over cleverness

Favor:

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
- Python code files under 500 lines
- many files in predictable directories
- one concept or subsystem per file

### 4. Prefer registries over branching logic

Use registries for:

- slide builders
- asset generators
- mini visuals
- renderers
- themes
- validators
- exporters

### 5. Prefer compatibility shims during refactors

When a module path is already used by the app, prefer a small compatibility wrapper instead of breaking imports immediately.

### 6. Prefer progressive hardening

The next architectural improvements should usually be:

- reduce helper duplication
- make imports more consistent
- extract reusable layout families
- normalize repeated slide-spec patterns
- add validation gradually

Do not stop useful presentation generation work for a massive framework rewrite.

---

## Current Cleanup Priorities

Good cleanup targets include:

1. remove dead or weak slide families
2. reduce helper duplication
3. move style decisions into `config/themes.py`
4. centralize standard headers in `render/header.py`
5. keep mini-visuals split by reusable family
6. keep fragile spacing out of builders
7. stop rendering metadata by default
8. keep project specs project-specific
9. keep docs synchronized
10. keep Python files below 500 lines when practical

---

## Extension Rules for Future LLM Sessions

When continuing work in this repo:

- first inspect current builders and project specs
- extend the builder layer rather than bypassing it
- reuse existing primitives before adding new drawing helpers
- reuse existing mini-visual motifs before creating new ones
- reuse existing layout helpers before hardcoding new placement guesses
- reuse `render/header.py` before reimplementing a header stack
- reuse `config/themes.py` before inventing new builder-local color systems
- prefer introducing a new `kind` over making one builder excessively branchy
- keep project-specific content in `projects/`
- keep generated artifacts out of source directories
- check whether `README.md`, `LLM_CONTEXT.md`, and `SLIDE_SPEC_RULES.md` need updates after structural changes
- check whether any Python file is becoming too large and should be split

If the user asks to continue slide generation, the default assumption should be:

- keep the existing architecture
- improve it only where it meaningfully reduces duplication or fragility
- avoid unnecessary churn

---

## Long-Term Target Architecture

The long-term pipeline should be:

**source content -> normalized content spec -> layout plan -> asset generation -> renderer output -> validation -> export**

This should support many presentation domains, not one subject area.

---

## Short Guidance for Contributors

If you are unsure what to do next, choose the smallest useful improvement that satisfies both:

- it helps generate the next presentation
- it leaves the repo easier to understand than before
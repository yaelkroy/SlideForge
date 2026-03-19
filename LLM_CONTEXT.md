
---

# `LLM_CONTEXT.md`

```md
# LLM_CONTEXT.md

## Project Identity

`LLM_CONTEXT.md` is the primary architecture and continuity guide for future development and for LLM-assisted work on this repository.

**Project name:** SlideForge  
**Project type:** Python presentation generation engine  
**Primary domain:** Academic lecture slides for machine learning, mathematics, geometry, optimization, probability, statistics, programming, and technical education  
**Primary output today:** `.pptx`  
**Planned future outputs:** `.pptx`, `.pdf`, preview images, AI-generated images, diagrams, charts, and richer media assets

---

## One-Sentence Mission

Build a **Python-native, spec-driven, modular presentation engine** that can generate polished academic slides while staying easy for an LLM to understand, edit, and extend across long-running development.

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

Update `LLM_CONTEXT.md` when the change affects:

- architecture
- module responsibilities
- design rules
- refactoring direction
- project conventions
- future roadmap assumptions

Update `SLIDE_SPEC_RULES.md` when the change affects:

- how slide spec files should be written
- visual density expectations
- readability rules
- builder selection rules
- anti-patterns in lecture-slide structure
- how metadata/guidance fields should behave

### Anti-drift rule

The LLM should never assume documentation is still correct after a refactor.  
It should actively compare intended architecture with actual code organization and call out mismatches.

### Priority rule

If there is a conflict:

- `README.md` should describe the repo as it currently exists
- `LLM_CONTEXT.md` should describe the intended architecture, governing rules, and long-term structure
- `SLIDE_SPEC_RULES.md` should describe how slide spec files should be authored for the current visual system

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
- generated PNG mini-visuals now need their own font policy separate from PowerPoint fonts

### Current active modules

Important current modules include:

- `src/slideforge_app.py`
- `src/slideforge/config/constants.py`
- `src/slideforge/config/paths.py`
- `src/slideforge/config/themes.py`
- `src/slideforge/io/backgrounds.py`
- `src/slideforge/render/primitives.py`
- `src/slideforge/render/header.py`
- `src/slideforge/assets/mini_visuals.py`
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
- `src/slideforge/projects/ml_foundations/__init__.py`
- `SLIDE_SPEC_RULES.md`

---

## Current Builder Model

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

The builder registry is expected to include:

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

### Important note on `integrated_bridge`

`integrated_bridge` is now a **questioned / likely deprecated** slide family.

Use it only if it is genuinely needed by an active deck.  
If no active slide spec uses `kind: "integrated_bridge"`, the preferred cleanup is:

1. remove it from active project slide specs
2. remove it from `builder_registry.py`
3. then delete `integrated_bridge.py`

Do **not** delete the file before registry cleanup, or imports will break.

### Builder rule

When a new slide pattern repeats, prefer adding a new builder rather than overloading one builder with many unrelated branches.

---

## Theme System

A major design direction is the theme layer in:

- `src/slideforge/config/themes.py`

This layer exists because many prior builder issues came from **hardcoded colors, fills, text colors, divider colors, and dark/light assumptions** scattered across builders.

### Design rule

Builders should increasingly consume a **theme object** or theme-derived style map rather than hardcoding colors directly.

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

### Default theme behavior

A slide’s `theme` should map to a named preset, for example:

- `title` -> dark-hero behavior
- `section` -> dark-section behavior
- `concept` -> light academic behavior
- `content` -> light academic behavior

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

This layer exists because many lecture-slide failures are not content failures.  
They are header geometry failures.

Examples:

- title collides with divider
- divider crosses subtitle
- long title wraps into the content area
- one builder uses a safe header stack while another reintroduces overlap
- subtitle placement differs unpredictably across builders

### Design rule

Header layout should be **computed once and reused**, not manually reimplemented in every builder.

### What the shared header should handle

The header layer should increasingly support:

- title text fitting
- subtitle text fitting
- divider placement below actual title height
- safe `content_top_y`
- theme-aware title/subtitle/divider colors
- long-title handling for 2-line headers
- consistent spacing across builders

### Preferred usage

Builders that have a standard lecture header should prefer:

- `render_header_from_spec(...)`

Avoid:

- manually drawing title, divider, subtitle in each builder
- fixed divider Y values unrelated to actual title height
- repeated title-box logic across many builder files

---

## Layout Layer

The layout layer has been deliberately split to keep files below the repo’s file-size threshold and to keep responsibilities explicit.

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

This is now a **compatibility/export layer** that re-exports the split layout API so builders can continue importing from one stable module path.

### Layout rule

The layout layer exists because many lecture-slide failures are geometry failures:

- notes are too small even though there is enough free space
- a single diagram is stuck in the top half of a large box
- captions, formulas, and notes collide
- notation tables shrink too aggressively
- vertical whitespace is poorly distributed
- cards do not center the visual payload
- right-side sidebars overlap diagrams
- bottom ribbons drift into the footer zone

Layout should increasingly be **calculated**.

---

## Reusable Mini-Visual Layer

A central design direction is the reusable mini-visual system in:

- `src/slideforge/assets/mini_visuals.py`

This layer exists to provide technical illustrations that can be reused across multiple builders and multiple decks.

### Why it exists

Technical lecture slides fail when they rely only on text boxes and labels.

This repo explicitly supports teaching through **explanatory diagrams**, including:

- points in space
- vector arrows
- plane / separator sketches
- loss and optimization visuals
- uncertainty curves
- array / matrix glyphs
- feature-vector examples
- prediction vs truth comparisons
- object-to-representation visuals such as movie and digit examples

### Design rule

Mini visuals should be:

- reusable
- lightweight
- transparent-background assets
- style-consistent
- technically explanatory
- builder-agnostic when possible

### Font rule for generated assets

PowerPoint text fonts and Matplotlib-generated asset fonts are separate concerns.

Prefer:

- PowerPoint text fonts for `.pptx` text
- Matplotlib-safe fonts for generated PNGs:
  - `DejaVu Sans`
  - `DejaVu Sans Mono`

Avoid relying on fragile special glyphs in generated assets unless the font is explicitly controlled.

### Refactoring direction

`mini_visuals.py` is still a candidate for further split by visual family, for example:

- geometry visuals
- optimization visuals
- probability visuals
- representation visuals
- classification visuals

That split should happen before the file becomes difficult to reason about safely.

---

## Large-Visual Lecture Rule

The lecture structure should follow a stronger visual rule:

### Core rule

**One slide = one dominant idea + one dominant visual**

That means:

- concept slide -> one large explanatory diagram
- example slide -> one large worked visual example
- overview slide -> a small number of large visual elements, not many tiny ones
- examples should get dedicated slides when they need visual space

### Practical implications

For lecture planning:

- avoid dense dashboard slides early in the deck
- split overview slides from example slides
- prefer fewer cards per slide
- keep diagrams readable from the back of a classroom
- use text as support, not as the primary payload

### Additional anti-duplication rule

Avoid near-duplicate slides that restate the same conceptual idea with only minor visual differences.

If two consecutive slides teach the same bridge, prefer:

- one stronger slide
- one larger visual
- one clearer takeaway

Do not keep both just because both are decent individually.

---

## Slide Metadata vs Visible Content Rule

This is now an important repo convention.

Some slide-spec fields are **content**.  
Some are **guidance**.  
They must not be treated the same.

### By default, these should be treated as design guidance / metadata

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

### Default behavior

Unless explicitly enabled:

- `concrete_example_anchor` should be hidden
- guidance text like “Use a visible bowl surface...” should not appear on the slide
- notes for the designer/LLM should not leak into final presentation output

This rule is especially important for:

- `section_divider.py`
- `concept_poster.py`
- any future builder that might confuse deck metadata with visible slide text

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

They should avoid becoming huge mixed architecture files.

### Current status for `slides_part1.py`

For now, `slides_part1.py` may remain a single file if the user explicitly wants that.

However, the preferred long-term direction is still:

- split giant spec files when they grow too large
- separate shared layout/style constants from slide dictionaries
- keep deck content easier to scan in small context

### Practical compromise

If a user explicitly says “do not split it,” respect that.  
But still keep:

- shared constants near the top
- repeated layout fragments minimized
- no avoidable duplication
- no dead slides that are no longer conceptually needed

---

## Slide Spec Rules File

The repo uses `SLIDE_SPEC_RULES.md` as the operational rulebook for writing project slide spec files such as `slides_part1.py`.

That file is the source of truth for:

- slide density rules
- minimum readability expectations
- builder selection guidance
- anti-patterns
- splitting rules for dense slides
- spec-writing template expectations

When writing or revising slide specs, follow that file directly.

---

## File Size and Refactoring Rule

This repository should avoid oversized Python source files and oversized documentation files where practical.

### Hard guideline

- **Python files with code should stay under 500 lines whenever practical.**
- If a Python file grows large or starts mixing multiple responsibilities, it should be refactored into several smaller modules.

### Refactor triggers

Refactor a Python file when one or more of these becomes true:

- the file approaches or exceeds 500 lines
- it contains multiple unrelated responsibilities
- it contains several layout families or builder variants that can be split
- it becomes hard to navigate in a single screen or small context window
- an LLM would have difficulty understanding or modifying it safely in one pass

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

- **what** the slide says
- **where** elements go
- **how** elements are drawn
- **which** assets or mini visuals they use
- **which** layout logic computes spacing and fit
- **which** style or theme is applied
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
- Python code files under 500 lines
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
- mini visuals
- renderers
- themes
- validators
- exporters

### 5. Prefer compatibility shims during refactors

When a module path is already used by the app, prefer a small compatibility wrapper instead of breaking imports immediately.

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

Do not stop useful slide generation work for a massive framework rewrite.

---

## Current Known Cleanup Priorities

These are good cleanup targets because they improve clarity without destabilizing the repo:

1. **Remove dead or weak slide families**
   - if `integrated_bridge` is no longer used by active specs, remove it cleanly
   - avoid keeping a builder family alive only because it once existed

2. **Helper deduplication**
   - keep one canonical presentation-creation implementation
   - keep one canonical `new_slide()` helper location if possible

3. **Theme hardening**
   - move style decisions into `config/themes.py`
   - reduce hardcoded builder-local colors
   - normalize dark/light behavior

4. **Header hardening**
   - centralize standard lecture headers in `render/header.py`
   - eliminate repeated divider/subtitle collision logic
   - compute `content_top_y` rather than guessing it per builder

5. **Mini-visual hardening**
   - expand motifs only when they improve multiple slides
   - keep naming stable and explicit
   - strengthen semantics so visuals are understandable before captions
   - avoid silently drifting visual meaning
   - avoid fragile glyph dependencies in Matplotlib-generated assets

6. **Layout hardening**
   - keep fragile spacing out of builders
   - prefer the split layout modules over repeated local geometry code
   - compute note height, table font size, and vertical stacks instead of guessing
   - make visual centering the default behavior for card-like builders
   - reserve side columns explicitly for dependency-style slides

7. **Project spec organization**
   - keep deck-specific slide specs inside `projects/`
   - split large slide lists if they become too long, unless the user explicitly prefers one file

8. **Metadata visibility governance**
   - stop rendering guidance fields by default
   - require explicit visible-content fields for anything that should appear on the slide

9. **Documentation coherence**
   - `README.md` should match actual current repo behavior
   - this file should reflect actual architectural direction
   - `SLIDE_SPEC_RULES.md` should reflect current slide-authoring expectations

10. **File-size governance**
   - keep Python source files below 500 lines when practical
   - refactor large modules before they become hard to reason about

---

## Extension Rules for Future LLM Sessions

When continuing work in this repo:

- first inspect current builders and project specs
- extend the builder layer rather than bypassing it
- reuse existing primitives before adding new drawing helpers
- reuse existing mini-visual motifs before creating new ones
- reuse existing layout helpers before hardcoding new placement guesses
- reuse `render/header.py` before reimplementing a title/divider/subtitle stack
- reuse `config/themes.py` before inventing new builder-local color systems
- prefer introducing a new `kind` over making one builder excessively branchy
- keep project-specific content in `projects/`
- keep generated artifacts out of source directories
- check whether `README.md`, `LLM_CONTEXT.md`, and `SLIDE_SPEC_RULES.md` need updates after any structural change
- check whether any Python file is becoming too large and should be split

If the user asks to continue slide generation, the default assumption should be:

- keep the existing architecture
- improve it only where it meaningfully reduces duplication or fragility
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
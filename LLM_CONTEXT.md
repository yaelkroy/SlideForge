# LLM_CONTEXT.md

## Project Identity

`LLM_CONTEXT.md` is the primary architecture and continuity guide for future development and LLM-assisted work on this repository.

- **Project name:** SlideForge
- **Project type:** Python presentation generation engine
- **Primary role:** general-purpose, spec-driven slide and presentation engine
- **Current example project:** Machine Learning Foundations lecture deck
- **Primary output today:** `.pptx`
- **Longer-term direction:** richer outputs may later include PDFs, previews, images, diagrams, charts, and other media-oriented assets, but the repo should always be documented first in terms of the code that actually exists now.

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
- builders should represent reusable slide patterns
- layout helpers should be domain-agnostic
- theme systems should remain presentation-agnostic
- render helpers should stay reusable across many deck types
- asset modules should be organized by visual family, not one lecture only
- projects should live above the engine layer, not inside the engine core
- naming should support reuse across many kinds of presentations

Prefer names like:
- `concept_poster`
- `pipeline`
- `dependency_map`
- `notation_panel`
- `card_grid`
- `title_composite`
- `render/header.py`
- `layout/poster.py`
- `layout/table.py`

Avoid names like:
- `ml_only_layout`
- `week2_cards`
- `part2_assets`
- `lecture_specific_renderer`
- `temporary_final_builder`

---

## Current Repo Reality

Describe the repo according to the code that exists now, not according to proposed refactors that have not yet been pushed.

The current codebase is a real modular repo under `src/slideforge/`, including:
- `app/`
- `assets/`
- `builders/`
- `config/`
- `io/`
- `layout/`
- `projects/`
- `render/`
- `utils/`

This is not a one-file prototype anymore. It is a working modular codebase that is still evolving and still needs disciplined cleanup.

---

## Current Practical Repository Structure

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
      ├─ __init__.py
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

When documenting the repo, prefer this real package-oriented structure over imagined future trees.

---

## Current Entrypoint and Build Flow

Current top-level run command:

```bash
python src/slideforge_app.py
```

### Intended build flow

The intended build flow is:

**project slide specs -> builder registry -> slide builders -> theme/header/layout helpers -> rendering primitives / mini visuals -> pptx output**

### Current committed entrypoint behavior

`src/slideforge_app.py` currently:
1. ensures runtime directories exist
2. validates backgrounds against the selected slides
3. creates a presentation object
4. loops through the slide specs
5. dispatches on `spec["kind"]` through the builder registry
6. saves the output deck

### Important current inconsistency

The current entrypoint imports:

```python
from slideforge.projects.ml_foundations import ML_FOUNDATIONS_SLIDES
```

But the current `src/slideforge/projects/ml_foundations/__init__.py` exports only:
- `ML_FOUNDATIONS_PART1_SLIDES`

That mismatch should be treated as a **current repo inconsistency**. Do not document the app as fully clean and consistent unless that import/export mismatch has been fixed.

### Compatibility-shim rule

A useful compatibility detail exists here:
- `slideforge.app.build_deck` is a thin compatibility wrapper
- `slideforge.app.presentation_factory` is the single source of truth for presentation creation

That wrapper pattern is intentional and should not be “cleaned up” in a way that breaks stable imports without a deliberate migration plan.

---

## Current Package Responsibilities

### `src/slideforge/app/`

Application-level orchestration.

Use this layer for:
- deck-building orchestration
- presentation factory setup
- top-level slide processing utilities
- compatibility shims that preserve stable import paths during refactors

Do not bury reusable rendering logic here.

Current files:
- `build_deck.py`
- `presentation_factory.py`
- `slide_utils.py`

### `src/slideforge/assets/`

Reusable visual assets and generated mini-illustration helpers.

Current reality:
- `mini_visuals.py` remains the public entrypoint for the mini-visual system
- support has been split into:
  - `mini_visuals_common.py`
  - `mini_visuals_core.py`
  - `mini_visuals_geometry.py`

Asset modules should stay focused on reusable visuals and visual families, not builder orchestration.

### `src/slideforge/builders/`

Slide-pattern builder layer.

This is where each stable slide pattern gets its own builder module.

Current builder files include:
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
- `integrated_bridge.py.bak`

### Current active builder kinds

The current builder registry wires these active kinds:
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

### Important current nuance

`integrated_bridge` is **not currently an active registered builder kind**.

The repository tree contains `integrated_bridge.py.bak`, and `builder_registry.py` shows the `integrated_bridge` import and registry entry commented out. Treat that as an inactive or parked builder, not an active module.

### Builder-layer intent

A builder should represent a **reusable visual pattern**, not merely one lecture topic.

### `src/slideforge/config/`

Configuration and presentation-wide semantics.

Current reality:
- `constants.py` holds core constants
- `paths.py` handles path/output/runtime path concerns
- `themes.py` is a real architectural layer, not just a future idea

### `src/slideforge/io/`

I/O-adjacent helpers.

Current reality:
- `backgrounds.py` handles background selection and validation behavior

### `src/slideforge/layout/`

This is a **first-class package** and must be treated as such in documentation and future edits.

Use this package for geometry, sizing, text fitting, region calculation, vertical stacking, table layout, and similar mathematically grounded placement logic.

Current reality includes:
- `autofit.py`
- `base.py`
- `cards.py`
- `dependency.py`
- `grid.py`
- `poster.py`
- `stack.py`
- `table.py`
- `text_fit.py`

`layout/__init__.py` acts as a compatibility/export surface by re-exporting commonly used layout helpers.

Do not re-scatter reusable layout logic back into individual builders unless there is a very strong reason.

### `src/slideforge/projects/`

Project-level slide specs.

Projects define **content** and project-specific defaults. They should not become dumping grounds for reusable rendering logic.

### `src/slideforge/projects/ml_foundations/`

Current example project.

Current reality:
- `slides_part1.py` exists
- `slides_part2.py` exists
- `__init__.py` currently exports only `ML_FOUNDATIONS_PART1_SLIDES`

Do not document combined exports or active Part II wiring unless that has actually been pushed.

### `src/slideforge/render/`

Low-level reusable PowerPoint rendering helpers.

Current reality:
- `primitives.py` handles core shape/text rendering primitives
- `header.py` is a reusable header system

Do not document `render/math_blocks.py` or other proposed renderer additions unless they exist in the repo.

### `src/slideforge/utils/`

Smaller reusable helpers that do not clearly belong in layout, render, or config.

Current reality includes:
- `units.py`
- `text_layout.py`

---

## Theme System Reality

The theme system is real and should be treated as a stable part of repo understanding.

Current reality in `config/themes.py`:
- `SlideTheme` exists as a dataclass
- theme lookup and override logic exists
- builders should prefer routing slide styling through the theme system instead of duplicating ad hoc color constants

### Theme rule

Future LLM edits should prefer routing color and styling behavior through the theme system instead of duplicating builder-local color and divider logic.

---

## Header System Reality

The header system is also real and reusable.

Current reality in `render/header.py`:
- header layout is computed through reusable logic
- title/subtitle fitting is handled through explicit structures
- builders can render headers from spec instead of manually reimplementing title/subtitle placement

### Header rule

When a builder uses a conventional title/subtitle/divider flow, prefer the reusable header functions rather than copying a custom title block unless the slide pattern genuinely requires a different composition.

---

## Layout and Autofit Rule

A major part of the current architecture is moving placement from guesswork to explicit layout helpers.

That means future changes should favor:
- layout boxes
- content regions
- text-fitting helpers
- calculated stacking and distribution
- card/poster/table layout utilities

Avoid regressing toward:
- arbitrary hand-tuned coordinates repeated in many files
- duplicated text-fit logic in each builder
- repeated magic numbers with no semantic grouping

Hardcoded coordinates are still allowed where necessary, but they should be minimized or grouped into meaningful layout dictionaries.

---

## Reusable Mini-Visual Layer

A central design direction is the reusable mini-visual system.

### Why it exists

Slides become weak when they rely only on text boxes. The repo explicitly supports lightweight explanatory diagrams and reusable motifs.

### Design rule

Mini visuals should be:
- reusable
- lightweight
- style-consistent
- builder-agnostic when possible
- organized by visual family rather than deck section

### Asset organization rule

Good examples:
- `mini_visuals_core.py`
- `mini_visuals_geometry.py`

Bad examples:
- `mini_visuals_part2.py`
- `ml_section_bridge_assets.py`

### Current honest note

The current repo still uses some formula-bearing symbolic mini visuals such as `orthogonal_vectors_symbolic` and `projection_symbolic_homework`. Proposed geometry-only refactors have **not** fully landed in `main` yet, so docs should describe the current state honestly while still encouraging the cleaner long-term split.

### Font rule for generated assets

PowerPoint text fonts and generated asset fonts are separate concerns.

Prefer:
- PowerPoint text fonts for `.pptx` text
- explicitly controlled, renderer-safe fonts for generated image assets

Avoid relying on fragile special glyphs in generated assets unless the font is explicitly controlled.

---

## One Slide = One Dominant Idea

The preferred slide philosophy remains:

**One slide = one dominant idea + one dominant visual**

This applies broadly, not only to academic decks.

That means:
- concept slide -> one large explanatory visual
- comparison slide -> one strong structured comparison
- workflow slide -> one readable process picture
- summary slide -> one dominant structural takeaway
- example slide -> one main example

---

## Slide Metadata vs Visible Content Rule

Some slide-spec fields are content. Some are guidance. They must not be treated the same.

### Usually metadata only

Examples:
- `purpose`
- `visual`
- `speaker_intent`
- `concrete_example_anchor`

These are usually for:
- the human author
- the LLM
- future editing continuity
- design guidance

They should **not automatically become visible slide text**.

### Visible-content rule

A guidance field should only be rendered when explicitly intended.

Prefer explicit mechanisms such as:
- `visible_anchor_text`
- `show_anchor_text: True`

---

## Slide Spec Reality

Slide specs are still Python dictionaries today. That is acceptable.

The important rule is that slide specs should remain:
- readable
- explicit
- visually intentioned
- builder-compatible
- easy for an LLM to edit safely

### Current spec expectation

A slide spec usually defines:
- `kind`
- title/subtitle fields
- theme/background fields
- layout overrides when needed
- content fields expected by the chosen builder

The builder should consume a spec in a way that is predictable and discoverable from code.

---

## Builder Registry Rule

The builder registry is a core recovery mechanism.

### Required behavior

- every stable active slide kind should be wired through `builder_registry.py`
- builders should be imported explicitly
- the registry should remain readable in one glance
- avoid large hidden dispatch systems or dynamic import magic unless there is a compelling reason

### Important nuance

Do not create a new builder kind for every one-off slide.

Create a new builder only when:
- the visual pattern is recurring
- the required content structure is stable
- multiple slides benefit from the same layout/render logic

Otherwise, prefer expressing variation through spec data and layout overrides inside an existing builder family.

---

## File Size and Refactoring Rule

This repository should avoid oversized Python source files and oversized documentation files where practical.

### Hard guideline

- **Python files with code should stay under 500 lines whenever practical.**
- **Most logic/helper/builder/layout files should preferably stay around 200 lines or less when practical.**
- If a Python file grows large or starts mixing multiple responsibilities, it should be refactored into several smaller modules.

### Scope of this rule

This size rule applies primarily to logic files such as:
- builders
- layout helpers
- render helpers
- config helpers
- registry files
- utility modules
- asset-generation logic

It does **not** mean every presentation-content file must be tiny.

Project slide-spec files and other declarative presentation-content files may be longer when:
- they are primarily content rather than reusable engine logic
- splitting them would make the deck harder to read or maintain
- a deck part naturally belongs in one file

Even then, long content files should still be split when doing so improves clarity, such as splitting a deck into `slides_part1.py` and `slides_part2.py`.

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

## Documentation Sync Rule

This project must keep documentation synchronized with the actual codebase.

Whenever the code structure, module responsibilities, file layout, build flow, naming conventions, builder inventory, theme system, header/layout behavior, slide-spec rules, or project architecture change in a way that affects repo understanding, the LLM should explicitly check whether these files also need updates:
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

### Anti-drift rule

The LLM should never assume documentation is still correct after a refactor.
It should actively compare intended architecture with actual code organization and call out mismatches.

---

## Current Known Mismatches and Cautions

As of the current pushed repo state:
- `src/slideforge_app.py` imports `ML_FOUNDATIONS_SLIDES`
- `src/slideforge/projects/ml_foundations/__init__.py` exports only `ML_FOUNDATIONS_PART1_SLIDES`
- `slides_part2.py` exists, but Part II is not currently exported through the package init
- `builder_registry.py` does not currently register a dedicated worked-example builder
- `integrated_bridge` remains commented out and parked
- proposed modules such as `worked_example_panel.py`, `layout/worked_example.py`, `render/math_blocks.py`, and `debug/slide_qc.py` are not part of the live repo tree yet

This means documentation should be **honest about current limitations**, not silently rewritten to match planned architecture.

---

## Current Cleanup Priorities

Good cleanup targets include:
1. reconcile the `ML_FOUNDATIONS_SLIDES` import/export mismatch
2. decide whether Part II should be exported and built by default
3. reduce helper duplication
4. move more style decisions into `config/themes.py`
5. centralize standard headers in `render/header.py`
6. keep mini-visuals split by reusable family
7. keep fragile spacing out of builders
8. stop rendering metadata by default
9. keep project specs project-specific
10. keep docs synchronized
11. keep Python logic files below 500 lines when practical
12. prefer most logic files around 200 lines when practical

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
- prefer introducing a new `kind` only when the pattern is truly recurring
- keep project-specific content in `projects/`
- keep generated artifacts out of source directories
- check whether `README.md`, `LLM_CONTEXT.md`, and `SLIDE_SPEC_RULES.md` need updates after structural changes
- check whether any Python file is becoming too large and should be split

If the user asks to continue slide generation, the default assumption should be:
- keep the existing architecture
- improve it only where it meaningfully reduces duplication or fragility
- avoid unnecessary churn
- document known inconsistencies explicitly

---

## Long-Term Target Architecture

The long-term pipeline should be:

**source content -> normalized content spec -> layout plan -> asset generation -> renderer output -> validation -> export**

This should support many presentation domains, not one subject area.

This is a target, not a claim that every piece already exists in `main`.

---

## Short Guidance for Contributors

If you are unsure what to do next, choose the smallest useful improvement that satisfies both:
- it helps generate the next presentation
- it leaves the repo easier to understand than before

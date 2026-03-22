# SLIDE_SPEC_RULES.md

## Purpose

This file defines the slide-spec writing rules for SlideForge decks.

It exists to keep generated slide specs readable, visually strong, and consistent across builders, projects, and future LLM-assisted edits.

This file is specifically about **how to describe and structure slides** such as `slides_part1.py`, not about low-level renderer implementation.

Although many current examples are lecture-oriented, the rules below should also support the broader goal of a **universal presentation engine**.

---

## Core Principle

**One slide = one dominant idea + one dominant visual**

This is the most important design rule for readable slides in this repository.

The audience should be able to understand the main point of a slide by looking at it for a few seconds from a realistic presentation distance.

That means:
- concept slides should have one large explanatory visual
- analytic/example slides should have one large worked visual example or one dominant derivation region
- overview slides should contain only a small number of clearly readable visual elements
- text should support the visual, not compete with it

---

## Spec Philosophy

The **project spec** should decide slide meaning.

The engine should not need to guess whether a slide is:
- a dense analytic slide
- a compact concept slide
- a visual-first summary
- a text-first synthesis slide

Prefer explicit spec/profile choices such as:
- `layout_profile="visual_dominant"`
- `layout_profile="text_dominant"`
- `poster_profile="compact_concept"`
- `poster_profile="analytic_steps"`

Use compatibility aliases only when maintaining older decks.

---

## Visual Density Rules

### Concept slides

A concept slide should usually contain:
- one dominant visual
- one short explanation sentence
- zero to three short bullet fragments
- one or two formulas at most unless the formula itself is the concept

Avoid turning a concept slide into a dashboard of mini-cards.

### Analytic / worked-example slides

An analytic slide should usually contain:
- one dominant diagram or one dominant calculation region
- clearly ordered steps
- only the formulas needed for the worked example or derivation
- no unrelated side content

### Overview slides

An overview slide may contain several visual elements, but they must remain large enough to be readable.

Rules:
- prefer 3 to 5 medium or large visual elements
- avoid many tiny cards
- avoid dense text inside each element

### Notation slides

Notation slides should stay sparse.

Rules:
- no more than 4 notation rows per slide when readability matters
- split notation across multiple slides if needed
- examples should be visibly large and concrete

### Anchor / comparison slides

Anchor-example or comparison slides should avoid overcrowding.

Rules:
- prefer 3 cards per slide
- 6 cards is the upper limit only when cards are truly simple
- if cards need formulas and diagrams, split into multiple slides

---

## Minimum Readability Rules

These are practical defaults.

### Font sizes

Use these as practical minimums for slide content:
- title: 26–30 pt
- subtitle: 16–18 pt
- main explanatory sentence: 15–18 pt
- concept captions: 14–16 pt
- formula strips: 13–15 pt
- anchor or note text: 12–14 pt

Avoid body text below 12 pt on presentation slides.

### Visual scale

A dominant visual should generally occupy:
- about 65–75% of the usable slide area on a single-concept poster slide
- about 55–70% of the usable slide area on an analytic or worked-example slide
- most of the vertical center of the slide, not just the top portion

Do not place a single diagram only in the upper half of a mostly empty panel.

---

## Visual Semantics Rules

A visual should be understandable before the audience reads small captions.

That means:
- shapes must be visually distinct
- arrows must clearly indicate process or direction
- separators and boundaries must look like separators and boundaries
- uncertainty visuals must look probabilistic, not decorative
- matrices, vectors, arrays, and diagrams must look computational or explanatory, not ornamental

### Good examples
- a classifier boundary visibly splitting two point clouds
- a loss curve with a clearly marked current point and downhill direction
- a pipeline that clearly shows object -> vector -> decision
- a projection picture with a visible perpendicular drop
- a real-world object explicitly turning into a feature vector

### Bad examples
- abstract line art that requires a caption to understand
- tiny technical icons inside overly dense cards
- decorative mini visuals that do not teach the concept directly
- point and vector diagrams that look identical when the slide is supposed to explain the distinction

---

## Layout Calculation Rules

SlideForge should increasingly rely on measurable layout rather than manual guesswork.

The slide size is known.  
The usable box size is known.  
Text can be estimated.  
So spacing, fitting, and coverage should be calculated.

### Layout should be computed when possible

Prefer calculated placement for:
- dominant visual height
- vertical text stacks
- note height
- whether a note should be 1 line or 2 lines
- notation row height
- table font size
- card visual centering
- safe spacing between subtitle, diagrams, formulas, and notes
- side-column reservation for dependency or hub-and-spoke slides
- safe bottom placement for formula ribbons and takeaway text

### Builders should avoid hardcoded guess stacks

Avoid patterns like:
- fixed tiny note heights for all slides
- manually stacking 4–5 text bands under one image
- assuming all captions fit in one line
- assuming formulas always fit into the same narrow ribbon
- placing a right-side explanation box without reserving horizontal space for it
- placing formula and takeaway bands at fixed Y positions regardless of actual content height

### Harmony rule

The slide should feel balanced in both directions:
- horizontally
- vertically

Do not optimize only left-to-right structure while ignoring top-to-bottom harmony.

A good slide uses the whole page intentionally.

---

## Composition Family Rules

Use the correct **composition family** for the visual job.

### `title_composite`

Use for:
- title slides
- hero opener slides
- high-level conceptual banners

Do not use for:
- detailed examples
- dense comparison slides
- notation tables

### `section_divider`

Use for:
- section opener slides
- divider slides
- mood-setting academic or structural transitions

Do not overload it with content.

### `dependency_map`

Use for:
- prerequisite maps
- concept dependency diagrams
- hub-and-spoke explanation slides

Rules:
- the diagram must have its own reserved region
- the explanation box must not overlap the diagram
- right-side explanatory columns should be treated as a real layout region, not as an afterthought
- formula and takeaway text should sit below the lowest occupied content area

Avoid adding dense bullet columns unless absolutely necessary.

### `concept_poster`

Use for:
- one concept with one large diagram
- visually dominant explanatory slides
- foundational concept slides where the visual must fill most of the slide

This is the preferred builder for slides like:
- Geometry Gives Us Representation
- Optimization Improves Parameters
- Probability Models Uncertainty
- Computation Makes the Math Executable

### `pipeline`

Use for:
- conceptual story pipelines
- deck-level flow slides
- compact but still readable stage progressions

Do not use when the slide requires a highly detailed example with many stage-specific explanations.

### `annotated_pipeline`

Use for:
- worked example storyboards
- representation pipelines for a specific example
- object-to-vector-to-prediction examples
- stage flows where each stage needs a stronger example or annotation layer

Preferred stage count:
- 3 stages is ideal for strong readability
- 4 stages is acceptable if each stage remains visually large
- avoid 5 narrow equal stages when the slide is meant to teach visually

Compatibility alias:
- `example_pipeline` may remain supported for legacy specs, but `annotated_pipeline` is the preferred name for new specs.

### `card_grid`

Use for:
- anchor-example slides
- example summaries
- simple concept collections

Avoid dense cards with too many text layers.

### `notation_panel`

Use for:
- notation slides
- symbol-to-meaning reference tables

Keep row count low enough for presentation readability.

### `analytic_panel`

Use for:
- step-by-step worked examples
- analytic derivations
- visual + reasoning slides
- slides with a dominant diagram and a structured steps/result/takeaway stack

Compatibility aliases:
- `worked_example_panel`
- `worked_example`

Use the composition-semantic name `analytic_panel` in all new specs.

### `multi_panel_summary`

Use for:
- parallel conceptual comparisons
- “same object, different roles” slides
- synthesis slides that compare several panels and end with a summary band

Compatibility alias:
- `triple_role`

Use the composition-semantic name `multi_panel_summary` in all new specs.

---

## Domain Packs vs Engine Core

When a slide uses domain-specific visuals, that is fine.

But specs should think in terms of:
- **composition family** for layout and content structure
- **visual pack** for domain graphics

For example:
- geometry visuals can come from `assets/packs/geometry/...`
- future business, systems, biology, or data visuals can come from their own packs

The engine should stay composition-driven, not domain-locked.

---

## Anti-Patterns

Do not generate slides with these patterns unless explicitly asked.

### Anti-pattern 1: tiny diagram in giant box
A single concept slide should not have:
- a very small diagram inside a large empty card
- formulas drifting in an orphan strip far away from the visual
- a large amount of dead whitespace without compositional purpose

### Anti-pattern 2: too many stacked micro-regions
Avoid slides that turn into:
- title
- explanation strip
- bullet strip
- formula strip
- note strip
- takeaway strip
- tiny diagram somewhere on top

This usually means the composition family is wrong.

### Anti-pattern 3: engine-semantic naming in new specs
For new specs, avoid preferring old lecture-flavored names when a universal composition name exists.

Prefer:
- `analytic_panel`
- `annotated_pipeline`
- `multi_panel_summary`

Use old names only when maintaining compatibility with existing decks.

---

## Project-Spec Responsibility

Project slide files such as:
- `slides_part1.py`
- `slides_part2.py`

are allowed to be declarative and presentation-specific.

That is where project-specific content belongs.

What should **not** live in project specs:
- reusable rendering primitives
- engine-wide style systems
- generic layout solvers
- registry wiring
- global asset contracts

Project specs should choose from the engine’s reusable parts rather than recreating them.

---

## Final Rule

When a slide looks wrong, first ask:

1. Is the **composition family** wrong?
2. Is the **profile** wrong?
3. Is the **visual pack** wrong?
4. Is the slide trying to express too many ideas at once?

Do not default immediately to patching random spacings or hardcoding one more special case.

A universal presentation engine stays healthy when slide meaning is expressed clearly in the spec and reusable composition families stay generic.

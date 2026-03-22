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
- a hero divider slide

Prefer explicit spec/profile choices such as:
- `layout_profile="visual_dominant"`
- `layout_profile="text_dominant"`
- `poster_profile="compact_concept"`
- `poster_profile="analytic_steps"`
- `worked_layout_mode="two_column"`
- `worked_layout_mode="top_visual"`

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
So spacing, fitting, coverage, and candidate layout choice should be calculated.

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
- orientation choice between `top_visual` and `two_column`
- split recommendation when a slide is too dense to remain readable

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

## Candidate Layout and Split Rules

When a slide can be laid out in more than one sensible way, the engine should prefer **candidate-layout evaluation** rather than forcing one layout family blindly.

Good candidate families include:
- `top_visual`
- `two_column`
- `two_column_visual_heavy`
- `two_column_text_heavy`
- compact concept poster with centered formula band
- split-required fallback

A spec author should still make good choices up front, but the engine may reject or switch layouts when:
- the visual becomes too compressed
- label-dense diagrams become unreadable
- the last line of text risks escaping the box
- the slide becomes both crowded and visually weak

### Split rule

If a concept or analytic slide requires too many steps, formulas, callouts, and notes to stay readable, split it.

Typical split pattern:
1. concept or geometry slide
2. worked derivation or calculation slide

Do not keep a slide overloaded just to preserve slide count.
A strong two-slide explanation is better than one crowded slide.

---

## Visual Metadata Rule

When a visual materially affects layout choice, its asset metadata should guide the solver.

Useful metadata includes:
- preferred layout orientation
- minimum readable width
- minimum readable height
- preferred aspect ratio
- label density
- whether the visual is text-bearing
- whether top-strip placement is allowed
- whether hero simplification is required

Spec authors should still choose the right builder and profile, but the layout engine can use metadata to reject obviously bad placements.

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
Divider heroes should remain bold and simple.

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

Compact concept slides should keep formulas visually integrated with the main composition. Do not let formulas drift into detached low-left ribbons.

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
- avoid 5 narrow equal stages unless they are extremely sparse

### `analytic_panel`

Use for:
- worked derivations
- step-by-step numeric or symbolic examples
- concept-plus-derivation slides where the derivation is central

Rules:
- geometry must remain large enough to read
- if the visual is label-dense, prefer `two_column`
- if the visual becomes too thin in `top_visual`, switch orientation or split
- result and takeaway should be visually protected
- last-line safety matters; do not fit text to the exact lower boundary

### `multi_panel_summary`

Use for:
- reusable multi-panel comparison or synthesis slides
- three-role or three-lens summaries
- bridge slides connecting several distinct but related ideas

Rules:
- panels should be visually large enough to scan quickly
- the summary band must add synthesis, not duplicate the panels
- if panels become too text-heavy, split into multiple slides

### `notation_panel`

Use for:
- notation review slides
- symbol/meaning/example panels
- compact mathematical vocabulary slides

If the notation content becomes table-like or row-heavy, prefer splitting or introducing a dedicated notation-table family rather than overloading a generic panel.

---

## Builder-Selection Rules for Current Decks

For new SlideForge work, prefer the canonical builder names:
- `analytic_panel`
- `annotated_pipeline`
- `multi_panel_summary`

Legacy names are acceptable only for compatibility maintenance:
- `worked_example_panel`
- `example_pipeline`
- `triple_role`

Do not introduce new deck content using the old names when the universal family name is already available.

---

## Slide Count Philosophy

Do not increase slide count carelessly.
But do not preserve slide count at the cost of readability.

A slide should not feel empty, but it also should not be overloaded.

Good balance:
- use the full page intentionally
- keep the dominant visual large
- keep the derivation legible
- split only when one slide cannot carry the material cleanly

“Not too empty” does **not** mean “fill every corner.”
It means the occupied regions feel deliberate and proportionate.

---

## Final Rule

Specs should be written so that both a human and an LLM can tell:
- what the dominant idea is
- what the dominant visual is
- what composition family is intended
- whether the slide is concept, analytic, overview, divider, or synthesis
- whether the slide should stay as one slide or would be better split

A good spec reduces downstream guesswork.
A great spec makes the final slide both readable and inevitable.

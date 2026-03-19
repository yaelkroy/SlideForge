# SLIDE_SPEC_RULES.md

## Purpose

This file defines the slide-spec writing rules for SlideForge lecture decks.

It exists to keep generated slide specs readable, visually strong, and consistent across builders, projects, and future LLM-assisted edits.

This file is specifically about **how to describe and structure slides** such as `slides_part1.py`, not about low-level renderer implementation.

---

## Core Principle

**One slide = one dominant idea + one dominant visual**

This is the most important design rule for lecture slides in this repository.

The audience should be able to understand the main point of a slide by looking at it for a few seconds from a classroom distance.

That means:

- concept slides should have one large explanatory visual
- example slides should have one large worked visual example
- overview slides should contain only a small number of clearly readable visual elements
- text should support the visual, not compete with it

---

## Lecture Visual Density Rules

### Concept slides

A concept slide should usually contain:

- one dominant visual
- one short explanation sentence
- zero to three short bullet fragments
- one or two formulas at most unless the formula itself is the concept

Avoid turning a concept slide into a dashboard of mini-cards.

### Worked example slides

A worked example slide should usually contain:

- one dominant example visual or one dominant calculation panel
- clearly ordered steps
- only the formulas needed for the worked example
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

### Anchor example slides

Anchor-example slides should avoid overcrowding.

Rules:

- prefer 3 cards per slide
- 6 cards is the upper limit only when cards are truly simple
- if the cards need formulas and diagrams, split into multiple slides

---

## Minimum Readability Rules

These are lecture-oriented defaults.

### Font sizes

Use these as practical minimums for slide content:

- title: 26–30 pt
- subtitle: 16–18 pt
- main explanatory sentence: 15–18 pt
- concept captions: 14–16 pt
- formula strips: 13–15 pt
- anchor or note text: 12–14 pt

Avoid body text below 12 pt on lecture slides.

### Visual scale

A dominant visual should generally occupy:

- about 65–75% of the usable slide area on a single-concept poster slide
- about 55–70% of the usable slide area on a worked example slide
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
- matrices, vectors, and arrays must look computational, not ornamental

### Good examples

- a classifier boundary visibly splitting two point clouds
- a loss curve with a clearly marked current point and downhill direction
- a pipeline that clearly shows object → vector → decision
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

### Builders should avoid hardcoded guess stacks

Avoid patterns like:

- fixed tiny note heights for all slides
- manually stacking 4–5 text bands under one image
- assuming all captions fit in one line
- assuming formulas always fit into the same narrow ribbon

### Harmony rule

The slide should feel balanced in both directions:

- horizontally
- vertically

Do not optimize only left-to-right structure while ignoring top-to-bottom harmony.

A good slide uses the whole page intentionally.

---

## Slide Family Rules

Use the correct builder family for the visual job.

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
- mood-setting academic transitions

Do not overload it with content.

### `dependency_map`

Use for:

- prerequisite maps
- concept dependency diagrams
- hub-and-spoke explanation slides

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

### `example_pipeline`

Use for:

- worked example storyboards
- representation pipelines for a specific example
- object-to-vector-to-prediction examples

Preferred stage count:

- 3 stages is ideal for strong lecture readability
- 4 stages is acceptable if each stage remains visually large
- avoid 5 narrow equal stages when the slide is meant to teach visually

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

Keep row count low enough for classroom readability.

### `triple_role`

Use for:

- parallel three-way conceptual comparisons
- slides where the same object plays three roles

### `integrated_bridge`

Use for:

- one-object-multiple-interpretations slides
- bridge slides where role changes must be shown with large annotations

---

## Anti-Patterns

Do not generate slides with these patterns unless the user explicitly asks for them.

### Anti-pattern 1: tiny diagram in giant box

A single concept slide should not have:

- one small diagram at the top
- four tiny text bands under it
- lots of empty lower space

### Anti-pattern 2: equal narrow cards for a visual story

Do not use:

- five narrow equal cards for a slide meant to feel like a large worked example
- six dense cards when three would be readable

### Anti-pattern 3: notation overload

Do not place:

- too many notation rows on one slide
- dense symbolic content without concrete examples

### Anti-pattern 4: caption-dependent visuals

Do not rely on captions to rescue unclear visuals.

The diagram itself must communicate the main concept.

### Anti-pattern 5: too many explanatory layers on one slide

Avoid stacking all of the following on one concept slide:

- long explanatory paragraph
- bullet list
- formula strip
- tiny anchor line
- takeaway box
- multiple unrelated mini visuals

Split the slide instead.

### Anti-pattern 6: top-biased card visuals

Do not let the main drawing sit only in the top half of a tall card when there is large unused white space below.

The visual should be vertically centered relative to the full card structure.

### Anti-pattern 7: fake distinction visuals

Do not use nearly identical visuals for concepts that are supposed to be contrasted, such as:

- point vs vector
- object vs encoded representation
- separator vs classifier output

If the audience cannot see the difference immediately, the slide failed.

---

## When to Split a Slide

Split a slide when one or more of these becomes true:

- the dominant visual becomes too small
- the slide contains more than one major teaching idea
- the audience would need to zoom in to read formulas
- the diagram requires several captions to be understood
- the slide uses many cards, boxes, or table rows
- the renderer is forced to shrink the visual to fit text

### Typical split cases

- one overview slide becomes concept slide + example slide
- one example slide becomes object-to-vector slide + vector-to-prediction slide
- one notation slide becomes two notation slides
- one 6-card grid becomes two 3-card grids

---

## Formula Placement Rules

Formulas should support the visual hierarchy.

### On concept slides

Use only a small number of formulas:

- 1 to 2 primary formulas
- optionally a short formula ribbon

Keep formulas secondary unless the formula is the concept itself.

### On worked example slides

Formulas may be more prominent, but they should be:

- stacked cleanly
- stepwise
- aligned with the visual explanation

### On title or divider slides

Formulas should be minimal or absent.

### Formula readability rule

Do not shrink formulas to rescue an overcrowded layout.  
If the formula area becomes too tight, reduce content or split the slide.

---

## Text Placement Rules

Text must not crowd the dominant visual.

### Preferred text hierarchy

1. slide title
2. visual
3. short explanation
4. short bullet fragments
5. formula strip
6. anchor or takeaway note

### Preferred text behavior

- one short explanatory sentence is usually better than a paragraph
- bullet fragments are better than long bullets
- speaker-intent content belongs in notes or source spec, not on the slide

### Note rule

Notes should be sized by fit, not by habit.

A note may be:

- one line
- two lines

The builder should calculate which is appropriate instead of forcing a tiny one-line box.

---

## Table and Notation Rules

Notation panels should be designed from row geometry, not only from habit.

### Notation panel rules

- default to 4 rows max per slide
- make symbols visually prominent
- keep meaning and example columns readable at lecture distance
- examples should be concrete and large enough to scan quickly

### Font calculation rule

Table font size should be derived from:

- available row height
- available column width
- expected maximum line count

Do not default to tiny table fonts just because there are multiple rows.

---

## Spec-Writing Rules for Files Like `slides_part1.py`

When writing a slide spec, describe the slide in a way that makes layout intent explicit.

Every slide spec should make clear:

- the dominant visual type
- the teaching purpose
- what must be large
- what text is essential
- what must remain secondary
- what the audience should understand first

### Good spec writing

A good slide spec says things like:

- one large classifier-style geometry picture
- one dominant loss curve with a downhill arrow
- three large parallel panels
- split notation across two slides
- do not force running examples here
- keep the slide conceptual and clean
- this should be a hero example slide
- treat this as a worked example storyboard

### Weak spec writing

Avoid vague spec language like:

- maybe include
- optionally somewhere
- small example if possible
- add some labels
- use some icons

That kind of wording leads to undersized visuals and layout drift.

---

## Recommended Spec Template

Use this structure when defining lecture slides:

- Slide title
- Purpose
- What the slide should visually show
- Text or explanation to include on slide
- Bullets to include
- Formulas to include
- Concrete example anchor
- Speaker intent
- Rendering guidance

### Rendering guidance is important

For visually sensitive slides, explicitly say things like:

- do not render as five equal narrow cards
- diagram must dominate the slide
- split into separate slides if visuals become too small
- captions must remain secondary
- this should look like a poster-style concept slide
- note height should be auto-calculated
- visual and text stack should be vertically balanced

---

## Builder Mapping Guidance

When creating or updating a slide spec, choose the builder by visual intent.

### Choose `concept_poster` when:

- one idea should dominate
- one large diagram must fill the slide
- the slide is conceptual and visual-first

### Choose `example_pipeline` when:

- the slide is a worked story of transformation
- stages should show a process with a specific example
- each stage must remain visually large

### Choose `card_grid` only when:

- cards are simple
- cards remain large
- the slide is summarizing anchors or categories

### Choose `notation_panel` when:

- the slide is genuinely a notation reference
- rows remain few enough to read comfortably

### Choose `integrated_bridge` when:

- the transition between roles is the actual teaching point
- the difference between the roles must be visually obvious

---

## Part I-Specific Rules

For the early foundations section:

- prefer more slides with larger visuals over fewer dense slides
- keep overview separate from detailed examples
- split notation into multiple slides
- keep prerequisite concepts on separate large poster slides when needed
- use recurring examples sparingly and visibly
- if point, vector, and feature vector are visually too similar, strengthen the semantics or merge weak duplicate slides into one stronger bridge slide

A visually strong Part I is more important than compressing content.

---

## Update Rule

Whenever the visual design philosophy changes in a meaningful way, update:

- `README.md`
- `LLM_CONTEXT.md`
- `SLIDE_SPEC_RULES.md`

These three files should remain consistent with one another.
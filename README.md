# SlideForge

SlideForge is a Python-native, spec-driven presentation engine for generating polished slide decks.

It is designed to generate **any kind of presentation**, including but not limited to:

- academic lecture decks
- technical presentations
- business presentations
- architecture and system-design decks
- project kickoffs
- training materials
- research presentations
- educational visual explainers
- course slides
- roadmap and strategy presentations

The current example project in the repo focuses on machine learning and mathematics lecture slides, but that is only one use case. The engine itself should remain **general-purpose**.

---

## What the repo does today

Current reality:

- builds a PowerPoint deck from Python slide specs
- uses a builder registry keyed by slide `kind`
- stores project slide definitions under `src/slideforge/projects/`
- renders reusable text, boxes, lines, connectors, cards, panels, and diagram structures through shared primitives
- renders reusable mini-illustrations through `mini_visuals`
- supports large concept-poster slides, comparison slides, pipelines, notation panels, dependency maps, and other reusable slide families
- uses shared theme and header layers so color systems and title/subtitle/divider layout do not have to be hardcoded in each builder
- uses a split layout system so fitting, stacking, grids, posters, tables, cards, and dependency maps are computed instead of manually guessed
- writes the generated deck to the repo root as `ML_Foundations_Auto.pptx`

This is a working presentation generator, not just a prototype.

---

## Current entrypoint

Run the deck builder from the repo root:

```bash
python src/slideforge_app.py
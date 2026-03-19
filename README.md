# SlideForge

SlideForge is a Python-native presentation engine for generating polished academic lecture slides, especially for:

- machine learning
- mathematics
- geometry
- optimization
- probability and statistics
- programming and technical education

The project currently generates PowerPoint presentations (`.pptx`) from structured Python slide specs and is evolving toward a more reusable, builder-driven, theme-aware, and layout-aware architecture.

---

## What the repo does today

Current reality:

- builds a PowerPoint deck from Python slide specs
- uses a builder registry keyed by slide `kind`
- stores project slide definitions under `src/slideforge/projects/`
- renders reusable text, boxes, lines, connectors, cards, and panels through shared primitives
- renders reusable technical mini-illustrations through `mini_visuals.py`
- supports larger poster-style concept slides through dedicated builder families
- uses shared theme and header layers so color systems and title/subtitle/divider layout do not have to be hardcoded in each builder
- uses a split layout system so fitting, stacking, grids, posters, tables, cards, and dependency maps are computed instead of manually guessed
- writes the generated deck to the repo root as `ML_Foundations_Auto.pptx`

This is a working slide generator, not just a prototype.

---

## Current entrypoint

Run the deck builder from the repo root:

```bash
python src/slideforge_app.py
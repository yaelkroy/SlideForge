# SlideForge

SlideForge is a Python-based presentation engine for generating polished academic lecture slides, especially for machine learning, mathematics, optimization, probability, statistics, and technical teaching.

The project currently generates PowerPoint presentations (`.pptx`) from structured Python slide specs and is being refined into a more reusable, builder-driven, spec-first architecture.

---

## What the repo does today

Current reality:

- builds a PowerPoint deck from Python slide specs
- uses a builder registry keyed by slide `kind`
- stores deck/project slide definitions under `src/slideforge/projects/`
- renders reusable shapes, boxes, text, and connectors through shared primitives
- supports reusable technical mini-illustrations through `mini_visuals.py`
- writes the generated deck to the repo root as `ML_Foundations_Auto.pptx`

This is already a working slide generator, not just a prototype.

---

## Current entrypoint

Run the deck builder from the repo root:

```bash
python src/slideforge_app.py
# SlideForge

SlideForge is a Python-native, spec-driven presentation engine for generating polished PowerPoint decks.

It is designed to generate **any kind of presentation**, including:

- academic lecture decks
- technical presentations
- business presentations
- project kickoffs
- training materials
- research talks
- architecture and system-design decks
- roadmap and strategy decks
- educational visual explainers

The current example project in the repository is a machine-learning lecture deck, but that is only one example project. The engine itself must remain **general-purpose**.

---

## Current Status

SlideForge already produces working `.pptx` decks from Python slide specs.

Current architecture supports:

- project slide specs under `src/slideforge/projects/`
- explicit builder dispatch through a builder registry
- reusable theme, header, layout, and primitive rendering layers
- reusable mini-visual generation for diagrams and concept visuals
- modular builder families for repeated slide patterns
- generation of a final PowerPoint deck from one active project slide list

This is not just a static template repository. It is a real deck-generation engine.

---

## Core Principle

SlideForge should be treated as a **universal presentation platform**.

That means:

- engine modules should be reusable across many domains
- builder families should represent reusable slide patterns
- shared visual modules should be organized by visual family, not one deck section
- project specs should live above the engine layer
- machine learning is an example project, not the boundary of the platform

---

## How to Run

From the repo root:

```bash
python src/slideforge_app.py
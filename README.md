# SlideForge

SlideForge is a Python-based presentation engine for building polished academic slides, especially for machine learning, mathematics, optimization, probability, statistics, and technical teaching.

The project currently generates PowerPoint presentations (`.pptx`) and is being refactored into a more modular, spec-driven architecture that will later support diagrams, charts, AI-generated visuals, preview exports, and eventually audio/video assets.

---

## Current local repo path

Current working local path at the time of writing:

`C:\Projects\SlideForge`

This is a working reference, not a permanent guarantee.  
If the repo is moved, update this README and `LLM_CONTEXT.md`.

---

## Project status

This project is **under active architectural refactoring**.

Current reality:
- the implementation is still partially monolithic
- slide content is still defined inline in Python dictionaries
- many slide coordinates are still explicit
- several custom slide builders already exist
- some visuals are generated with matplotlib and inserted into PowerPoint
- the system already produces useful academic slides

Target direction:
- modular slide schemas
- reusable layout templates
- registries instead of large `if/elif` chains
- better asset management and caching
- validation for overlap, bounds, and readability
- support for AI-generated images and future video/audio assets

For the long-term architecture, read **`LLM_CONTEXT.md`** first.

---

## Main goals

- Generate high-quality academic lecture slides in Python
- Keep the system easy for an LLM to understand and extend
- Move from hardcoded layouts to reusable templates and regions
- Support diagrams, charts, mathematical visuals, and future media assets
- Maintain a repository structure that remains understandable even with small context windows

---

## Primary output today

- `.pptx`

## Planned future outputs

- `.pptx`
- `.pdf`
- slide preview images
- AI-generated backgrounds and illustrations
- diagrams and charts
- narration assets
- storyboard/video assets
- project manifests and validation reports

---

## Current repository role of each important file

### `LLM_CONTEXT.md`
The architectural north star for the project.

This is the most important context file for future LLM sessions.  
It defines:
- the long-term structure
- refactoring rules
- modularity principles
- small-context design requirements
- future asset and rendering plans

### `README.md`
The practical entry document for humans and LLMs.

This file should stay grounded in:
- what the project is
- what currently exists
- how to run it
- where to look next

---
## Current Status

SlideForge is currently a working Python PowerPoint generator under active refactor.

Current entrypoint:

```bash
python src/slideforge_app.py

## Current repository structure

This is the **current practical structure**, not the full target architecture:

```text
SlideForge/
├─ README.md
├─ LLM_CONTEXT.md
├─ pyproject.toml
├─ src/
│  ├─ slideforge_app.py
│  └─ slideforge/
│     ├─ __init__.py
│     ├─ app/
│     │  ├─ __init__.py
│     │  ├─ build_deck.py
│     │  ├─ presentation_factory.py
│     │  └─ slide_utils.py
│     ├─ assets/
│     │  ├─ __init__.py
│     │  └─ mini_visuals.py
│     ├─ builders/
│     │  ├─ __init__.py
│     │  ├─ basic.py
│     │  ├─ builder_registry.py
│     │  ├─ common.py
│     │  ├─ dependency_map.py
│     │  ├─ section_divider.py
│     │  └─ title_composite.py
│     ├─ config/
│     │  ├─ __init__.py
│     │  ├─ constants.py
│     │  └─ paths.py
│     ├─ io/
│     │  ├─ __init__.py
│     │  └─ backgrounds.py
│     ├─ projects/
│     │  ├─ __init__.py
│     │  └─ ml_foundations/
│     │     ├─ __init__.py
│     │     └─ slides_part1.py
│     ├─ render/
│     │  ├─ __init__.py
│     │  └─ primitives.py
│     └─ utils/
│        ├─ __init__.py
│        └─ units.py
├─ backgrounds/
├─ _generated/
├─ docs/
└─ tests/
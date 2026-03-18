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
│   slideforge_app.py
│
├───slideforge
│   │   __init__.py
│   │
│   ├───app
│   │   │   build_deck.py
│   │   │   presentation_factory.py
│   │   │   slide_utils.py
│   │   │   __init__.py
│   │   │
│   │   └───__pycache__
│   │           build_deck.cpython-311.pyc
│   │           build_deck.cpython-313.pyc
│   │           presentation_factory.cpython-311.pyc
│   │           slide_utils.cpython-311.pyc
│   │           __init__.cpython-311.pyc
│   │           __init__.cpython-313.pyc
│   │
│   ├───assets
│   │   │   mini_visuals.py
│   │   │   __init__.py
│   │   │
│   │   └───__pycache__
│   │           mini_visuals.cpython-311.pyc
│   │           __init__.cpython-311.pyc
│   │
│   ├───builders
│   │   │   basic.py
│   │   │   builder_registry.py
│   │   │   common.py
│   │   │   dependency_map.py
│   │   │   section_divider.py
│   │   │   title_composite.py
│   │   │   __init__.py
│   │   │
│   │   └───__pycache__
│   │           builder_registry.cpython-311.pyc
│   │           builder_registry.cpython-313.pyc
│   │           common.cpython-311.pyc
│   │           dependency_map.cpython-311.pyc
│   │           section_divider.cpython-311.pyc
│   │           title_composite.cpython-311.pyc
│   │           __init__.cpython-311.pyc
│   │           __init__.cpython-313.pyc
│   │
│   ├───config
│   │   │   constants.py
│   │   │   paths.py
│   │   │   __init__.py
│   │   │
│   │   └───__pycache__
│   │           constants.cpython-311.pyc
│   │           constants.cpython-313.pyc
│   │           paths.cpython-311.pyc
│   │           paths.cpython-313.pyc
│   │           __init__.cpython-311.pyc
│   │           __init__.cpython-313.pyc
│   │
│   ├───io
│   │   │   backgrounds.py
│   │   │   __init__.py
│   │   │
│   │   └───__pycache__
│   │           backgrounds.cpython-311.pyc
│   │           backgrounds.cpython-313.pyc
│   │           __init__.cpython-311.pyc
│   │           __init__.cpython-313.pyc
│   │
│   ├───projects
│   │   │   __init__.py
│   │   │
│   │   ├───ml_foundations
│   │   │   │   intro_slides.py
│   │   │   │   slides_part1.py
│   │   │   │   __init__.py
│   │   │   │
│   │   │   └───__pycache__
│   │   │           slides_part1.cpython-311.pyc
│   │   │           __init__.cpython-311.pyc
│   │   │
│   │   └───__pycache__
│   │           __init__.cpython-311.pyc
│   │
│   ├───render
│   │   │   primitives.py
│   │   │   __init__.py
│   │   │
│   │   └───__pycache__
│   │           primitives.cpython-311.pyc
│   │           __init__.cpython-311.pyc
│   │
│   ├───utils
│   │   │   units.py
│   │   │   __init__.py
│   │   │
│   │   └───__pycache__
│   │           units.cpython-311.pyc
│   │           units.cpython-313.pyc
│   │           __init__.cpython-311.pyc
│   │           __init__.cpython-313.pyc
│   │
│   └───__pycache__
│           __init__.cpython-311.pyc
│           __init__.cpython-313.pyc
│
└───slideforge.egg-info
        dependency_links.txt
        PKG-INFO
        requires.txt
        SOURCES.txt
        top_level.txt
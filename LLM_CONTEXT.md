# LLM_CONTEXT.md

## Project Identity



`LLM_CONTEXT.md` is the primary architecture and continuity guide for future development and for LLM-assisted work on this repository.
**Project name:** SlideForge  
**Project type:** Python presentation and media generation engine  
**Primary domain:** Academic lecture slides for machine learning, mathematics, geometry, optimization, probability, statistics, programming, and technical education  
**Primary output today:** `.pptx`  
**Planned outputs:** `.pptx`, `.pdf`, preview images, AI-generated images, diagrams, charts, videos, narration assets, subtitles, project manifests

---

## One-Sentence Mission

Build a **Python-native, spec-driven, modular presentation engine** that can generate polished academic slides and future AI-assisted media while staying easy for an LLM to understand, edit, and extend across long-running development.

---

## The Most Important Rule

This project must be designed for **small-context recovery**.

That means:
- many small modules
- stable file names
- one responsibility per file
- explicit schemas
- explicit registries
- explicit manifests
- explicit docs
- minimal hidden conventions
- minimal giant files

If something can be made more explicit for future LLM understanding, do it.

---

## Current Strategy

The project is moving from:

- one large script
- hardcoded coordinates
- mixed layout/render/content logic
- duplicated helpers
- slide-specific special cases

toward:

- schema-driven content
- modular layout engine
- reusable rendering primitives
- asset pipeline
- renderer backends
- project manifests
- machine-readable configs
- many small files

---

## Current Repo Reality

The repository already has a working modular split, but it is still mid-refactor.

Current active modules include:

- `src/slideforge_app.py`
- `src/slideforge/config/constants.py`
- `src/slideforge/config/paths.py`
- `src/slideforge/io/backgrounds.py`
- `src/slideforge/render/primitives.py`
- `src/slideforge/assets/mini_visuals.py`
- `src/slideforge/builders/basic.py`
- `src/slideforge/builders/title_composite.py`
- `src/slideforge/builders/section_divider.py`
- `src/slideforge/builders/dependency_map.py`
- `src/slideforge/builders/builder_registry.py`
- `src/slideforge/projects/ml_foundations/intro_slides.py`

The project is not yet fully migrated to typed schemas or a full layout engine.

When editing this repo, prefer:
- extending the existing modular structure
- avoiding logic moving back into `slideforge_app.py`
- keeping builders small and slide-type specific
- keeping project slide specs inside `projects/`
# 1. System Overview

## 1.1 Core pipeline

The long-term pipeline should be:

**source content -> normalized content spec -> layout plan -> asset generation -> renderer output -> validation -> export**

## 1.2 Main architectural layers

The project should be split into these layers:

1. **Domain**
2. **Project Config**
3. **Content Parsing**
4. **Content Transformation**
5. **Theme System**
6. **Layout System**
7. **Asset System**
8. **Rendering System**
9. **Validation System**
10. **Orchestration**
11. **Interfaces**
12. **Documentation/Context Bundles**

Each layer should have many small modules rather than a few huge modules.

---

# 2. Architecture Principles

## 2.1 Separation of concerns

Always separate:
- **what** the slide says
- **where** elements go
- **how** they are drawn
- **which** assets they use
- **which** style/theme is applied
- **which** output backend is used

## 2.2 Prefer structure over cleverness

The repo should favor:
- explicit classes
- explicit registries
- explicit config files
- explicit file maps
- explicit naming
- explicit manifests

over compact but opaque code.

## 2.3 Prefer many small files

Target:
- most files under ~200 lines
- many files in predictable directories
- one concept or subsystem per file

Avoid:
- giant utility files
- giant builder files
- giant config files
- giant schema files

## 2.4 Prefer registries over if/elif chains

Use registries for:
- slide builders
- asset generators
- visual generators
- renderers
- themes
- validators
- exporters

## 2.5 Prefer typed schemas over free-form dictionaries

Long-term the project should use structured models, ideally Pydantic, for all important objects.

---

# 3. Repository Layout

This is the intended long-term repository shape.

```text
slideforge/
├─ README.md
├─ LLM_CONTEXT.md
├─ CHANGELOG.md
├─ ROADMAP.md
├─ pyproject.toml
├─ .gitignore
├─ docs/
│  ├─ architecture/
│  │  ├─ overview.md
│  │  ├─ pipeline.md
│  │  ├─ registries.md
│  │  ├─ layouts.md
│  │  ├─ assets.md
│  │  ├─ rendering.md
│  │  ├─ validation.md
│  │  └─ video.md
│  ├─ schemas/
│  │  ├─ deck_spec.md
│  │  ├─ slide_spec.md
│  │  ├─ layout_spec.md
│  │  ├─ theme_spec.md
│  │  ├─ asset_spec.md
│  │  └─ project_manifest.md
│  ├─ guides/
│  │  ├─ adding_a_slide_type.md
│  │  ├─ adding_a_theme.md
│  │  ├─ adding_an_asset_generator.md
│  │  ├─ rendering_pptx.md
│  │  └─ context_bundle_workflow.md
│  ├─ known_issues.md
│  └─ design_decisions.md
├─ src/
│  └─ slideforge/
│     ├─ __init__.py
│     ├─ config/
│     │  ├─ paths.py
│     │  ├─ defaults.py
│     │  ├─ constants.py
│     │  └─ runtime.py
│     ├─ domain/
│     │  ├─ deck_spec.py
│     │  ├─ slide_spec.py
│     │  ├─ theme_spec.py
│     │  ├─ layout_spec.py
│     │  ├─ asset_spec.py
│     │  ├─ media_spec.py
│     │  ├─ project_manifest.py
│     │  ├─ render_job.py
│     │  └─ enums.py
│     ├─ projects/
│     │  ├─ loader.py
│     │  ├─ saver.py
│     │  ├─ resolver.py
│     │  ├─ manifest_builder.py
│     │  └─ project_index.py
│     ├─ content/
│     │  ├─ parsers/
│     │  │  ├─ markdown_parser.py
│     │  │  ├─ docx_parser.py
│     │  │  ├─ pdf_outline_parser.py
│     │  │  ├─ transcript_parser.py
│     │  │  └─ json_outline_parser.py
│     │  ├─ transformers/
│     │  │  ├─ normalize_deck.py
│     │  │  ├─ normalize_slide.py
│     │  │  ├─ section_splitter.py
│     │  │  ├─ notes_extractor.py
│     │  │  ├─ formula_normalizer.py
│     │  │  └─ example_card_builder.py
│     │  ├─ enrichers/
│     │  │  ├─ title_enricher.py
│     │  │  ├─ bullet_enricher.py
│     │  │  ├─ callout_enricher.py
│     │  │  └─ diagram_hint_enricher.py
│     │  └─ prompting/
│     │     ├─ prompt_models.py
│     │     ├─ prompt_templates.py
│     │     ├─ image_prompt_templates.py
│     │     └─ narration_prompt_templates.py
│     ├─ themes/
│     │  ├─ loader.py
│     │  ├─ registry.py
│     │  ├─ tokens/
│     │  │  ├─ colors.py
│     │  │  ├─ fonts.py
│     │  │  ├─ spacing.py
│     │  │  ├─ borders.py
│     │  │  └─ shadows.py
│     │  ├─ presets/
│     │  │  ├─ academic_light.yaml
│     │  │  ├─ academic_dark.yaml
│     │  │  ├─ ml_foundations.yaml
│     │  │  └─ lecture_minimal.yaml
│     │  └─ resolvers/
│     │     ├─ typography_resolver.py
│     │     ├─ color_resolver.py
│     │     └─ panel_style_resolver.py
│     ├─ layout/
│     │  ├─ engine.py
│     │  ├─ layout_context.py
│     │  ├─ region_model.py
│     │  ├─ geometry.py
│     │  ├─ collision.py
│     │  ├─ measurements.py
│     │  ├─ constraints.py
│     │  ├─ auto_fit.py
│     │  ├─ gutters.py
│     │  ├─ anchors.py
│     │  ├─ placements/
│     │  │  ├─ title_placement.py
│     │  │  ├─ subtitle_placement.py
│     │  │  ├─ footer_placement.py
│     │  │  ├─ panel_placement.py
│     │  │  ├─ bullets_placement.py
│     │  │  ├─ formula_placement.py
│     │  │  └─ image_placement.py
│     │  ├─ templates/
│     │  │  ├─ title_composite_layout.py
│     │  │  ├─ section_divider_layout.py
│     │  │  ├─ dependency_map_layout.py
│     │  │  ├─ formula_layout.py
│     │  │  ├─ two_column_layout.py
│     │  │  ├─ image_layout.py
│     │  │  ├─ card_grid_layout.py
│     │  │  ├─ timeline_layout.py
│     │  │  └─ comparison_layout.py
│     │  └─ registries/
│     │     ├─ layout_template_registry.py
│     │     └─ region_rule_registry.py
│     ├─ assets/
│     │  ├─ registry.py
│     │  ├─ asset_store.py
│     │  ├─ cache.py
│     │  ├─ naming.py
│     │  ├─ hash_utils.py
│     │  ├─ images/
│     │  │  ├─ background_selector.py
│     │  │  ├─ background_manifest.py
│     │  │  ├─ ai_image_adapter.py
│     │  │  ├─ image_prompt_resolver.py
│     │  │  ├─ image_postprocess.py
│     │  │  └─ thumbnail_generator.py
│     │  ├─ diagrams/
│     │  │  ├─ registry.py
│     │  │  ├─ dependency_map_diagram.py
│     │  │  ├─ vector_diagram.py
│     │  │  ├─ plane_diagram.py
│     │  │  ├─ classifier_diagram.py
│     │  │  ├─ timeline_diagram.py
│     │  │  └─ svg_export.py
│     │  ├─ charts/
│     │  │  ├─ registry.py
│     │  │  ├─ gaussian_chart.py
│     │  │  ├─ loss_curve_chart.py
│     │  │  ├─ scatter_separator_chart.py
│     │  │  ├─ bar_chart.py
│     │  │  ├─ line_chart.py
│     │  │  └─ chart_export.py
│     │  ├─ icons/
│     │  │  ├─ icon_registry.py
│     │  │  └─ icon_resolver.py
│     │  ├─ audio/
│     │  │  ├─ narration_script_builder.py
│     │  │  ├─ tts_adapter.py
│     │  │  └─ audio_manifest.py
│     │  └─ video/
│     │     ├─ storyboard_builder.py
│     │     ├─ transition_plan.py
│     │     ├─ frame_export.py
│     │     └─ video_manifest.py
│     ├─ visuals/
│     │  ├─ registry.py
│     │  ├─ primitives/
│     │  │  ├─ boxes.py
│     │  │  ├─ text.py
│     │  │  ├─ connectors.py
│     │  │  ├─ chips.py
│     │  │  ├─ labels.py
│     │  │  ├─ icons.py
│     │  │  ├─ panels.py
│     │  │  └─ overlays.py
│     │  ├─ composites/
│     │  │  ├─ title_banner.py
│     │  │  ├─ ghost_geometry_band.py
│     │  │  ├─ hub_spoke_map.py
│     │  │  └─ concept_card_grid.py
│     │  └─ adapters/
│     │     ├─ matplotlib_adapter.py
│     │     ├─ svg_adapter.py
│     │     └─ image_adapter.py
│     ├─ renderers/
│     │  ├─ base_renderer.py
│     │  ├─ render_context.py
│     │  ├─ pptx/
│     │  │  ├─ pptx_renderer.py
│     │  │  ├─ pptx_slide_dispatcher.py
│     │  │  ├─ pptx_text_renderer.py
│     │  │  ├─ pptx_box_renderer.py
│     │  │  ├─ pptx_image_renderer.py
│     │  │  ├─ pptx_connector_renderer.py
│     │  │  ├─ pptx_theme_adapter.py
│     │  │  └─ pptx_shape_factory.py
│     │  ├─ pdf/
│     │  │  ├─ pdf_renderer.py
│     │  │  └─ pdf_export_pipeline.py
│     │  ├─ preview/
│     │  │  ├─ preview_renderer.py
│     │  │  ├─ thumbnail_sheet.py
│     │  │  └─ preview_manifest.py
│     │  ├─ html/
│     │  │  ├─ html_renderer.py
│     │  │  └─ html_preview_template.py
│     │  └─ video/
│     │     ├─ video_renderer.py
│     │     ├─ ffmpeg_adapter.py
│     │     ├─ timeline_renderer.py
│     │     └─ subtitle_exporter.py
│     ├─ validation/
│     │  ├─ schema_validator.py
│     │  ├─ layout_validator.py
│     │  ├─ collision_validator.py
│     │  ├─ asset_validator.py
│     │  ├─ theme_validator.py
│     │  ├─ deck_validator.py
│     │  └─ report_builder.py
│     ├─ orchestration/
│     │  ├─ build_deck.py
│     │  ├─ build_slide.py
│     │  ├─ build_assets.py
│     │  ├─ build_video.py
│     │  ├─ incremental_rebuild.py
│     │  ├─ dependency_tracker.py
│     │  ├─ artifact_manifest.py
│     │  └─ job_runner.py
│     ├─ interfaces/
│     │  ├─ cli/
│     │  │  ├─ main.py
│     │  │  ├─ build_commands.py
│     │  │  ├─ validate_commands.py
│     │  │  ├─ asset_commands.py
│     │  │  └─ video_commands.py
│     │  ├─ api/
│     │  │  ├─ app.py
│     │  │  ├─ deck_routes.py
│     │  │  ├─ asset_routes.py
│     │  │  ├─ render_routes.py
│     │  │  └─ project_routes.py
│     │  └─ ui/
│     │     ├─ project_panel.py
│     │     ├─ asset_panel.py
│     │     └─ preview_panel.py
│     └─ context/
│        ├─ context_bundle.py
│        ├─ repo_index.py
│        ├─ module_summaries.py
│        └─ export_context_bundle.py
├─ tests/
│  ├─ unit/
│  ├─ integration/
│  ├─ golden/
│  └─ snapshots/
├─ examples/
│  ├─ minimal_deck/
│  ├─ ml_foundations/
│  └─ media_demo/
└─ tools/
   ├─ export_context_bundle.py
   ├─ validate_repo_structure.py
   ├─ check_large_files.py
   └─ build_example_project.py

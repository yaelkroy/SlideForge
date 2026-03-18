from __future__ import annotations

from typing import Any


SLIDES: list[dict[str, Any]] = [
    {
        "kind": "title_composite",
        "theme": "title",
        "background": "Background 8.png",
        "slide_number": 1,
        "slide_title": "Machine Learning Foundations: Geometry, Optimization, and Linear Classification",
        "purpose": (
            "Open the presentation with a strong conceptual bridge: this deck is about how "
            "geometric objects, optimization ideas, and computational representations become "
            "the language of early machine learning."
        ),
        "visual": (
            "A polished composite visual with four connected layers: "
            "point/vector in space, plane or separating line, loss curve/optimization surface, "
            "and classifier boundary over labeled points. The visual should feel like a "
            "progression from math objects to ML decisions."
        ),
        "text_explanation": (
            "From vectors and planes to loss functions, feature vectors, and classifiers"
        ),
        "bullets": [
            "Geometry gives us representation",
            "Optimization gives us learning",
            "Classification gives us prediction",
        ],
        "formulas": [
            "x ∈ R^d",
            "θ · x + θ₀ = 0",
            "θ ← θ − γ∇L(θ)",
        ],
        "concrete_example_anchor": (
            "Tiny embedded labels in the visual: x=(3,2,2), 3x₁+x₂−1=0, h(x)∈{−1,+1}."
        ),
        "speaker_intent": (
            "This deck starts before the classifier. First we need the language: points, "
            "vectors, planes, loss, gradients, and features."
        ),
        "title": "Machine Learning Foundations: Geometry, Optimization,\nand Linear Classification",
        "subtitle": "From vectors and planes to loss functions, feature vectors, and classifiers",
        "tiny_footer": "Foundations for early machine learning concepts and linear classification",
        "formula_ribbon": "",
        "show_footer_author": False,
        "show_author_line": True,
        "author_line": "Dr. Yael Demedetskaya",
        "layout": {
            "title_y": 0.90,
            "subtitle_y": 2.02,
            "author_y": 2.70,
            "visual_region": {"x": 1.00, "y": 3.30, "w": 11.30, "h": 2.00},
            "bullets_region": {"x": 2.75, "y": 5.38, "w": 7.90, "h": 0.36},
            "tiny_footer_region": {"x": 2.00, "y": 6.36, "w": 9.35, "h": 0.22},
        },
        "composite_visual": {
            "type": "connected_four_stage_banner",
            "style": "clean_academic_glass_panels",
            "panels": [
                {
                    "label": "Point / Vector",
                    "x": 1.05,
                    "y": 3.62,
                    "w": 2.30,
                    "h": 1.40,
                    "mini_visual": "vector_point_plane_combo",
                    "embedded_label": "x=(3,2,2)",
                },
                {
                    "label": "Plane / Separator",
                    "x": 3.82,
                    "y": 3.62,
                    "w": 2.30,
                    "h": 1.40,
                    "mini_visual": "plane_slice_with_normal",
                    "embedded_label": "3x₁+x₂−1=0",
                },
                {
                    "label": "Loss / Optimization",
                    "x": 6.59,
                    "y": 3.62,
                    "w": 2.30,
                    "h": 1.40,
                    "mini_visual": "loss_curve_with_descent_arrow",
                    "embedded_label": "θ ← θ−γ∇L(θ)",
                },
                {
                    "label": "Classifier",
                    "x": 9.36,
                    "y": 3.62,
                    "w": 2.30,
                    "h": 1.40,
                    "mini_visual": "scatter_with_boundary_and_classes",
                    "embedded_label": "h(x)∈{−1,+1}",
                },
            ],
            "connectors": [
                {"from": 0, "to": 1, "style": "soft_arrow"},
                {"from": 1, "to": 2, "style": "soft_arrow"},
                {"from": 2, "to": 3, "style": "soft_arrow"},
            ],
        },
        "design_notes": [
            "No footer author on title slide.",
            "No formula ribbon on title slide.",
            "Hero element is the four-panel progression.",
            "Keep lower area clean except for the three pill tags and tiny footer.",
        ],
    },
    {
        "kind": "section_divider",
        "theme": "section",
        "background": "Background 9.png",
        "slide_number": 2,
        "slide_title": "Part I — Framing, Notation, and Roadmap",
        "purpose": (
            "Mark the start of the first section clearly. This should feel like a section divider, "
            "not a content-heavy slide."
        ),
        "visual": (
            "Minimal, elegant section-divider design with a faint geometric mood and three soft "
            "ghost visuals: vector arrow, plane slice, scatterplot with separator."
        ),
        "text_explanation": (
            "How the course’s mathematical language becomes machine learning language"
        ),
        "bullets": [],
        "formulas": [],
        "concrete_example_anchor": (
            "Optional faint background labels: vector, hyperplane, classifier."
        ),
        "speaker_intent": (
            "In this part we establish the vocabulary and the map of the deck."
        ),
        "title": "Part I — Framing, Notation, and Roadmap",
        "subtitle": "How the course’s mathematical language becomes machine learning language",
        "tiny_footer": "",
        "formula_ribbon": "",
        "show_footer_author": True,
        "layout": {
            "title_region": {"x": 1.0, "y": 2.00, "w": 11.0, "h": 0.90},
            "subtitle_region": {"x": 1.45, "y": 2.88, "w": 10.1, "h": 0.40},
            "ghost_visual_region": {"x": 1.20, "y": 3.85, "w": 10.90, "h": 1.30},
        },
        "section_visual": {
            "type": "ghost_geometry_overlay",
            "style": "minimal_dark_academic",
            "elements": [
                {
                    "kind": "vector_arrow",
                    "x": 1.70,
                    "y": 4.00,
                    "w": 2.00,
                    "h": 0.80,
                    "label": "vector",
                },
                {
                    "kind": "plane_slice",
                    "x": 5.15,
                    "y": 3.92,
                    "w": 2.00,
                    "h": 0.84,
                    "label": "hyperplane",
                },
                {
                    "kind": "scatter_separator",
                    "x": 8.50,
                    "y": 3.92,
                    "w": 2.15,
                    "h": 0.84,
                    "label": "classifier",
                },
            ],
            "faint_grid": True,
            "soft_connector_line": True,
        },
        "design_notes": [
            "No bullet content on the divider.",
            "The three ghost visuals should be large, simple, and readable.",
            "Labels should be tiny and decorative, not dominant.",
        ],
    },
    {
        "kind": "dependency_map",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 3,
        "slide_title": "Why These Foundations Come First",
        "purpose": (
            "Explain why geometry, calculus, probability, and computation appear before or "
            "alongside ML concepts. The source material motivates points, vectors, planes, "
            "optimization, feature vectors, classifiers, and training behavior in one shared language."
        ),
        "visual": (
            "A clean dependency map with four prerequisite areas feeding into Machine Learning, "
            "plus a compact explanatory right column."
        ),
        "text_explanation": (
            "Machine learning is not a single idea. It depends on how we represent data, "
            "measure error, optimize parameters, and reason about uncertainty."
        ),
        "bullets": [
            "Vectors represent examples and parameters",
            "Planes represent decision boundaries",
            "Loss functions define prediction error",
            "Gradients tell us how to improve",
            "Probability helps us model uncertainty",
            "Computation makes the math executable",
        ],
        "formulas": [],
        "concrete_example_anchor": (
            "movie → feature vector; line/plane → classifier boundary; "
            "bowl surface → optimization; Gaussian curve → uncertainty"
        ),
        "speaker_intent": (
            "Before a model can learn, it needs representation, error measurement, "
            "and a method for improvement."
        ),
        "title": "Why These Foundations Come First",
        "subtitle": "",
        "tiny_footer": "",
        "formula_ribbon": "",
        "show_footer_author": True,
        "layout": {
            "title_y": 0.42,
            "box_title_gap": 0.34,
            "box_title_h": 0.24,
            "box_title_font_size": 13,
            "box_inner_pad_x": 0.16,
            "box_inner_pad_y": 0.16,
            "note_text_font_size": 13,
            "bullet_font_size": 11,
            "bullet_sub_font_size": 10,
            "takeaway_font_size": 12,
            "connector_width_pt": 1.3,
            "diagram_region": {"x": 1.15, "y": 1.30, "w": 6.95, "h": 4.15},
            "right_column_x": 8.52,
            "right_column_w": 3.58,
            "explanation_box": {"x": 8.52, "y": 1.46, "w": 3.58, "h": 0.86},
            "bullets_box": {"x": 8.40, "y": 2.88, "w": 3.70, "h": 2.38},
            "takeaway_box": {"x": 1.25, "y": 5.90, "w": 10.85, "h": 0.42},
        },
        "diagram": {
            "type": "hub_and_spokes",
            "style": "balanced_left_diagram_right_notes",
            "center_node": {
                "label": "Machine\nLearning",
                "x": 3.78,
                "y": 2.42,
                "w": 1.95,
                "h": 0.95,
                "style": "primary_hub_glow",
                "font_size": 18,
            },
            "input_nodes": [
                {
                    "label": "Linear Algebra /\nGeometry",
                    "x": 1.50,
                    "y": 1.45,
                    "w": 2.15,
                    "h": 0.82,
                    "style": "input_node",
                    "font_size": 14,
                    "mini_visual": "",
                    "callout": "",
                },
                {
                    "label": "Calculus /\nOptimization",
                    "x": 1.50,
                    "y": 3.72,
                    "w": 2.15,
                    "h": 0.82,
                    "style": "input_node",
                    "font_size": 14,
                    "mini_visual": "",
                    "callout": "",
                },
                {
                    "label": "Probability /\nUncertainty",
                    "x": 5.90,
                    "y": 1.45,
                    "w": 1.95,
                    "h": 0.82,
                    "style": "input_node",
                    "font_size": 14,
                    "mini_visual": "",
                    "callout": "",
                },
                {
                    "label": "Computation /\nNumPy",
                    "x": 5.90,
                    "y": 3.72,
                    "w": 1.95,
                    "h": 0.82,
                    "style": "input_node",
                    "font_size": 14,
                    "mini_visual": "",
                    "callout": "",
                },
            ],
            "arrows": [
                {"from": "Linear Algebra /\nGeometry", "to": "Machine\nLearning", "style": "clean_connector"},
                {"from": "Calculus /\nOptimization", "to": "Machine\nLearning", "style": "clean_connector"},
                {"from": "Probability /\nUncertainty", "to": "Machine\nLearning", "style": "clean_connector"},
                {"from": "Computation /\nNumPy", "to": "Machine\nLearning", "style": "clean_connector"},
            ],
        },
        "explanation_box": {
            "title": "Core idea",
            "text": (
                "Machine learning is built from representation, geometry, "
                "optimization, uncertainty, and computation."
            ),
        },
        "right_panel_title": "Why these prerequisites matter",
        "right_panel_bullets": [
            "Vectors represent examples and parameters",
            "Planes represent decision boundaries",
            "Loss functions define prediction error",
            "Gradients tell us how to improve",
            "Probability helps us model uncertainty",
            "Computation makes the math executable",
        ],
        "takeaway": (
            "Before a model can learn, it needs representation, error measurement, "
            "and a method for improvement."
        ),
        "design_notes": [
            "Full right column stays.",
            "Box title spacing is controlled by layout.",
            "No mini visuals or callouts on this slide.",
            "Diagram stays left; notes stay right; takeaway stays below.",
        ],
    },
]
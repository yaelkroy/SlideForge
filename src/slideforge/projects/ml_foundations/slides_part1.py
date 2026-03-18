from __future__ import annotations

from typing import Any


ML_FOUNDATIONS_PART1_SLIDES: list[dict[str, Any]] = [
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
            "A single hero composition in the lower half of the slide showing a point/vector, "
            "a separator, a loss curve with downhill arrow, and a classifier boundary."
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
            "Tiny embedded labels only: x=(3,2,2), 3x₁+x₂−1=0, h(x)∈{−1,+1}"
        ),
        "speaker_intent": (
            "This deck starts before the classifier. First we need the language: points, "
            "vectors, planes, loss, gradients, and features."
        ),
        "title": "Machine Learning Foundations: Geometry, Optimization,\nand Linear Classification",
        "subtitle": "From vectors and planes to loss functions, feature vectors, and classifiers",
        "tiny_footer": "Foundations for early machine learning concepts and linear classification",
        "author_line": "Dr. Yael Demedetskaya",
        "show_author_line": True,
        "show_footer_author": False,
        "layout": {
            "title_y": 0.90,
            "subtitle_y": 2.02,
            "author_y": 2.70,
            "visual_region": {"x": 0.82, "y": 3.05, "w": 11.55, "h": 2.42},
            "bullets_region": {"x": 2.65, "y": 5.60, "w": 8.10, "h": 0.34},
            "tiny_footer_region": {"x": 2.00, "y": 6.36, "w": 9.35, "h": 0.22},
        },
        "composite_visual": {
            "type": "connected_four_stage_banner",
            "style": "hero_academic_progression",
            "panels": [
                {
                    "label": "Point / Vector",
                    "x": 0.95,
                    "y": 3.34,
                    "w": 2.62,
                    "h": 1.72,
                    "mini_visual": "vector_point_plane_combo",
                    "embedded_label": "x=(3,2,2)",
                    "visual_h": 1.12,
                },
                {
                    "label": "Plane / Separator",
                    "x": 3.82,
                    "y": 3.34,
                    "w": 2.62,
                    "h": 1.72,
                    "mini_visual": "plane_slice_with_normal",
                    "embedded_label": "3x₁+x₂−1=0",
                    "visual_h": 1.12,
                },
                {
                    "label": "Loss / Optimization",
                    "x": 6.69,
                    "y": 3.34,
                    "w": 2.62,
                    "h": 1.72,
                    "mini_visual": "loss_curve_with_descent_arrow",
                    "embedded_label": "θ ← θ−γ∇L(θ)",
                    "visual_h": 1.12,
                },
                {
                    "label": "Classifier",
                    "x": 9.56,
                    "y": 3.34,
                    "w": 2.62,
                    "h": 1.72,
                    "mini_visual": "scatter_with_boundary_and_classes",
                    "embedded_label": "h(x)∈{−1,+1}",
                    "visual_h": 1.12,
                },
            ],
            "connectors": [
                {"from": 0, "to": 1, "style": "soft_arrow"},
                {"from": 1, "to": 2, "style": "soft_arrow"},
                {"from": 2, "to": 3, "style": "soft_arrow"},
            ],
        },
    },
    {
        "kind": "section_divider",
        "theme": "section",
        "background": "Background 9.png",
        "slide_number": 2,
        "slide_title": "Part I — Framing, Notation, and Roadmap",
        "purpose": "Mark the start of the first section clearly. This should feel like a section divider.",
        "visual": (
            "A dark academic divider with one wide central visual band: vector arrow, plane slice, "
            "and scatterplot with separator."
        ),
        "text_explanation": "How the course’s mathematical language becomes machine learning language",
        "bullets": [],
        "formulas": [],
        "concrete_example_anchor": "Faint background words only: vector, hyperplane, training set, classifier",
        "speaker_intent": "In this part we establish the vocabulary and the map of the deck.",
        "title": "Part I — Framing, Notation, and Roadmap",
        "subtitle": "How the course’s mathematical language becomes machine learning language",
        "layout": {
            "title_region": {"x": 1.0, "y": 2.00, "w": 11.0, "h": 0.90},
            "subtitle_region": {"x": 1.20, "y": 2.92, "w": 10.6, "h": 0.40},
        },
        "section_visual": {
            "type": "wide_concept_band",
            "style": "minimal_dark_academic",
            "elements": [
                {
                    "kind": "vector_arrow",
                    "x": 1.00,
                    "y": 3.70,
                    "w": 3.00,
                    "h": 1.14,
                    "label": "vector",
                },
                {
                    "kind": "plane_slice",
                    "x": 4.35,
                    "y": 3.68,
                    "w": 3.00,
                    "h": 1.16,
                    "label": "hyperplane",
                },
                {
                    "kind": "scatter_separator",
                    "x": 7.80,
                    "y": 3.68,
                    "w": 3.15,
                    "h": 1.16,
                    "label": "classifier",
                },
            ],
            "faint_grid": True,
            "soft_connector_line": True,
        },
    },
    {
        "kind": "dependency_map",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 3,
        "slide_title": "Why These Foundations Come First",
        "purpose": (
            "Explain why geometry, calculus, probability, and computation must appear before "
            "or alongside machine-learning concepts."
        ),
        "visual": (
            "A clean dependency map with four prerequisite nodes and one central Machine Learning node."
        ),
        "text_explanation": (
            "Machine learning depends on representation, error measurement, optimization, uncertainty, and computation."
        ),
        "bullets": [],
        "formulas": ["x ↦ feature vector", "L(θ)", "∇θL(θ)"],
        "concrete_example_anchor": "No tiny icons here; keep the slide conceptually clean.",
        "speaker_intent": (
            "Before a model can learn, we need a representation of data, a score for error, "
            "and a method for improvement."
        ),
        "title": "Why These Foundations Come First",
        "subtitle": "",
        "layout": {
            "title_y": 0.42,
            "box_title_gap": 0.30,
            "box_title_h": 0.24,
            "box_title_font_size": 13,
            "box_inner_pad_x": 0.16,
            "box_inner_pad_y": 0.14,
            "note_text_font_size": 12,
            "takeaway_font_size": 12,
            "connector_width_pt": 1.45,
            "explanation_box": {"x": 8.55, "y": 2.05, "w": 3.35, "h": 1.20},
            "bullets_box": None,
            "takeaway_box": {"x": 1.35, "y": 5.82, "w": 10.50, "h": 0.44},
        },
        "diagram": {
            "type": "hub_and_spokes",
            "style": "large_clean_prereq_map",
            "center_node": {
                "label": "Machine\nLearning",
                "x": 4.00,
                "y": 2.55,
                "w": 2.10,
                "h": 1.05,
                "style": "primary_hub_glow",
                "font_size": 19,
            },
            "input_nodes": [
                {
                    "label": "Linear Algebra /\nGeometry",
                    "x": 1.25,
                    "y": 1.40,
                    "w": 2.30,
                    "h": 0.95,
                    "font_size": 14,
                },
                {
                    "label": "Calculus /\nOptimization",
                    "x": 1.25,
                    "y": 3.95,
                    "w": 2.30,
                    "h": 0.95,
                    "font_size": 14,
                },
                {
                    "label": "Probability /\nUncertainty",
                    "x": 6.55,
                    "y": 1.40,
                    "w": 2.10,
                    "h": 0.95,
                    "font_size": 14,
                },
                {
                    "label": "Computation /\nNumPy",
                    "x": 6.55,
                    "y": 3.95,
                    "w": 2.10,
                    "h": 0.95,
                    "font_size": 14,
                },
            ],
        },
        "explanation_box": {
            "title": "Core idea",
            "text": (
                "Machine learning depends on representation, error measurement, "
                "optimization, uncertainty, and computation."
            ),
        },
        "right_panel_title": "",
        "right_panel_bullets": [],
        "takeaway": "Representation, error, improvement, uncertainty, and computation all arrive before learning can happen.",
    },
    {
        "kind": "prereq_grid",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 4,
        "slide_title": "Geometry Gives Us Representation",
        "purpose": "Make the contribution of geometry large, concrete, and visually obvious.",
        "visual": (
            "One large classifier-style geometry picture with points in space, a separator, and a labeled vector x."
        ),
        "text_explanation": "",
        "bullets": [],
        "formulas": [],
        "concrete_example_anchor": "Use x=(3,2,2) and a boundary example 3x₁+x₂−1=0.",
        "speaker_intent": "Without geometry, we have no meaningful space in which learning can happen.",
        "title": "Geometry Gives Us Representation",
        "subtitle": "",
        "layout": {
            "title_y": 0.42,
            "grid_region": {"x": 1.05, "y": 1.52, "w": 10.90, "h": 4.65},
            "cols": 1,
            "rows": 1,
            "gap_x": 0.0,
            "gap_y": 0.0,
            "takeaway_box": {"x": 1.10, "y": 6.08, "w": 10.80, "h": 0.24},
        },
        "panels": [
            {
                "title": "Geometry lets us place examples in space, compare directions, and define boundaries",
                "mini_visual": "line_to_boundary",
                "caption": "vectors represent objects · space gives structure · boundaries separate regions",
                "formula": "x ∈ R^d     ·     θ · x + θ₀ = 0",
                "anchor": "point/vector x=(3,2,2) and boundary 3x₁+x₂−1=0",
            },
        ],
        "takeaway": "Geometry is the language that lets examples become locations, directions, and separable regions.",
    },
    {
        "kind": "prereq_grid",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 5,
        "slide_title": "Optimization Improves Parameters",
        "purpose": "Make the contribution of optimization large and intuitive.",
        "visual": "One large loss picture with a current point, a downhill arrow, and a lower point.",
        "text_explanation": "",
        "bullets": [],
        "formulas": [],
        "concrete_example_anchor": "Use a visible bowl surface or 1D loss curve.",
        "speaker_intent": "Optimization is how a model changes from a bad fit into a better fit.",
        "title": "Optimization Improves Parameters",
        "subtitle": "",
        "layout": {
            "title_y": 0.42,
            "grid_region": {"x": 1.05, "y": 1.52, "w": 10.90, "h": 4.65},
            "cols": 1,
            "rows": 1,
            "gap_x": 0.0,
            "gap_y": 0.0,
            "takeaway_box": {"x": 1.10, "y": 6.08, "w": 10.80, "h": 0.24},
        },
        "panels": [
            {
                "title": "Optimization gives us a rule for improving parameters by moving toward lower loss",
                "mini_visual": "loss_curve_with_descent_arrow",
                "caption": "error becomes a function · lower is better · updates move downhill",
                "formula": "L(θ)     ·     θ ← θ − γ∇L(θ)",
                "anchor": "current parameter, lower-loss direction, visible minimum",
            },
        ],
        "takeaway": "Optimization turns model improvement into a concrete downhill search problem.",
    },
    {
        "kind": "prereq_grid",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 6,
        "slide_title": "Probability Models Uncertainty",
        "purpose": "Explain that not everything in machine learning is exact or deterministic.",
        "visual": "One large uncertainty visual with a Gaussian curve, mean, and spread.",
        "text_explanation": "",
        "bullets": [],
        "formulas": [],
        "concrete_example_anchor": "Use one Gaussian with clear mean and spread.",
        "speaker_intent": "Real data is not perfectly clean, so machine learning must reason probabilistically.",
        "title": "Probability Models Uncertainty",
        "subtitle": "",
        "layout": {
            "title_y": 0.42,
            "grid_region": {"x": 1.05, "y": 1.52, "w": 10.90, "h": 4.65},
            "cols": 1,
            "rows": 1,
            "gap_x": 0.0,
            "gap_y": 0.0,
            "takeaway_box": {"x": 1.10, "y": 6.08, "w": 10.80, "h": 0.24},
        },
        "panels": [
            {
                "title": "Probability lets us describe uncertainty, variability, and noisy data",
                "mini_visual": "gaussian_curve",
                "caption": "outcomes can vary · uncertainty can be modeled · ML must reason under uncertainty",
                "formula": "X ∼ N(μ,σ²)",
                "anchor": "visible mean and spread",
            },
        ],
        "takeaway": "Probability gives machine learning a principled way to reason about noise and uncertainty.",
    },
    {
        "kind": "prereq_grid",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 7,
        "slide_title": "Computation Makes the Math Executable",
        "purpose": "Explain the role of computation as the bridge between mathematical ideas and real model-building.",
        "visual": "One large matrix/vector/code-style visual showing executable math.",
        "text_explanation": "",
        "bullets": [],
        "formulas": [],
        "concrete_example_anchor": "Use a clear matrix-vector visual or array layout.",
        "speaker_intent": "Without computation, the formulas stay on paper.",
        "title": "Computation Makes the Math Executable",
        "subtitle": "",
        "layout": {
            "title_y": 0.42,
            "grid_region": {"x": 1.05, "y": 1.52, "w": 10.90, "h": 4.65},
            "cols": 1,
            "rows": 1,
            "gap_x": 0.0,
            "gap_y": 0.0,
            "takeaway_box": {"x": 1.10, "y": 6.08, "w": 10.80, "h": 0.24},
        },
        "panels": [
            {
                "title": "Computation turns the math into something we can evaluate, repeat, and optimize",
                "mini_visual": "array_glyph",
                "caption": "vectors become arrays · formulas become code · repeated updates become algorithms",
                "formula": "A x",
                "anchor": "matrix/vector/array structure as executable math",
            },
        ],
        "takeaway": "Computation is what lets mathematical ideas become trainable algorithms.",
    },
    {
        "kind": "pipeline",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 8,
        "slide_title": "The Big Story: From Data to Decisions",
        "purpose": "Give the full conceptual storyline of the deck.",
        "visual": "A large five-stage conceptual pipeline.",
        "text_explanation": (
            "Machine learning turns real-world objects into numerical representations, places "
            "them in a geometric space, and learns rules that predict labels or values."
        ),
        "bullets": [],
        "formulas": [
            "raw input → x ∈ R^d → h(x)",
            "h(x)=sign(θ · x+θ₀)",
        ],
        "concrete_example_anchor": "No running examples here. Keep the slide conceptual and clean.",
        "speaker_intent": "This is the whole arc of the deck: representation, geometry, learning, prediction.",
        "title": "The Big Story: From Data to Decisions",
        "subtitle": (
            "Machine learning turns real-world objects into numerical representations, places "
            "them in a geometric space, and learns rules that predict labels or values."
        ),
        "pipeline": {
            "steps": [
                {
                    "title": "Raw Object",
                    "mini_visual": "raw_object_pair",
                    "body": "",
                    "footer": "raw input",
                },
                {
                    "title": "Feature Vector",
                    "mini_visual": "feature_vector_pair",
                    "body": "",
                    "footer": "x ∈ R^d",
                },
                {
                    "title": "Point in Space",
                    "mini_visual": "point_in_space",
                    "body": "",
                    "footer": "point / vector",
                },
                {
                    "title": "Model / Boundary",
                    "mini_visual": "decision_boundary",
                    "body": "",
                    "footer": "θ · x + θ₀",
                },
                {
                    "title": "Prediction / Error",
                    "mini_visual": "prediction_error",
                    "body": "",
                    "footer": "h(x), L(θ)",
                },
            ]
        },
        "examples": [],
        "takeaway": "Representation comes first: objects become vectors, vectors enter geometry, and geometry supports prediction.",
        "layout": {
            "title_y": 0.42,
            "subtitle_y": 0.98,
            "pipeline_region": {"x": 0.82, "y": 1.80, "w": 11.35, "h": 2.38},
            "pipeline_gap": 0.14,
            "takeaway_box": {"x": 1.00, "y": 5.42, "w": 10.90, "h": 0.66},
        },
    },
    {
        "kind": "example_pipeline",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 9,
        "slide_title": "Example A — From Movie to Feature Vector to Label",
        "purpose": "Show one full, memorable representation example.",
        "visual": (
            "A large worked pipeline from movie object to feature vector to prediction."
        ),
        "text_explanation": "A real object becomes a machine-readable representation, then a prediction.",
        "bullets": ["object", "encoding", "representation", "prediction"],
        "formulas": [
            "x=[1,0,1,1,0]",
            "h(x)=sign(θ · x+θ₀)",
        ],
        "concrete_example_anchor": "movie → 5-feature vector → like/dislike",
        "speaker_intent": "This is what representation means in machine learning.",
        "title": "Example A — From Movie to Feature Vector to Label",
        "subtitle": "A real object becomes a machine-readable representation, then a prediction.",
        "example_pipeline": {
            "stages": [
                {
                    "title": "Movie",
                    "mini_visual": "movie_card",
                    "caption": "object / metadata",
                },
                {
                    "title": "Encoding",
                    "mini_visual": "movie_to_vector",
                    "caption": "5-feature binary vector",
                    "formula": "x=[1,0,1,1,0]",
                },
                {
                    "title": "Geometric Representation",
                    "mini_visual": "point_in_space",
                    "caption": "point in feature space",
                },
                {
                    "title": "Prediction",
                    "mini_visual": "prediction_error",
                    "caption": "like / dislike",
                    "formula": "h(x)=sign(θ · x+θ₀)",
                },
            ]
        },
        "takeaway": "A real object becomes a feature vector before it becomes a prediction.",
        "layout": {
            "title_y": 0.42,
            "subtitle_y": 0.98,
            "pipeline_region": {"x": 0.78, "y": 1.82, "w": 11.45, "h": 2.78},
            "pipeline_gap": 0.28,
            "bullets_y": 4.96,
            "takeaway_y": 5.42,
        },
    },
    {
        "kind": "example_pipeline",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 10,
        "slide_title": "Example B — From Digit Image to Class Label",
        "purpose": "Show that the same pipeline works for a different kind of data.",
        "visual": (
            "A large worked pipeline from handwritten digit to features to class label."
        ),
        "text_explanation": (
            "Different objects can still enter the same machine-learning pipeline once represented numerically."
        ),
        "bullets": ["image", "features", "point", "class"],
        "formulas": [
            "x=[brightness,width]",
            "h(x)=7",
        ],
        "concrete_example_anchor": "digit → brightness/width features → class label",
        "speaker_intent": "The raw object changes, but the mathematical pipeline stays.",
        "title": "Example B — From Digit Image to Class Label",
        "subtitle": (
            "Different objects can still enter the same machine-learning pipeline once represented numerically."
        ),
        "example_pipeline": {
            "stages": [
                {
                    "title": "Digit",
                    "mini_visual": "digit_card",
                    "caption": "image input",
                },
                {
                    "title": "Features",
                    "mini_visual": "feature_vector_pair",
                    "caption": "brightness / width",
                    "formula": "x=[brightness,width]",
                },
                {
                    "title": "Geometric Representation",
                    "mini_visual": "point_in_space",
                    "caption": "point in low-dimensional space",
                },
                {
                    "title": "Prediction",
                    "mini_visual": "digit_to_label",
                    "caption": "class label",
                    "formula": "h(x)=7",
                },
            ]
        },
        "takeaway": "Different data types still pass through the same representation-first pipeline.",
        "layout": {
            "title_y": 0.42,
            "subtitle_y": 0.98,
            "pipeline_region": {"x": 0.78, "y": 1.82, "w": 11.45, "h": 2.78},
            "pipeline_gap": 0.28,
            "bullets_y": 4.96,
            "takeaway_y": 5.42,
        },
    },
    {
        "kind": "card_grid",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 11,
        "slide_title": "Running Examples We Will Reuse",
        "purpose": "Introduce the recurring examples once, in a way that stays readable.",
        "visual": "A 2×3 grid of large anchor cards, each simpler and more visual than before.",
        "text_explanation": "These examples will return throughout the deck as anchors.",
        "bullets": [],
        "formulas": [],
        "concrete_example_anchor": "This slide itself is the anchor slide.",
        "speaker_intent": (
            "Whenever a new idea appears, it will usually connect back to one of these examples."
        ),
        "title": "Running Examples We Will Reuse",
        "subtitle": "These examples will return throughout the deck as anchors.",
        "grid": {
            "rows": 2,
            "cols": 3,
            "cards": [
                {
                    "title": "Point / Vector",
                    "mini_visual": "point_in_space",
                    "formula": "x=(3,2,2)",
                    "caption": "geometry anchor",
                },
                {
                    "title": "Plane / Hyperplane",
                    "mini_visual": "line_to_boundary",
                    "formula": "3x₁+x₂−1=0",
                    "caption": "boundary anchor",
                },
                {
                    "title": "1D Optimization",
                    "mini_visual": "loss_curve",
                    "formula": "f(x)=⅓x³−x²−3x+10",
                    "caption": "optimization anchor",
                },
                {
                    "title": "Gradient",
                    "mini_visual": "loss_curve_with_descent_arrow",
                    "formula": "f(θ)=θ₁²+θ₂²",
                    "caption": "descent anchor",
                },
                {
                    "title": "Gaussian",
                    "mini_visual": "gaussian_curve",
                    "formula": "X∼N(1,2)",
                    "caption": "probability anchor",
                },
                {
                    "title": "Movie Recommender",
                    "mini_visual": "movie_to_vector",
                    "formula": "5-feature vector + label ±1",
                    "caption": "supervised-learning anchor",
                },
            ]
        },
        "takeaway": "geometry, optimization, probability, computation, supervised learning",
        "layout": {
            "title_y": 0.42,
            "subtitle_y": 0.98,
            "grid_region": {"x": 0.88, "y": 1.55, "w": 11.28, "h": 4.55},
            "gap_x": 0.28,
            "gap_y": 0.32,
            "takeaway_y": 6.14,
        },
    },
    {
        "kind": "notation_panel",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 12,
        "slide_title": "Notation You Must Read Fluently — Objects and Coordinates",
        "purpose": "Clarify notation without overwhelming the audience.",
        "visual": "A three-column notation panel with only the first four entries.",
        "text_explanation": (
            "In machine learning, the same letters are reused across different mathematical objects. Context matters."
        ),
        "bullets": [],
        "formulas": [
            "x∈R^d",
            "A∈R^{m×n}",
            "y∈{−1,+1}",
        ],
        "concrete_example_anchor": "Use large examples: x=(3,2,2), x₂=2, Ax, y=+1",
        "speaker_intent": "Notation should feel like compressed meaning, not decorative symbols.",
        "title": "Notation You Must Read Fluently — Objects and Coordinates",
        "subtitle": (
            "In machine learning, the same letters are reused across different mathematical objects. Context matters."
        ),
        "columns": ["symbol", "meaning", "visual example"],
        "rows": [
            {"symbol": "x", "meaning": "point / feature vector / example", "example": "x=(3,2,2)"},
            {"symbol": "xᵢ", "meaning": "i-th coordinate", "example": "x₂=2"},
            {"symbol": "A", "meaning": "matrix", "example": "A x"},
            {"symbol": "y", "meaning": "label", "example": "y=+1"},
        ],
        "layout": {
            "title_y": 0.42,
            "subtitle_y": 0.98,
            "table_box": {"x": 0.88, "y": 1.55, "w": 11.20, "h": 4.85},
            "formula_y": 6.55,
        },
    },
    {
        "kind": "notation_panel",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 13,
        "slide_title": "Notation You Must Read Fluently — Parameters, Classifiers, and Loss",
        "purpose": "Continue notation in a readable way.",
        "visual": "A three-column notation panel with the parameter and learning symbols.",
        "text_explanation": (
            "These symbols will appear repeatedly in linear models, classification, and optimization."
        ),
        "bullets": [],
        "formulas": [
            "θ∈R^d",
            "θ·x+θ₀=0",
            "h(x)=sign(θ·x+θ₀)",
            "L(θ)",
        ],
        "concrete_example_anchor": "Use large examples: θ·x+θ₀=0, h(x)=sign(θ·x+θ₀), L(θ)",
        "speaker_intent": "These are the symbols that make geometry and learning talk to each other.",
        "title": "Notation You Must Read Fluently — Parameters, Classifiers, and Loss",
        "subtitle": (
            "These symbols will appear repeatedly in linear models, classification, and optimization."
        ),
        "columns": ["symbol", "meaning", "visual example"],
        "rows": [
            {"symbol": "θ", "meaning": "parameter vector / normal vector", "example": "θ·x+θ₀=0"},
            {"symbol": "θ₀", "meaning": "offset / intercept", "example": "boundary shift"},
            {"symbol": "h", "meaning": "classifier / prediction rule", "example": "h(x)=sign(θ·x+θ₀)"},
            {"symbol": "L", "meaning": "loss", "example": "L(θ)"},
        ],
        "layout": {
            "title_y": 0.42,
            "subtitle_y": 0.98,
            "table_box": {"x": 0.88, "y": 1.55, "w": 11.20, "h": 4.85},
            "formula_y": 6.55,
        },
    },
    {
        "kind": "triple_role",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 14,
        "slide_title": "Point, Vector, Feature Vector: Same Shape, Different Role",
        "purpose": "Bridge geometry to machine-learning representation.",
        "visual": (
            "Three large side-by-side panels using the same object: point in coordinate space, "
            "arrow from origin, feature vector representing an example."
        ),
        "text_explanation": (
            "Mathematically, these can look identical. Conceptually, they play different roles."
        ),
        "bullets": [
            "location in space",
            "displacement from origin",
            "encoded example for prediction",
        ],
        "formulas": [
            "x=(3,2,2)",
            "x∈R^3",
            "x↦feature vector",
        ],
        "concrete_example_anchor": (
            "Use x=(3,2,2) for point/vector and a movie feature vector for ML representation."
        ),
        "speaker_intent": (
            "This is one of the most important conceptual bridges in the whole deck."
        ),
        "title": "Point, Vector, Feature Vector: Same Shape, Different Role",
        "subtitle": "",
        "panels": [
            {
                "title": "Point",
                "mini_visual": "point_in_space",
                "caption": "location in coordinate space",
                "formula": "x=(3,2,2)",
            },
            {
                "title": "Vector",
                "mini_visual": "vector_arrow",
                "caption": "arrow from the origin",
                "formula": "x∈R^3",
            },
            {
                "title": "Feature Vector",
                "mini_visual": "movie_to_vector",
                "caption": "encoded example for prediction",
                "formula": "x↦feature vector",
            },
        ],
        "layout": {
            "title_y": 0.42,
            "panel_region": {"x": 0.88, "y": 1.78, "w": 11.24, "h": 3.05},
            "panel_gap": 0.24,
            "bullets_y": 5.16,
            "formula_y": 5.56,
        },
    },
    {
        "kind": "integrated_bridge",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 15,
        "slide_title": "One Object, Three Interpretations",
        "purpose": "Give a full large visual example immediately after the concept slide.",
        "visual": (
            "One integrated visual with the same coordinate triple, the same arrow, the same "
            "feature-vector table, and visible annotation arrows explaining the role change."
        ),
        "text_explanation": "The coordinates did not change. The interpretation changed.",
        "bullets": [],
        "formulas": [
            "x=(3,2,2)",
            "movie → x",
        ],
        "concrete_example_anchor": "Make the movie example explicit here.",
        "speaker_intent": (
            "The mathematical object stays the same shape, but its meaning depends on context."
        ),
        "title": "One Object, Three Interpretations",
        "subtitle": "The coordinates did not change. The interpretation changed.",
        "integrated_visual": {
            "base_object": "x=(3,2,2)",
            "left_role": {
                "title": "Point",
                "mini_visual": "point_in_space",
                "caption": "same coordinates, location in space",
            },
            "center_role": {
                "title": "Vector",
                "mini_visual": "vector_arrow",
                "caption": "same coordinates, displacement from origin",
            },
            "right_role": {
                "title": "Feature Vector",
                "mini_visual": "movie_to_vector",
                "caption": "same shape, encoded movie example",
            },
            "bridge_labels": [
                "same coordinates",
                "different role",
                "context changes meaning",
            ],
        },
        "takeaway": "The shape of the mathematical object stays the same; only the interpretation changes.",
        "layout": {
            "title_y": 0.42,
            "subtitle_y": 0.98,
            "visual_y": 1.80,
            "formula_y": 4.60,
            "takeaway_y": 5.28,
        },
    },
]
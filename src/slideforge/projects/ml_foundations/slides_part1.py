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
            "A hero composite visual occupying most of the lower 60% of the slide, with four "
            "large connected stages, not tiny cards."
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
            "visual_region": {"x": 0.85, "y": 3.10, "w": 11.50, "h": 2.35},
            "bullets_region": {"x": 2.70, "y": 5.58, "w": 8.00, "h": 0.34},
            "tiny_footer_region": {"x": 2.00, "y": 6.36, "w": 9.35, "h": 0.22},
        },
        "composite_visual": {
            "type": "connected_four_stage_banner",
            "style": "hero_academic_progression",
            "panels": [
                {
                    "label": "Point / Vector",
                    "x": 0.98,
                    "y": 3.38,
                    "w": 2.55,
                    "h": 1.66,
                    "mini_visual": "vector_point_plane_combo",
                    "embedded_label": "x=(3,2,2)",
                    "visual_h": 1.08,
                },
                {
                    "label": "Plane / Separator",
                    "x": 3.78,
                    "y": 3.38,
                    "w": 2.55,
                    "h": 1.66,
                    "mini_visual": "plane_slice_with_normal",
                    "embedded_label": "3x₁+x₂−1=0",
                    "visual_h": 1.08,
                },
                {
                    "label": "Loss / Optimization",
                    "x": 6.58,
                    "y": 3.38,
                    "w": 2.55,
                    "h": 1.66,
                    "mini_visual": "loss_curve_with_descent_arrow",
                    "embedded_label": "θ ← θ−γ∇L(θ)",
                    "visual_h": 1.08,
                },
                {
                    "label": "Classifier",
                    "x": 9.38,
                    "y": 3.38,
                    "w": 2.55,
                    "h": 1.66,
                    "mini_visual": "scatter_with_boundary_and_classes",
                    "embedded_label": "h(x)∈{−1,+1}",
                    "visual_h": 1.08,
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
            "A minimal dark academic divider with one wide central visual band, not three tiny isolated visuals."
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
            "subtitle_region": {"x": 1.25, "y": 2.92, "w": 10.5, "h": 0.40},
        },
        "section_visual": {
            "type": "wide_concept_band",
            "style": "minimal_dark_academic",
            "elements": [
                {
                    "kind": "vector_arrow",
                    "x": 1.10,
                    "y": 3.72,
                    "w": 2.80,
                    "h": 1.10,
                    "label": "vector",
                },
                {
                    "kind": "plane_slice",
                    "x": 4.40,
                    "y": 3.68,
                    "w": 2.80,
                    "h": 1.12,
                    "label": "hyperplane",
                },
                {
                    "kind": "scatter_separator",
                    "x": 7.75,
                    "y": 3.68,
                    "w": 3.00,
                    "h": 1.12,
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
            "A clean dependency map with only the four prerequisite nodes and one central ML node."
        ),
        "text_explanation": (
            "Machine learning depends on representation, error measurement, optimization, "
            "uncertainty, and computation."
        ),
        "bullets": [],
        "formulas": ["x ↦ feature vector", "L(θ)", "∇θL(θ)"],
        "concrete_example_anchor": "No tiny icons here anymore.",
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
            "explanation_box": {"x": 8.55, "y": 2.10, "w": 3.35, "h": 1.12},
            "bullets_box": None,
            "takeaway_box": {"x": 1.35, "y": 5.82, "w": 10.50, "h": 0.44},
        },
        "diagram": {
            "type": "hub_and_spokes",
            "style": "large_clean_prereq_map",
            "center_node": {
                "label": "Machine\nLearning",
                "x": 4.00,
                "y": 2.58,
                "w": 2.10,
                "h": 1.02,
                "style": "primary_hub_glow",
                "font_size": 19,
            },
            "input_nodes": [
                {
                    "label": "Linear Algebra /\nGeometry",
                    "x": 1.25,
                    "y": 1.45,
                    "w": 2.30,
                    "h": 0.92,
                    "font_size": 14,
                },
                {
                    "label": "Calculus /\nOptimization",
                    "x": 1.25,
                    "y": 3.90,
                    "w": 2.30,
                    "h": 0.92,
                    "font_size": 14,
                },
                {
                    "label": "Probability /\nUncertainty",
                    "x": 6.55,
                    "y": 1.45,
                    "w": 2.10,
                    "h": 0.92,
                    "font_size": 14,
                },
                {
                    "label": "Computation /\nNumPy",
                    "x": 6.55,
                    "y": 3.90,
                    "w": 2.10,
                    "h": 0.92,
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
        "takeaway": (
            "Representation, error, improvement, uncertainty, and computation all arrive before learning can happen."
        ),
    },
    {
        "kind": "prereq_grid",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 4,
        "slide_title": "What Each Prerequisite Contributes",
        "purpose": "Turn the four prerequisites into large explanatory visuals.",
        "visual": "A 2×2 grid of large visual panels.",
        "text_explanation": "",
        "bullets": [],
        "formulas": [],
        "concrete_example_anchor": (
            "Each panel must be explicit: line/plane → classifier boundary; bowl surface → optimization; "
            "Gaussian curve → uncertainty; array/vector → NumPy execution."
        ),
        "speaker_intent": "These are not side topics. Each one contributes a specific piece of the machinery.",
        "title": "What Each Prerequisite Contributes",
        "subtitle": "",
        "layout": {
            "title_y": 0.42,
            "grid_region": {"x": 0.95, "y": 1.45, "w": 11.10, "h": 4.45},
            "cols": 2,
            "rows": 2,
            "gap_x": 0.42,
            "gap_y": 0.42,
            "takeaway_box": {"x": 1.00, "y": 6.00, "w": 10.90, "h": 0.34},
        },
        "panels": [
            {
                "title": "Linear Algebra / Geometry",
                "mini_visual": "line_to_boundary",
                "caption": "Geometry: represent and separate",
                "formula": "x ∈ R^d",
                "anchor": "line / plane → classifier boundary",
            },
            {
                "title": "Calculus / Optimization",
                "mini_visual": "loss_curve",
                "caption": "Optimization: improve parameters",
                "formula": "∇L(θ)",
                "anchor": "bowl surface → optimization",
            },
            {
                "title": "Probability / Uncertainty",
                "mini_visual": "gaussian_curve",
                "caption": "Probability: model uncertainty",
                "formula": "X ∼ N(μ,σ²)",
                "anchor": "Gaussian curve → uncertainty",
            },
            {
                "title": "Computation / NumPy",
                "mini_visual": "array_glyph",
                "caption": "Computation: make the math executable",
                "formula": "A x",
                "anchor": "array / vector → NumPy execution",
            },
        ],
        "takeaway": "Each prerequisite contributes a distinct part of the machine-learning toolkit.",
    },
    {
        "kind": "pipeline",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 5,
        "slide_title": "The Big Story: From Data to Decisions",
        "purpose": "Give the conceptual storyline of the deck.",
        "visual": "A large horizontal five-stage pipeline.",
        "text_explanation": (
            "Machine learning turns real-world objects into numerical representations, places "
            "them in a geometric space, and learns rules that predict labels or values."
        ),
        "bullets": [],
        "formulas": [
            "raw input → x ∈ R^d → h(x)",
            "h(x)=sign(θ · x+θ₀)",
        ],
        "concrete_example_anchor": "Keep this slide conceptual and large.",
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
        "takeaway": (
            "Representation comes first: objects become vectors, vectors enter geometry, and geometry supports prediction."
        ),
        "layout": {
            "title_y": 0.42,
            "subtitle_y": 0.98,
            "pipeline_region": {"x": 0.82, "y": 1.80, "w": 11.35, "h": 2.35},
            "pipeline_gap": 0.14,
            "takeaway_box": {"x": 1.00, "y": 5.42, "w": 10.90, "h": 0.66},
        },
    },
    {
        "kind": "example_pipeline",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 6,
        "slide_title": "Example A — From Movie to Feature Vector to Label",
        "purpose": "Show one full large running example with enough size to be memorable.",
        "visual": (
            "A large left-to-right pipeline: movie object, 5-feature vector, point in feature space, "
            "scoring rule or boundary, and output like/dislike."
        ),
        "text_explanation": "A real object becomes a machine-readable representation, then a prediction.",
        "bullets": ["object", "encoding", "representation", "prediction"],
        "formulas": [
            "x=[1,0,1,1,0]",
            "h(x)=sign(θ · x+θ₀)",
        ],
        "concrete_example_anchor": "movie → 5-feature vector → like/dislike",
        "speaker_intent": "This is what ‘representation’ means in machine learning.",
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
                    "title": "Representation",
                    "mini_visual": "point_in_space",
                    "caption": "point in feature space",
                },
                {
                    "title": "Model",
                    "mini_visual": "decision_boundary",
                    "caption": "score or boundary",
                    "formula": "h(x)=sign(θ · x+θ₀)",
                },
                {
                    "title": "Output",
                    "mini_visual": "prediction_error",
                    "caption": "like / dislike",
                },
            ]
        },
        "takeaway": "A real object becomes a feature vector before it becomes a prediction.",
    },
    {
        "kind": "example_pipeline",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 7,
        "slide_title": "Example B — From Digit Image to Class Label",
        "purpose": (
            "Show a second full example so the audience sees that the same pipeline applies to different data."
        ),
        "visual": (
            "A large left-to-right pipeline: handwritten digit image, simple feature extraction, "
            "point in low-dimensional space, classifier region/boundary, and output class label."
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
                    "title": "Representation",
                    "mini_visual": "point_in_space",
                    "caption": "point in low-dimensional space",
                },
                {
                    "title": "Classifier",
                    "mini_visual": "decision_boundary",
                    "caption": "class region / boundary",
                },
                {
                    "title": "Output",
                    "mini_visual": "digit_to_label",
                    "caption": "class label",
                    "formula": "h(x)=7",
                },
            ]
        },
        "takeaway": "Different data types still pass through the same representation-first pipeline.",
    },
    {
        "kind": "card_grid",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 8,
        "slide_title": "Running Examples We Will Reuse",
        "purpose": "Introduce the recurring examples once, but with fewer and larger cards.",
        "visual": "A 2×3 grid of large example cards, not 8 tiny cards.",
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
    },
    {
        "kind": "notation_panel",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 9,
        "slide_title": "Notation You Must Read Fluently",
        "purpose": "Clarify notation early so symbols do not feel abstract or intimidating.",
        "visual": "A large three-column notation panel: symbol, meaning, visual example.",
        "text_explanation": (
            "In machine learning, the same letters are reused across different mathematical objects. Context matters."
        ),
        "bullets": [],
        "formulas": [
            "x∈R^d",
            "θ∈R^d",
            "A∈R^{m×n}",
            "y∈{−1,+1}",
        ],
        "concrete_example_anchor": (
            "Large examples on the right: x=(3,2,2), θ·x+θ₀=0, h(x)=sign(θ·x+θ₀)"
        ),
        "speaker_intent": "From here on, notation should feel like compressed meaning, not decoration.",
        "title": "Notation You Must Read Fluently",
        "subtitle": (
            "In machine learning, the same letters are reused across different mathematical objects. Context matters."
        ),
        "columns": ["symbol", "meaning", "visual example"],
        "rows": [
            {"symbol": "x", "meaning": "point / feature vector / example", "example": "x=(3,2,2)"},
            {"symbol": "xᵢ", "meaning": "i-th coordinate", "example": "x₂=2"},
            {"symbol": "θ", "meaning": "parameter vector / normal vector", "example": "θ·x+θ₀=0"},
            {"symbol": "θ₀", "meaning": "offset / intercept", "example": "boundary shift"},
            {"symbol": "A", "meaning": "matrix", "example": "A x"},
            {"symbol": "y", "meaning": "label", "example": "y∈{−1,+1}"},
            {"symbol": "h", "meaning": "classifier / prediction rule", "example": "h(x)=sign(θ·x+θ₀)"},
            {"symbol": "L", "meaning": "loss", "example": "L(θ)"},
        ],
    },
    {
        "kind": "triple_role",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 10,
        "slide_title": "Point, Vector, Feature Vector: Same Shape, Different Role",
        "purpose": "Bridge geometry to ML representation.",
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
    },
    {
        "kind": "integrated_bridge",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 11,
        "slide_title": "One Object, Three Interpretations",
        "purpose": "Give a full visual example slide immediately after Slide 10.",
        "visual": (
            "One large integrated visual with the same coordinate triple, the same arrow, "
            "the same feature-vector table, and annotations explaining the role change."
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
        "takeaway": (
            "The shape of the mathematical object stays the same; only the interpretation changes."
        ),
    },
]
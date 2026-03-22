from __future__ import annotations

from typing import Any


def _merged_layout(base: dict[str, Any], **overrides: Any) -> dict[str, Any]:
    merged = dict(base)
    merged.update(overrides)
    return merged


TITLE_DARK_HERO_STYLE: dict[str, Any] = {
    "preset": "dark_hero",
    "panel_fill_color": "DARK_BOX_FILL",
    "panel_line_color": "TITLE_PANEL_LINE",
    "connector_color": "ACCENT",
}

LONG_HEADER_LAYOUT_GRID: dict[str, Any] = {
    "title_y": 0.42,
    "title_h": 0.88,
    "title_max_lines": 2,
    "title_max_font": 25,
    "subtitle_h": 0.46,
    "subtitle_max_lines": 2,
    "content_to_grid_gap": 0.14,
}

LONG_HEADER_LAYOUT_TABLE: dict[str, Any] = {
    "title_y": 0.42,
    "title_h": 0.88,
    "title_max_lines": 2,
    "title_max_font": 25,
    "subtitle_h": 0.48,
    "subtitle_max_lines": 2,
    "content_to_table_gap": 0.12,
}


PART1_COMPACT_CONCEPT_LAYOUT: dict[str, Any] = {
    "title_y": 0.42,
    "subtitle_y": 0.98,
    "poster_box": {"x": 0.94, "y": 1.32, "w": 11.14, "h": 5.02},
    "poster_profile": "compact_concept",
    "layout_profile": "compact_concept",
    "compact_concept_mode": True,
    "compact_visual_min_share": 0.66,
    "compact_visual_max_share": 0.84,
    "compact_preferred_visual_share": 0.76,
    "visual_min_share": 0.62,
    "visual_max_share": 0.82,
    "preferred_visual_share": 0.72,
}

PART1_TEXT_FORWARD_CONCEPT_LAYOUT: dict[str, Any] = _merged_layout(
    PART1_COMPACT_CONCEPT_LAYOUT,
    poster_profile="text_priority",
    layout_profile="text_priority",
    prioritize_text_over_visual=True,
    reserve_formula_first=True,
    stack_formulas=True,
    visual_min_share=0.48,
    visual_max_share=0.68,
    preferred_visual_share=0.58,
)

PART1_PIPELINE_LAYOUT: dict[str, Any] = {
    "title_y": 0.42,
    "subtitle_y": 0.98,
    "pipeline_region": {"x": 0.78, "y": 1.74, "w": 11.44, "h": 2.82},
    "pipeline_gap": 0.24,
    "takeaway_box": {"x": 0.98, "y": 5.28, "w": 10.96, "h": 0.82},
}

PART1_ANNOTATED_PIPELINE_LAYOUT: dict[str, Any] = {
    "title_y": 0.42,
    "subtitle_y": 0.98,
    "pipeline_region": {"x": 0.78, "y": 1.72, "w": 11.44, "h": 3.08},
    "pipeline_gap": 0.26,
    "bullets_y": 5.06,
    "takeaway_y": 5.54,
}

PART1_MULTI_PANEL_SUMMARY_LAYOUT: dict[str, Any] = {
    "title_y": 0.42,
    "title_h": 0.84,
    "title_max_lines": 2,
    "title_max_font": 25,
    "subtitle_h": 0.40,
    "subtitle_max_lines": 1,
    "panel_region": {"x": 0.82, "y": 1.92, "w": 11.36, "h": 3.06},
    "panel_gap": 0.24,
    "adaptive_panel_visual": True,
    "prioritize_text_over_visual": True,
    "panel_visual_min_share": 0.34,
    "panel_visual_max_share": 0.60,
    "panel_visual_preferred_share": 0.44,
    "bottom_text_gap": 0.10,
    "takeaway_grow_weight": 2.2,
    "use_bottom_summary_card": True,
    "footer_clearance_top": 6.46,
}


ML_FOUNDATIONS_PART1_SLIDES: list[dict[str, Any]] = [
    {
        "kind": "title_composite",
        "theme": "title",
        "background": "Background 8.png",
        "slide_number": 1,
        "slide_title": "Machine Learning Foundations: Geometry, Optimization, and Linear Classification",
        "purpose": (
            "Open the presentation with a strong conceptual bridge. This slide should immediately "
            "communicate that machine learning is built from mathematical objects, geometric "
            "separation, optimization, and prediction."
        ),
        "visual": (
            "A single hero composition in the lower half of the slide showing a point/vector, "
            "a separator, a loss curve with downhill arrow, and a classifier boundary."
        ),
        "text_explanation": "From vectors and planes to loss functions, feature vectors, and classifiers",
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
        "title_style": TITLE_DARK_HERO_STYLE,
        "layout": {
            "title_y": 0.90,
            "subtitle_y": 2.02,
            "author_y": 2.70,
            "visual_region": {"x": 0.82, "y": 3.02, "w": 11.55, "h": 2.48},
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
                    "y": 3.30,
                    "w": 2.62,
                    "h": 1.76,
                    "mini_visual": "vector_point_plane_combo",
                    "embedded_label": "x=(3,2,2)",
                    "visual_h": 1.16,
                },
                {
                    "label": "Plane / Separator",
                    "x": 3.82,
                    "y": 3.30,
                    "w": 2.62,
                    "h": 1.76,
                    "mini_visual": "plane_slice_with_normal",
                    "embedded_label": "3x₁+x₂−1=0",
                    "visual_h": 1.16,
                },
                {
                    "label": "Loss / Optimization",
                    "x": 6.69,
                    "y": 3.30,
                    "w": 2.62,
                    "h": 1.76,
                    "mini_visual": "loss_curve_with_descent_arrow",
                    "embedded_label": "θ ← θ−γ∇L(θ)",
                    "visual_h": 1.16,
                },
                {
                    "label": "Classifier",
                    "x": 9.56,
                    "y": 3.30,
                    "w": 2.62,
                    "h": 1.76,
                    "mini_visual": "scatter_with_boundary_and_classes",
                    "embedded_label": "h(x)∈{−1,+1}",
                    "visual_h": 1.16,
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
        "purpose": "Mark the start of the first section clearly. This should feel like a section divider and a visual reset.",
        "visual": (
            "A dark academic divider with one wide central visual band including a vector arrow, "
            "a plane slice, and a scatterplot with a separator."
        ),
        "text_explanation": "How the course’s mathematical language becomes machine learning language",
        "bullets": [],
        "formulas": [],
        "concrete_example_anchor": "Faint background words only: vector, hyperplane, training set, classifier",
        "speaker_intent": "In this part we establish the vocabulary and the map of the deck.",
        "title": "Part I — Framing, Notation, and Roadmap",
        "subtitle": "How the course’s mathematical language becomes machine learning language",
        "layout": {
            "title_region": {"x": 1.0, "y": 1.96, "w": 11.0, "h": 0.90},
            "subtitle_region": {"x": 1.20, "y": 2.88, "w": 10.6, "h": 0.40},
        },
        "section_visual": {
            "type": "wide_concept_band",
            "style": "minimal_dark_academic",
            "elements": [
                {
                    "kind": "vector_arrow",
                    "x": 1.00,
                    "y": 3.68,
                    "w": 3.00,
                    "h": 1.16,
                    "label": "vector",
                },
                {
                    "kind": "plane_slice",
                    "x": 4.35,
                    "y": 3.66,
                    "w": 3.00,
                    "h": 1.18,
                    "label": "hyperplane",
                },
                {
                    "kind": "scatter_separator",
                    "x": 7.80,
                    "y": 3.66,
                    "w": 3.15,
                    "h": 1.18,
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
        "visual": "A clean dependency map with four prerequisite nodes and one central Machine Learning node.",
        "text_explanation": (
            "Machine learning depends on representation, error measurement, optimization, uncertainty, and computation."
        ),
        "bullets": [],
        "formulas": ["x ↦ feature vector", "L(θ)", "∇θL(θ)"],
        "concrete_example_anchor": "No icons or mini examples on this slide. Keep it conceptually clean.",
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
            "explanation_box": {"x": 8.55, "y": 2.05, "w": 3.35, "h": 1.18},
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
                "h": 1.06,
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
        "kind": "concept_poster",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 4,
        "slide_title": "Geometry Gives Us Representation",
        "purpose": "Make the contribution of geometry large, concrete, and visually obvious.",
        "title": "Geometry Gives Us Representation",
        "subtitle": "",
        "mini_visual": "line_to_boundary",
        "text_explanation": (
            "Geometry lets us place examples in space, compare directions, and define boundaries."
        ),
        "bullets": [
            "vectors represent objects",
            "space gives structure",
            "boundaries separate regions",
        ],
        "formulas": [
            "x ∈ R^d",
            "θ · x + θ₀ = 0",
        ],
        "concrete_example_anchor": "point/vector x=(3,2,2) and boundary 3x₁+x₂−1=0",
        "takeaway": "Without geometry, there is no meaningful space in which learning can happen.",
        "layout": _merged_layout(PART1_COMPACT_CONCEPT_LAYOUT, compact_preferred_visual_share=0.79),
    },
    {
        "kind": "concept_poster",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 5,
        "slide_title": "Optimization Improves Parameters",
        "purpose": "Make the contribution of optimization large and intuitive.",
        "title": "Optimization Improves Parameters",
        "subtitle": "",
        "mini_visual": "loss_curve_with_descent_arrow",
        "text_explanation": (
            "Optimization gives us a rule for improving parameters by moving toward lower loss."
        ),
        "bullets": [
            "error becomes a function",
            "lower is better",
            "updates move downhill",
        ],
        "formulas": [
            "L(θ)",
            "θ ← θ − γ∇L(θ)",
        ],
        "concrete_example_anchor": "Use a visible bowl surface or 1D loss curve.",
        "takeaway": "Optimization is how a model changes from a bad fit into a better fit.",
        "layout": _merged_layout(PART1_COMPACT_CONCEPT_LAYOUT, compact_preferred_visual_share=0.77),
    },
    {
        "kind": "concept_poster",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 6,
        "slide_title": "Probability Models Uncertainty",
        "purpose": "Explain that not everything in machine learning is exact or deterministic.",
        "title": "Probability Models Uncertainty",
        "subtitle": "",
        "mini_visual": "gaussian_curve",
        "text_explanation": (
            "Probability lets us describe uncertainty, variability, and noisy data."
        ),
        "bullets": [
            "outcomes can vary",
            "uncertainty can be modeled",
            "ML must reason under uncertainty",
        ],
        "formulas": [
            "X ∼ N(μ,σ²)",
        ],
        "concrete_example_anchor": "Use one Gaussian with clear mean and spread.",
        "takeaway": "Real data is not perfectly clean, so machine learning must reason probabilistically.",
        "layout": _merged_layout(PART1_COMPACT_CONCEPT_LAYOUT, compact_preferred_visual_share=0.76),
    },
    {
        "kind": "concept_poster",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 7,
        "slide_title": "Computation Makes the Math Executable",
        "purpose": "Explain the role of computation as the bridge between mathematical ideas and real model-building.",
        "title": "Computation Makes the Math Executable",
        "subtitle": "",
        "mini_visual": "array_glyph",
        "text_explanation": (
            "Computation turns the math into something we can evaluate, repeat, and optimize."
        ),
        "bullets": [
            "vectors become arrays",
            "formulas become code",
            "repeated updates become algorithms",
        ],
        "formulas": [
            "A x",
        ],
        "concrete_example_anchor": "Use a clear matrix-vector visual or array layout.",
        "takeaway": "Without computation, the formulas stay on paper.",
        "layout": _merged_layout(PART1_TEXT_FORWARD_CONCEPT_LAYOUT, compact_preferred_visual_share=0.68),
    },
    {
        "kind": "pipeline",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 8,
        "slide_title": "The Big Story: From Data to Decisions",
        "purpose": "Give the full conceptual storyline of the deck.",
        "visual": "A large four-stage conceptual pipeline.",
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
                    "footer": "real-world input",
                },
                {
                    "title": "Feature Vector",
                    "mini_visual": "feature_vector_pair",
                    "body": "",
                    "footer": "machine-readable x",
                },
                {
                    "title": "Geometry / Model",
                    "mini_visual": "decision_boundary",
                    "body": "",
                    "footer": "space + boundary",
                },
                {
                    "title": "Prediction",
                    "mini_visual": "prediction_error",
                    "body": "",
                    "footer": "label / error",
                },
            ]
        },
        "examples": [],
        "takeaway": "Representation comes first: objects become vectors, vectors enter geometry, and geometry supports prediction.",
        "layout": PART1_PIPELINE_LAYOUT,
    },
    {
        "kind": "annotated_pipeline",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 9,
        "slide_title": "Example A — From Movie Object to Feature Vector",
        "purpose": "Show the first half of a memorable representation example.",
        "visual": "A three-stage storyboard from movie object to encoded properties to a feature vector.",
        "text_explanation": "A real object becomes a machine-readable representation.",
        "bullets": ["object", "encoding", "vector"],
        "formulas": ["x=[1,0,1,1,0]"],
        "concrete_example_anchor": "movie → encoded properties → 5-feature vector",
        "speaker_intent": "The first step in machine learning is to turn an object into numbers.",
        "title": "Example A — From Movie Object to Feature Vector",
        "subtitle": "A real object becomes a machine-readable representation.",
        "example_pipeline": {
            "stages": [
                {
                    "title": "Movie",
                    "mini_visual": "movie_card",
                    "caption": "raw object / metadata",
                },
                {
                    "title": "Encoding",
                    "mini_visual": "movie_to_vector",
                    "caption": "choose measurable properties",
                },
                {
                    "title": "Feature Vector",
                    "mini_visual": "feature_vector_pair",
                    "caption": "machine-readable x",
                    "formula": "x=[1,0,1,1,0]",
                },
            ]
        },
        "takeaway": "Representation means converting a real object into a vector that a model can use.",
        "layout": PART1_ANNOTATED_PIPELINE_LAYOUT,
    },
    {
        "kind": "annotated_pipeline",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 10,
        "slide_title": "Example A — From Feature Vector to Prediction",
        "purpose": "Show the second half of the movie example: vector to geometric model to decision.",
        "visual": "A three-stage storyboard from feature vector to point in space to prediction.",
        "text_explanation": "Once represented numerically, the object can enter a geometric model and produce a prediction.",
        "bullets": ["vector", "space", "prediction"],
        "formulas": ["h(x)=sign(θ · x+θ₀)"],
        "concrete_example_anchor": "5-feature vector → point in feature space → like/dislike",
        "speaker_intent": "After representation, the model can score the vector and make a decision.",
        "title": "Example A — From Feature Vector to Prediction",
        "subtitle": "Once represented numerically, the object can enter a geometric model and produce a prediction.",
        "example_pipeline": {
            "stages": [
                {
                    "title": "Vector x",
                    "mini_visual": "feature_vector_pair",
                    "caption": "input to the model",
                },
                {
                    "title": "Geometric Space",
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
        "takeaway": "A prediction is made only after the object has been turned into a vector.",
        "layout": PART1_ANNOTATED_PIPELINE_LAYOUT,
    },
    {
        "kind": "annotated_pipeline",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 11,
        "slide_title": "Example B — From Digit Image to Features",
        "purpose": "Show the first half of the digit example: image to numerical features.",
        "visual": "A three-stage storyboard from digit image to simple measurements to feature vector.",
        "text_explanation": "A handwritten image can also be converted into a numerical representation.",
        "bullets": ["image", "measurement", "vector"],
        "formulas": ["x=[brightness,width]"],
        "concrete_example_anchor": "digit → brightness/width features → vector",
        "speaker_intent": "Different kinds of raw objects can still become feature vectors.",
        "title": "Example B — From Digit Image to Features",
        "subtitle": "A handwritten image can also be converted into a numerical representation.",
        "example_pipeline": {
            "stages": [
                {
                    "title": "Digit Image",
                    "mini_visual": "digit_card",
                    "caption": "raw handwritten input",
                },
                {
                    "title": "Measured Features",
                    "mini_visual": "feature_vector_pair",
                    "caption": "brightness / width",
                },
                {
                    "title": "Vector x",
                    "mini_visual": "feature_vector_pair",
                    "caption": "numeric representation",
                    "formula": "x=[brightness,width]",
                },
            ]
        },
        "takeaway": "The same representation idea works for images too.",
        "layout": PART1_ANNOTATED_PIPELINE_LAYOUT,
    },
    {
        "kind": "annotated_pipeline",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 12,
        "slide_title": "Example B — From Features to Class Label",
        "purpose": "Show the second half of the digit example: features to geometric classification.",
        "visual": "A three-stage storyboard from feature vector to class region to output label.",
        "text_explanation": "Once represented numerically, the image can be placed in space and classified.",
        "bullets": ["vector", "boundary", "class"],
        "formulas": ["h(x)=7"],
        "concrete_example_anchor": "features → point in low-dimensional space → class label",
        "speaker_intent": "The raw object changes, but the mathematical pipeline stays the same.",
        "title": "Example B — From Features to Class Label",
        "subtitle": "Once represented numerically, the image can be placed in space and classified.",
        "example_pipeline": {
            "stages": [
                {
                    "title": "Vector x",
                    "mini_visual": "feature_vector_pair",
                    "caption": "numeric input to the model",
                },
                {
                    "title": "Class Regions",
                    "mini_visual": "decision_boundary",
                    "caption": "boundary / regions in space",
                },
                {
                    "title": "Output Label",
                    "mini_visual": "digit_to_label",
                    "caption": "predicted class",
                    "formula": "h(x)=7",
                },
            ]
        },
        "takeaway": "A class prediction is made after the image becomes a vector in a geometric space.",
        "layout": PART1_ANNOTATED_PIPELINE_LAYOUT,
    },
    {
        "kind": "card_grid",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 13,
        "slide_title": "Running Examples We Will Reuse — Geometry and Optimization",
        "purpose": "Introduce the first set of recurring anchor examples in a sparse, readable way.",
        "visual": "A 1×3 grid of large anchor cards.",
        "text_explanation": "These examples will return throughout the deck as anchors.",
        "bullets": [],
        "formulas": [],
        "concrete_example_anchor": "This slide itself is the anchor slide.",
        "speaker_intent": "These are the examples that will keep the course connected.",
        "title": "Running Examples We Will Reuse — Geometry and Optimization",
        "subtitle": "These examples will return throughout the deck as anchors.",
        "grid": {
            "rows": 1,
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
            ],
        },
        "takeaway": "geometry and optimization examples we will reuse often",
        "layout": _merged_layout(
            LONG_HEADER_LAYOUT_GRID,
            grid_x=0.90,
            grid_y=1.96,
            grid_w=11.20,
            grid_h=3.72,
            gap_x=0.28,
            gap_y=0.0,
            takeaway_y=5.98,
        ),
    },
    {
        "kind": "card_grid",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 14,
        "slide_title": "Running Examples We Will Reuse — Probability, Computation, and Supervised Learning",
        "purpose": "Introduce the second set of recurring anchor examples in a sparse, readable way.",
        "visual": "A 1×3 grid of large anchor cards.",
        "text_explanation": "These examples will return throughout the deck as anchors.",
        "bullets": [],
        "formulas": [],
        "concrete_example_anchor": "This slide itself is the anchor slide.",
        "speaker_intent": "These examples connect uncertainty, computation, and supervised learning.",
        "title": "Running Examples We Will Reuse — Probability, Computation, and Supervised Learning",
        "subtitle": "These examples will return throughout the deck as anchors.",
        "grid": {
            "rows": 1,
            "cols": 3,
            "cards": [
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
            ],
        },
        "takeaway": "probability, computation, and supervised-learning anchors",
        "layout": _merged_layout(
            LONG_HEADER_LAYOUT_GRID,
            grid_x=0.90,
            grid_y=1.98,
            grid_w=11.20,
            grid_h=3.70,
            gap_x=0.28,
            gap_y=0.0,
            takeaway_y=5.98,
        ),
    },
    {
        "kind": "notation_panel",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 15,
        "slide_title": "Notation You Must Read Fluently — Objects and Coordinates",
        "purpose": "Clarify notation without overwhelming the audience.",
        "visual": "A three-column notation panel with four entries.",
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
        "layout": _merged_layout(
            LONG_HEADER_LAYOUT_TABLE,
            table_x=0.88,
            table_y=1.98,
            table_w=11.20,
            table_h=4.40,
            formula_y=6.55,
        ),
    },
    {
        "kind": "notation_panel",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 16,
        "slide_title": "Notation You Must Read Fluently — Parameters, Classifiers, and Loss",
        "purpose": "Continue notation in a readable way.",
        "visual": "A three-column notation panel with four entries.",
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
        "layout": _merged_layout(
            LONG_HEADER_LAYOUT_TABLE,
            table_x=0.88,
            table_y=1.98,
            table_w=11.20,
            table_h=4.40,
            formula_y=6.55,
        ),
    },
    {
        "kind": "multi_panel_summary",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 17,
        "slide_title": "Point, Vector, Feature Vector: Same Shape, Different Role",
        "purpose": "Bridge geometry to machine-learning representation in one unified slide.",
        "visual": (
            "Three large side-by-side panels using the same object: point in coordinate space, "
            "arrow from origin, and feature vector representing an example."
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
            "The coordinates did not change. The interpretation changed."
        ),
        "title": "Point, Vector, Feature Vector: Same Shape, Different Role",
        "subtitle": "The coordinates did not change. The interpretation changed.",
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
        "takeaway": "same coordinates • different role • context changes meaning",
        "layout": _merged_layout(
            PART1_MULTI_PANEL_SUMMARY_LAYOUT,
            panel_region={"x": 0.82, "y": 1.92, "w": 11.36, "h": 3.02},
        ),
    },
]
from __future__ import annotations

from typing import Any


def _merged_layout(base: dict[str, Any], **overrides: Any) -> dict[str, Any]:
    merged = dict(base)
    merged.update(overrides)
    return merged


PART2_POSTER_LAYOUT: dict[str, Any] = {
    "title_y": 0.42,
    "subtitle_y": 0.98,
    "poster_box": {"x": 0.96, "y": 1.34, "w": 11.10, "h": 4.98},
    "visual_min_share": 0.56,
    "visual_max_share": 0.76,
    "preferred_visual_share": 0.63,
}

PART2_TEXT_FIRST_POSTER_LAYOUT: dict[str, Any] = _merged_layout(
    PART2_POSTER_LAYOUT,
    prioritize_text_over_visual=True,
    reserve_formula_first=True,
    stack_formulas=True,
    visual_min_share=0.44,
    visual_max_share=0.64,
    preferred_visual_share=0.52,
)

PART2_WORKED_EXAMPLE_LAYOUT: dict[str, Any] = {
    "content_box": {"x": 0.88, "y": 1.34, "w": 11.24, "h": 5.02},
    "worked_layout_mode": "two_column",
    "column_gap": 0.24,
    "visual_share": 0.40,
    "block_gap": 0.12,
    "steps_min_h": 2.10,
    "result_min_h": 0.72,
    "takeaway_min_h": 0.56,
}

PART2_DENSE_WORKED_EXAMPLE_LAYOUT: dict[str, Any] = {
    "content_box": {"x": 0.88, "y": 1.32, "w": 11.24, "h": 5.06},
    "worked_layout_mode": "top_visual",
    "top_visual_h": 2.12,
    "column_gap": 0.22,
    "lower_right_share": 0.34,
    "block_gap": 0.12,
    "result_min_h": 0.86,
    "result_max_h": 1.30,
    "takeaway_min_h": 0.92,
}

PART2_NOTATION_LAYOUT: dict[str, Any] = {
    "title_y": 0.42,
    "title_h": 0.88,
    "title_max_lines": 2,
    "title_max_font": 25,
    "subtitle_h": 0.46,
    "subtitle_max_lines": 2,
    "content_to_table_gap": 0.12,
    "table_x": 0.88,
    "table_y": 1.98,
    "table_w": 11.20,
    "table_h": 4.26,
    "formula_y": 6.46,
    "example_max_lines": 2,
}

PART2_TWO_PANEL_LAYOUT: dict[str, Any] = {
    "title_y": 0.42,
    "title_h": 0.84,
    "title_max_lines": 2,
    "title_max_font": 25,
    "subtitle_h": 0.40,
    "subtitle_max_lines": 1,
    "panel_region": {"x": 0.88, "y": 1.96, "w": 11.24, "h": 2.92},
    "panel_gap": 0.28,
    "footer_clearance_top": 6.50,
    "takeaway_min_font": 13,
    "takeaway_max_font": 14,
}

PART2_THREE_PANEL_LAYOUT: dict[str, Any] = {
    "title_y": 0.42,
    "title_h": 0.84,
    "title_max_lines": 2,
    "title_max_font": 25,
    "subtitle_h": 0.42,
    "subtitle_max_lines": 2,
    "panel_region": {"x": 0.88, "y": 1.98, "w": 11.24, "h": 2.88},
    "panel_gap": 0.24,
    "footer_clearance_top": 6.46,
    "bottom_text_gap": 0.12,
    "takeaway_min_font": 13,
    "takeaway_max_font": 14,
    "adaptive_panel_visual": True,
    "prioritize_text_over_visual": True,
    "panel_visual_min_share": 0.30,
    "panel_visual_max_share": 0.58,
    "panel_visual_preferred_share": 0.40,
    "takeaway_grow_weight": 2.2,
    "use_bottom_summary_card": True,
}


ML_FOUNDATIONS_PART2_SLIDES: list[dict[str, Any]] = [
    {
        "kind": "section_divider",
        "theme": "section",
        "background": "Background 9.png",
        "slide_number": 12,
        "slide_title": "Part II — Points, Vectors, Norms, Dot Products, and Projections",
        "purpose": "Mark the beginning of the geometric foundations section.",
        "visual": (
            "A large unified geometry composition with a coordinate frame, one vector, "
            "a second vector with angle marked, and a projection shadow."
        ),
        "text_explanation": (
            "The geometric language used to represent examples, compare directions, "
            "and measure similarity"
        ),
        "bullets": [],
        "formulas": [],
        "concrete_example_anchor": "Tiny embedded labels only: x=(3,2,2), y=(1,1,1)",
        "speaker_intent": "This is where the geometry starts becoming operational.",
        "title": "Part II — Points, Vectors, Norms, Dot Products, and Projections",
        "subtitle": (
            "The geometric language used to represent examples, compare directions, "
            "and measure similarity"
        ),
        "layout": {
            "title_region": {"x": 0.92, "y": 1.76, "w": 11.40, "h": 1.02},
            "subtitle_region": {"x": 1.14, "y": 2.82, "w": 10.96, "h": 0.42},
        },
        "section_visual": {
            "type": "wide_concept_band",
            "style": "minimal_dark_academic",
            "elements": [
                {
                    "kind": "point_vector_projection_hero",
                    "x": 1.20,
                    "y": 3.34,
                    "w": 9.90,
                    "h": 1.86,
                    "label": "",
                },
            ],
        },
    },
    {
        "kind": "concept_poster",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 13,
        "slide_title": "Point in Space, Vector from the Origin",
        "purpose": (
            "Introduce the key idea that the same coordinates can be viewed both as a "
            "point and as a vector."
        ),
        "title": "Point in Space, Vector from the Origin",
        "subtitle": "",
        "mini_visual": "point_and_vector_same_coords",
        "text_explanation": (
            "The same coordinates can be interpreted in two ways: as a location in "
            "space and as a displacement from the origin."
        ),
        "bullets": [
            "point view: where the object is",
            "vector view: how far and in what direction from the origin",
            "same coordinates, different interpretation",
        ],
        "formulas": [
            "x=(3,2,2)",
            "x∈R^3",
        ],
        "required_formulas": True,
        "concrete_example_anchor": "Use x=(3,2,2) as both point and vector.",
        "takeaway": (
            "This is the first bridge between geometry language and machine-learning "
            "representation."
        ),
        "layout": PART2_POSTER_LAYOUT,
    },
    {
        "kind": "triple_role",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 14,
        "slide_title": "One Set of Coordinates, Two Interpretations",
        "purpose": "Give students a dedicated visual example slide right after the definition slide.",
        "visual": "A two-panel comparison using the same coordinates as a point and as a vector.",
        "text_explanation": "Nothing numerical changed. Only the interpretation changed.",
        "bullets": [],
        "formulas": [],
        "concrete_example_anchor": "point x and vector x",
        "speaker_intent": "The distinction is conceptual, not algebraic.",
        "title": "One Set of Coordinates, Two Interpretations",
        "subtitle": "Nothing numerical changed. Only the interpretation changed.",
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
                "caption": "displacement from the origin",
                "formula": "x=(3,2,2)",
            },
        ],
        "takeaway": "Same coordinates. Different role.",
        "layout": _merged_layout(
            PART2_TWO_PANEL_LAYOUT,
            panel_region={"x": 0.88, "y": 1.94, "w": 11.24, "h": 3.06},
        ),
    },
    {
        "kind": "notation_panel",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 15,
        "slide_title": "Coordinates and the Meaning of x_i",
        "purpose": (
            "Explain vector notation and indexing clearly enough that later sums and "
            "dot products feel natural."
        ),
        "visual": (
            "A large notation comparison with coordinate-list form, column-vector form, "
            "and indexed coordinate meaning."
        ),
        "text_explanation": (
            "A vector is made of coordinates, and x_i means the i-th coordinate of the vector."
        ),
        "bullets": [],
        "formulas": [
            "x=[x_1,x_2,x_3]ᵀ",
            "x=(3,2,2) ⇒ x_1=3, x_2=2, x_3=2",
        ],
        "concrete_example_anchor": "Explicitly highlight x_2=2.",
        "speaker_intent": "Index notation is how vector formulas become manageable.",
        "title": "Coordinates and the Meaning of x_i",
        "subtitle": (
            "A vector is made of coordinates, and x_i means the i-th coordinate of the vector."
        ),
        "columns": ["symbol", "meaning", "visual example"],
        "rows": [
            {"symbol": "x", "meaning": "the full vector", "example": "x=(3,2,2)"},
            {"symbol": "[x_1,x_2,x_3]ᵀ", "meaning": "column-vector notation", "example": "[3,2,2]ᵀ"},
            {"symbol": "x_i", "meaning": "the i-th coordinate", "example": "x_2=2"},
            {"symbol": "x_1,x_2,x_3", "meaning": "coordinate-by-coordinate view", "example": "3,2,2"},
        ],
        "layout": PART2_NOTATION_LAYOUT,
    },
    {
        "kind": "concept_poster",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 16,
        "slide_title": "Vector Difference as Displacement",
        "purpose": "Show that subtraction gives the vector from one point/vector to another.",
        "title": "Vector Difference as Displacement",
        "subtitle": "",
        "mini_visual": "vector_difference_geometry",
        "text_explanation": (
            "If A and B start at the origin, then the vector from A to B is their difference."
        ),
        "bullets": [
            "“from A to B” means subtract",
            "displacement is directional",
            "subtraction is geometric",
        ],
        "formulas": [
            "A + C = B",
            "C = B − A",
        ],
        "required_formulas": True,
        "concrete_example_anchor": "Use generic labeled geometry with A, B, C.",
        "takeaway": "Subtraction tells us how to move from one vector to another.",
        "layout": PART2_POSTER_LAYOUT,
    },
    {
        "kind": "worked_example",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 17,
        "slide_title": "Worked Example: From One Point to Another",
        "purpose": "Turn vector subtraction into a concrete geometric example.",
        "title": "Worked Example: From One Point to Another",
        "mini_visual": "displacement_worked_example",
        "visual_label": "Geometry",
        "visual_caption": "Displacement vector from A to B",
        "text_explanation": "To go from A to B, subtract coordinates entry by entry.",
        "steps": [
            {
                "title": "Step 1",
                "body": "Write the starting and ending points.",
                "formula": "A=(1,1), B=(4,3)",
            },
            {
                "title": "Step 2",
                "body": "Use ending minus starting point.",
                "formula": "C = B − A",
            },
            {
                "title": "Step 3",
                "body": "Subtract coordinate-wise.",
                "formula": "C=(4,3)−(1,1)=(3,2)",
            },
        ],
        "result": {
            "label": "Result",
            "body": "The displacement from A to B is the vector from the first point to the second.",
            "formula": "C=(3,2)",
        },
        "takeaway": (
            "This same subtraction pattern returns later in optimization, gradients, and "
            "error vectors."
        ),
        "layout": PART2_WORKED_EXAMPLE_LAYOUT,
    },
    {
        "kind": "concept_poster",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 18,
        "slide_title": "Norm = Length of a Vector",
        "purpose": "Introduce Euclidean norm as the standard way to measure vector size.",
        "title": "Norm = Length of a Vector",
        "subtitle": "",
        "mini_visual": "norm_triangle",
        "text_explanation": (
            "The norm tells us how long a vector is. In Euclidean space, length comes "
            "from summing squared coordinates and taking a square root."
        ),
        "bullets": [
            "norm = magnitude",
            "Euclidean norm is the default here",
            "same idea as distance from the origin",
        ],
        "formulas": [
            "‖x‖ = √(x_1^2 + x_2^2 + ⋯ + x_n^2)",
            "‖x‖ = √(Σ_{i=1}^n x_i^2)",
        ],
        "required_formulas": True,
        "concrete_example_anchor": "General n-dimensional vector.",
        "takeaway": "This is the first standard measurement tool for vectors.",
        "layout": PART2_POSTER_LAYOUT,
    },
    {
        "kind": "worked_example",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 19,
        "slide_title": "Worked Example: ‖(3,2,2)‖",
        "purpose": "Compute a concrete norm fully, step by step.",
        "title": "Worked Example: ‖(3,2,2)‖",
        "mini_visual": "norm_worked_geometry",
        "visual_label": "Geometry",
        "visual_caption": "The vector x=(3,2,2) with length measured from the origin",
        "text_explanation": "Square each coordinate, add the squares, then take the square root.",
        "steps": [
            {
                "title": "Step 1",
                "body": "Start from the coordinates of the vector.",
                "formula": "x=(3,2,2)",
            },
            {
                "title": "Step 2",
                "body": "Apply the Euclidean norm formula.",
                "formula": "‖x‖ = √(3^2 + 2^2 + 2^2)",
            },
            {
                "title": "Step 3",
                "body": "Add the squares under the root.",
                "formula": "‖x‖ = √(9+4+4) = √17",
            },
        ],
        "result": {
            "label": "Result",
            "formula": "‖(3,2,2)‖ = √17",
        },
        "takeaway": "Students should be able to repeat this exact norm pattern on their own.",
        "layout": PART2_WORKED_EXAMPLE_LAYOUT,
    },
    {
        "kind": "concept_poster",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 20,
        "slide_title": "Dot Product as Coordinate-by-Coordinate Multiplication",
        "purpose": "Define the dot product algebraically.",
        "title": "Dot Product as Coordinate-by-Coordinate Multiplication",
        "subtitle": "",
        "mini_visual": "dot_product_pairing",
        "text_explanation": (
            "The dot product combines two vectors into one number. Algebraically, it is "
            "the sum of coordinate-wise products."
        ),
        "bullets": [
            "multiply corresponding coordinates",
            "add the results",
            "output is a scalar",
        ],
        "formulas": [
            "x·y = Σ_{i=1}^n x_i y_i",
            "x·y = x_1y_1 + x_2y_2 + ⋯ + x_ny_n",
        ],
        "required_formulas": True,
        "concrete_example_anchor": "Generic x,y∈R^n.",
        "takeaway": "Dot product is one of the central operations in all of machine learning.",
        "layout": PART2_POSTER_LAYOUT,
    },
    {
        "kind": "worked_example",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 21,
        "slide_title": "Worked Example: (3,2,2)·(1,1,1)",
        "purpose": "Carry out a full numerical dot-product computation.",
        "title": "Worked Example: (3,2,2)·(1,1,1)",
        "mini_visual": "dot_product_worked_geometry",
        "visual_label": "Geometry",
        "visual_caption": "Coordinate pairing between x and y",
        "text_explanation": "Dot product is often easiest to compute directly from coordinates.",
        "steps": [
            {
                "title": "Step 1",
                "body": "Write the two vectors.",
                "formula": "x=(3,2,2), y=(1,1,1)",
            },
            {
                "title": "Step 2",
                "body": "Multiply matching coordinates.",
                "formula": "x·y = 3·1 + 2·1 + 2·1",
            },
            {
                "title": "Step 3",
                "body": "Add the coordinate products.",
                "formula": "x·y = 7",
            },
        ],
        "result": {
            "label": "Result",
            "formula": "(3,2,2)·(1,1,1)=7",
        },
        "takeaway": "This is the fast mechanical computation students should be able to do reliably.",
        "layout": PART2_WORKED_EXAMPLE_LAYOUT,
    },
    {
        "kind": "concept_poster",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 22,
        "slide_title": "Dot Product as Angle and Alignment",
        "purpose": (
            "Show the geometric meaning of the dot product and connect it to relative orientation."
        ),
        "title": "Dot Product as Angle and Alignment",
        "subtitle": "",
        "mini_visual": "dot_alignment_angle",
        "text_explanation": (
            "Geometrically, dot product measures alignment. It depends on both length "
            "and angle."
        ),
        "bullets": [
            "large positive: similar direction",
            "zero: perpendicular",
            "negative: opposite tendency",
        ],
        "formulas": [
            "x·y = ‖x‖ ‖y‖ cos α",
        ],
        "required_formulas": True,
        "concrete_example_anchor": "Generic angle diagram with α.",
        "takeaway": "This is where the algebra starts to acquire geometric meaning.",
        "layout": PART2_POSTER_LAYOUT,
    },
    {
        "kind": "concept_poster",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 23,
        "slide_title": "Using the Dot Product to Find an Angle",
        "purpose": "Combine the algebraic and geometric definitions to compute an angle.",
        "title": "Using the Dot Product to Find an Angle",
        "subtitle": "",
        "mini_visual": "angle_recovery_geometry",
        "text_explanation": "If we know the dot product and the norms, we can recover the angle.",
        "bullets": [
            "compute x·y",
            "compute ‖x‖ and ‖y‖",
            "solve for cos α",
        ],
        "formulas": [
            "cos α = (x·y)/(‖x‖‖y‖)",
            "α = arccos((x·y)/(‖x‖‖y‖))",
        ],
        "required_formulas": True,
        "concrete_example_anchor": "Use x=[0.4,0.3]ᵀ and y=[−0.15,0.2]ᵀ.",
        "takeaway": "This is the bridge from arithmetic to geometric interpretation.",
        "layout": PART2_TEXT_FIRST_POSTER_LAYOUT,
    },
    {
        "kind": "worked_example",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 24,
        "slide_title": "Worked Example: Norms and Angle in 2D",
        "purpose": "Give a full worked example close to the homework.",
        "title": "Worked Example: Norms and Angle in 2D",
        "mini_visual": "angle_homework_geometry",
        "visual_label": "Geometry",
        "visual_caption": "Two vectors in 2D whose angle will turn out to be 90°",
        "steps": [
            {
                "title": "Step 1",
                "body": "Compute each norm.",
                "formula": "‖x‖ = 0.5, ‖y‖ = 0.25",
            },
            {
                "title": "Step 2",
                "body": "Compute the dot product.",
                "formula": "x·y = (0.4)(−0.15) + (0.3)(0.2) = 0",
            },
            {
                "title": "Step 3",
                "body": "Recover the angle from the geometric dot-product formula.",
                "formula": "cos α = 0/(0.5·0.25) = 0 ⇒ α = π/2",
            },
        ],
        "result": {
            "label": "Result",
            "body": "The vectors are orthogonal because the dot product vanishes.",
            "formula": "α = π/2",
        },
        "takeaway": "Norm, dot product, angle, and geometry now work together in one computation.",
        "layout": PART2_DENSE_WORKED_EXAMPLE_LAYOUT,
    },
    {
        "kind": "worked_example",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 25,
        "slide_title": "Orthogonal Vectors",
        "purpose": (
            "Define perpendicularity in vector language and connect it directly to the dot product."
        ),
        "title": "Orthogonal Vectors",
        "mini_visual": "orthogonal_vectors_geometry",
        "visual_label": "Geometry",
        "visual_caption": "Perpendicular vectors with the dot product criterion shown separately as text",
        "steps": [
            {
                "title": "Criterion",
                "body": "Orthogonal means perpendicular in vector language.",
                "formula": "x ⟂ y ⟺ x·y = 0",
            },
            {
                "title": "Homework pair",
                "body": "For the symbolic vectors from the homework, compute the dot product.",
                "formula": "x^(1)·x^(2) = a_1^2 − a_2^2 + a_3^2",
            },
            {
                "title": "Test",
                "body": "Set the dot product equal to zero to enforce orthogonality.",
                "formula": "a_1^2 − a_2^2 + a_3^2 = 0",
            },
        ],
        "result": {
            "label": "Result",
            "formula": "x^(1) ⟂ x^(2) ⟺ a_1^2 − a_2^2 + a_3^2 = 0",
        },
        "takeaway": "Perpendicularity becomes a direct algebraic test instead of a purely visual fact.",
        "layout": PART2_DENSE_WORKED_EXAMPLE_LAYOUT,
    },
    {
        "kind": "concept_poster",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 26,
        "slide_title": "Unit Vector = Direction Only",
        "purpose": "Explain normalization and why it matters.",
        "title": "Unit Vector = Direction Only",
        "subtitle": "",
        "mini_visual": "unit_vector_normalization",
        "text_explanation": "A unit vector keeps direction but removes scale.",
        "bullets": [
            "same direction",
            "norm equal to 1",
            "divide by original norm",
        ],
        "formulas": [
            "u = x / ‖x‖",
            "x=(3,2,2) ⇒ u=(1/√17)(3,2,2)",
        ],
        "required_formulas": True,
        "concrete_example_anchor": "Generic x, plus optional x=(3,2,2).",
        "takeaway": "This is how we isolate pure direction.",
        "layout": PART2_POSTER_LAYOUT,
    },
    {
        "kind": "concept_poster",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 27,
        "slide_title": "Projection = How Much of x Lies in the Direction of y",
        "purpose": "Introduce vector projection geometrically and algebraically.",
        "title": "Projection = How Much of x Lies in the Direction of y",
        "subtitle": "",
        "mini_visual": "projection_geometry",
        "text_explanation": (
            "Projection asks what part of one vector points along another. It isolates "
            "the directional component."
        ),
        "bullets": [
            "result points along target direction",
            "length depends on alignment",
            "sign can be positive or negative",
        ],
        "formulas": [
            "proj_y(x) = ((x·y)/(‖y‖^2)) y",
            "if u = y/‖y‖, then proj_y(x) = (x·u)u",
        ],
        "required_formulas": True,
        "concrete_example_anchor": "Generic projection picture.",
        "takeaway": "Projection is one of the most useful geometric decompositions in the deck.",
        "layout": PART2_POSTER_LAYOUT,
    },
    {
        "kind": "worked_example",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 28,
        "slide_title": "Projection of x^(1) Onto x^(2)",
        "purpose": "Make the homework projection question fully understandable.",
        "title": "Projection of x^(1) Onto x^(2)",
        "mini_visual": "projection_homework_geometry",
        "visual_label": "Geometry",
        "visual_caption": "The projected vector points along x^(2), not in an arbitrary direction",
        "steps": [
            {
                "title": "Step 1",
                "body": "Write the unit direction of the target vector.",
                "formula": "u = x^(2)/‖x^(2)‖",
            },
            {
                "title": "Step 2",
                "body": "The projection has the form “scalar times target direction.”",
                "formula": "p_{x^(1)→x^(2)} = c u",
            },
            {
                "title": "Step 3",
                "body": "Compute the signed magnitude from a dot product.",
                "formula": "c = (x^(1)·x^(2))/‖x^(2)‖",
            },
            {
                "title": "Step 4",
                "body": "Substitute the symbolic homework dot product.",
                "formula": "x^(1)·x^(2)=a_1^2−a_2^2+a_3^2",
            },
        ],
        "result": {
            "label": "Result",
            "body": "Equivalent direct formula:",
            "formula": "proj_{x^(2)}(x^(1)) = ((x^(1)·x^(2))/‖x^(2)‖^2) x^(2)",
        },
        "takeaway": (
            "Projection is controlled by direction and alignment together, which is exactly "
            "why dot products matter."
        ),
        "layout": PART2_DENSE_WORKED_EXAMPLE_LAYOUT,
    },
    {
        "kind": "triple_role",
        "theme": "concept",
        "background": "Background 10.png",
        "slide_number": 29,
        "slide_title": "Why Norms, Dot Products, and Projections Matter in ML",
        "purpose": "Close Part II by connecting the geometry back to machine learning.",
        "visual": "A three-card ML bridge slide with visuals for size, similarity, and directional component.",
        "text_explanation": (
            "In machine learning, vectors represent examples, features, parameters, and gradients."
        ),
        "bullets": [
            "norm → size / magnitude",
            "dot product → similarity / alignment",
            "projection → directional component",
        ],
        "formulas": [],
        "concrete_example_anchor": (
            "Mention feature vectors in classification, parameter vectors in linear models, "
            "and gradients in optimization."
        ),
        "speaker_intent": (
            "This geometry is not background decoration — it is the operating language of "
            "machine learning."
        ),
        "title": "Why Norms, Dot Products, and Projections Matter in ML",
        "subtitle": (
            "Norms measure size, dot products measure alignment, and projections isolate "
            "directional components."
        ),
        "panels": [
            {
                "title": "Norm",
                "mini_visual": "ml_norm_bridge",
                "caption": "feature-vector size / parameter magnitude",
                "formula": "‖x‖",
            },
            {
                "title": "Dot Product",
                "mini_visual": "ml_dot_bridge",
                "caption": "similarity / alignment / scoring",
                "formula": "x·y",
            },
            {
                "title": "Projection",
                "mini_visual": "ml_projection_bridge",
                "caption": "directional component / useful subspace",
                "formula": "proj_y(x)",
            },
        ],
        "takeaway": "This geometry is the operating language of machine learning.",
        "layout": PART2_THREE_PANEL_LAYOUT,
    },
]

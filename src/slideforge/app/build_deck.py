from __future__ import annotations

"""
Compatibility wrapper for presentation creation.

Why this file exists:
- `src/slideforge_app.py` currently imports `create_presentation` from
  `slideforge.app.build_deck`.
- The actual implementation lives in `slideforge.app.presentation_factory`.

Keeping this module as a thin re-export avoids breaking existing imports while
making `presentation_factory.py` the single source of truth.
"""

from slideforge.app.presentation_factory import create_presentation

__all__ = ["create_presentation"]
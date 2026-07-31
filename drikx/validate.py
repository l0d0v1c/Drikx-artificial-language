"""Oracle de validation Drikx.

Point d'entrée `validate(sentence) -> Report`. La logique vit dans `engine` ; ce module
existe pour respecter la structure de dépôt cible (spec §5) et offrir une façade stable.
"""

from __future__ import annotations

from .engine import Issue, Report, get_lexicon, validate

__all__ = ["validate", "Report", "Issue", "get_lexicon"]

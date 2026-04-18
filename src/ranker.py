from __future__ import annotations

from typing import Dict, List, Tuple


def score_document(term_frequencies: Dict[str, int]) -> int:
    """Score one document as sum of matched query-term frequencies."""
    return sum(term_frequencies.values())


def rank_documents(
    doc_term_frequencies: Dict[str, Dict[str, int]],
) -> List[Tuple[str, int, Dict[str, int]]]:
    """
    Rank documents by descending score, then ascending doc_id for stable ties.

    Returns tuples: (doc_id, score, matched_term_frequencies).
    """
    ranked = [
        (doc_id, score_document(term_freqs), term_freqs)
        for doc_id, term_freqs in doc_term_frequencies.items()
    ]
    ranked.sort(key=lambda item: (-item[1], item[0]))
    return ranked

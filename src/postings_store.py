from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Posting:
    """One posting entry containing a document and term frequency."""

    doc_id: str
    term_frequency: int


class PostingsStore:
    """
    Stores occurrence lists in an external array-like structure.

    Each occurrence list is addressed by an integer index so that
    a dictionary structure (like a trie) can store only pointers.
    """

    def __init__(self) -> None:
        self._lists: List[List[Posting]] = []

    def create_occurrence_list(self, frequency_by_doc: Dict[str, int]) -> int:
        """
        Create a new sorted postings list and return its index.

        Sort order is by document id for deterministic retrieval and
        merge-style intersection later.
        """
        postings = [
            Posting(doc_id=doc_id, term_frequency=frequency)
            for doc_id, frequency in frequency_by_doc.items()
        ]
        postings.sort(key=lambda posting: posting.doc_id)
        self._lists.append(postings)
        return len(self._lists) - 1

    def get_occurrence_list(self, list_index: int) -> List[Posting]:
        """Return one postings list by index."""
        return self._lists[list_index]

    def total_lists(self) -> int:
        """Return the number of occurrence lists currently stored."""
        return len(self._lists)

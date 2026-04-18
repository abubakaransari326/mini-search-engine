from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from src.inverted_index import InvertedIndex
from src.postings_store import Posting
from src.ranker import rank_documents
from src.stopwords import STOP_WORDS
from src.utils import filter_stop_words, tokenize_text


@dataclass
class SearchResult:
    """One ranked search result document."""

    doc_id: str
    score: int
    term_frequencies: Dict[str, int]


def normalize_query_terms(query: str) -> List[str]:
    """Tokenize and stop-word filter query text."""
    raw_tokens = tokenize_text(query)
    return filter_stop_words(raw_tokens, STOP_WORDS)


def search_single_term(index: InvertedIndex, term: str) -> List[Posting]:
    """Return postings for one normalized term."""
    normalized = normalize_query_terms(term)
    if not normalized:
        return []

    # For a single-term API, only first normalized token is considered.
    pointer = index.trie.search(normalized[0])
    if pointer is None:
        return []
    return index.postings_store.get_occurrence_list(pointer)


def search_multi_term_and(index: InvertedIndex, query: str) -> List[SearchResult]:
    """
    Perform AND-search for query terms with merge-style postings intersection.

    Results are ranked by summed term frequencies, then doc_id.
    """
    terms = normalize_query_terms(query)
    if not terms:
        return []

    terms = sorted(set(terms))
    postings_by_term: Dict[str, List[Posting]] = {}
    for term in terms:
        pointer = index.trie.search(term)
        if pointer is None:
            return []
        postings_by_term[term] = index.postings_store.get_occurrence_list(pointer)

    ordered_terms = sorted(terms, key=lambda t: len(postings_by_term[t]))
    shared_docs = postings_by_term[ordered_terms[0]]

    for term in ordered_terms[1:]:
        shared_docs = _intersect_postings(shared_docs, postings_by_term[term])
        if not shared_docs:
            return []

    doc_term_frequencies: Dict[str, Dict[str, int]] = {}
    for posting in shared_docs:
        doc_id = posting.doc_id
        term_freqs: Dict[str, int] = {}
        for term in terms:
            term_freqs[term] = _lookup_frequency(postings_by_term[term], doc_id)
        doc_term_frequencies[doc_id] = term_freqs

    ranked = rank_documents(doc_term_frequencies)
    return [
        SearchResult(doc_id=doc_id, score=score, term_frequencies=term_freqs)
        for doc_id, score, term_freqs in ranked
    ]


def _intersect_postings(left: List[Posting], right: List[Posting]) -> List[Posting]:
    """Intersect two sorted postings lists by document id."""
    i = 0
    j = 0
    intersection: List[Posting] = []

    while i < len(left) and j < len(right):
        left_doc = left[i].doc_id
        right_doc = right[j].doc_id
        if left_doc == right_doc:
            # Keep one posting per shared doc; frequencies are looked up later.
            intersection.append(left[i])
            i += 1
            j += 1
        elif left_doc < right_doc:
            i += 1
        else:
            j += 1

    return intersection


def _lookup_frequency(postings: List[Posting], doc_id: str) -> int:
    """Find term frequency for a specific doc_id in a sorted postings list."""
    for posting in postings:
        if posting.doc_id == doc_id:
            return posting.term_frequency
        if posting.doc_id > doc_id:
            break
    return 0

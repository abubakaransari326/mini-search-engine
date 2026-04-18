from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from src.compressed_trie import CompressedTrie
from src.parser import parse_and_normalize_file
from src.postings_store import PostingsStore


@dataclass
class IndexedDocument:
    """Stores parsed metadata for an indexed page."""

    doc_id: str
    links: List[str]
    term_count: int


@dataclass
class InvertedIndex:
    """Container for the trie, postings store, and indexed document metadata."""

    trie: CompressedTrie
    postings_store: PostingsStore
    documents: List[IndexedDocument]
    total_unique_terms: int


def build_inverted_index(pages_dir: Path) -> InvertedIndex:
    """Build a textbook-style inverted index from local HTML pages."""
    html_files = sorted(pages_dir.glob("*.html"))
    if not html_files:
        raise ValueError(f"No HTML files found in {pages_dir}.")

    term_to_doc_frequencies: Dict[str, Dict[str, int]] = defaultdict(dict)
    documents: List[IndexedDocument] = []

    for file_path in html_files:
        parsed = parse_and_normalize_file(file_path)
        doc_id = parsed["page"]
        terms = parsed["terms"]
        links = parsed["links"]

        doc_term_counts = Counter(terms)
        for term, freq in doc_term_counts.items():
            term_to_doc_frequencies[term][doc_id] = freq

        documents.append(
            IndexedDocument(doc_id=doc_id, links=links, term_count=len(terms))
        )

    postings_store = PostingsStore()
    trie = CompressedTrie()

    for term in sorted(term_to_doc_frequencies.keys()):
        occurrence_list_index = postings_store.create_occurrence_list(
            term_to_doc_frequencies[term]
        )
        trie.insert(term, occurrence_list_index)

    return InvertedIndex(
        trie=trie,
        postings_store=postings_store,
        documents=documents,
        total_unique_terms=len(term_to_doc_frequencies),
    )

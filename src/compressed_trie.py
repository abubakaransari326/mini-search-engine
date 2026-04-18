from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class CompressedTrieNode:
    """A node in a compressed trie (radix trie)."""

    children: Dict[str, "CompressedTrieNode"] = field(default_factory=dict)
    occurrence_list_index: Optional[int] = None


class CompressedTrie:
    """
    Compressed trie for mapping terms to occurrence list indices.

    Each outgoing edge from a node stores a string segment (not just one char),
    which keeps the trie compact compared to a standard character-by-character trie.
    """

    def __init__(self) -> None:
        self.root = CompressedTrieNode()

    def insert(self, term: str, occurrence_list_index: int) -> None:
        """Insert or update a term with its occurrence list index."""
        if not term:
            raise ValueError("Term must be non-empty.")
        self._insert_at_node(self.root, term, occurrence_list_index)

    def search(self, term: str) -> Optional[int]:
        """Return the occurrence list index for a term, or None if absent."""
        if not term:
            return None

        node = self.root
        remaining = term

        while remaining:
            matched_edge = None
            for edge_label, child in node.children.items():
                common_len = _common_prefix_length(remaining, edge_label)
                if common_len == 0:
                    continue
                if common_len < len(edge_label):
                    return None
                matched_edge = (edge_label, child)
                remaining = remaining[common_len:]
                node = child
                break

            if matched_edge is None:
                return None

        return node.occurrence_list_index

    def _insert_at_node(
        self, node: CompressedTrieNode, remaining: str, occurrence_list_index: int
    ) -> None:
        for edge_label, child in list(node.children.items()):
            common_len = _common_prefix_length(remaining, edge_label)
            if common_len == 0:
                continue

            # Existing edge fully matches; continue descent.
            if common_len == len(edge_label):
                new_remaining = remaining[common_len:]
                if not new_remaining:
                    child.occurrence_list_index = occurrence_list_index
                    return
                self._insert_at_node(child, new_remaining, occurrence_list_index)
                return

            # Partial overlap: split edge into common prefix and suffix.
            common_prefix = edge_label[:common_len]
            edge_suffix = edge_label[common_len:]
            term_suffix = remaining[common_len:]

            split_node = CompressedTrieNode()
            split_node.children[edge_suffix] = child

            if term_suffix:
                split_node.children[term_suffix] = CompressedTrieNode(
                    occurrence_list_index=occurrence_list_index
                )
            else:
                split_node.occurrence_list_index = occurrence_list_index

            del node.children[edge_label]
            node.children[common_prefix] = split_node
            return

        # No overlapping edge from this node; add direct compressed edge.
        node.children[remaining] = CompressedTrieNode(
            occurrence_list_index=occurrence_list_index
        )


def _common_prefix_length(left: str, right: str) -> int:
    """Return length of the longest common prefix for two strings."""
    max_len = min(len(left), len(right))
    for idx in range(max_len):
        if left[idx] != right[idx]:
            return idx
    return max_len

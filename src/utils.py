from __future__ import annotations

import re
from typing import List, Set


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def tokenize_text(text: str) -> List[str]:
    """Lowercase and split text into alphanumeric tokens."""
    return TOKEN_PATTERN.findall(text.lower())


def filter_stop_words(tokens: List[str], stop_words: Set[str]) -> List[str]:
    """Remove stop words while keeping token order."""
    return [token for token in tokens if token not in stop_words]

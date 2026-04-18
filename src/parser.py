from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from bs4 import BeautifulSoup
from src.stopwords import STOP_WORDS
from src.utils import filter_stop_words, tokenize_text


def parse_html_file(file_path: Path) -> Dict[str, object]:
    """Parse one HTML file and return extracted text and local links."""
    html = file_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)

    links: List[str] = []
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()
        if href and not href.startswith(("http://", "https://", "mailto:", "#")):
            links.append(href)

    return {
        "page": file_path.name,
        "text": text,
        "links": links,
    }


def parse_and_normalize_file(file_path: Path) -> Dict[str, object]:
    """Parse one HTML file and return text, links, and cleaned terms."""
    parsed = parse_html_file(file_path)
    raw_tokens = tokenize_text(parsed["text"])
    terms = filter_stop_words(raw_tokens, STOP_WORDS)
    parsed["terms"] = terms
    return parsed

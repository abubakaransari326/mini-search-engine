from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List

from src.inverted_index import build_inverted_index
from src.search_engine import SearchResult, normalize_query_terms, search_multi_term_and


DEMO_QUERIES = [
    "crawler",
    "search ranking",
    "crawler crawler",
    "quartzite obsidian",
    "beautifulsoup obsidian",
    "zephyrionxyz",
    "python unknownterm",
    "CRAWLER!!!",
    "   \t  ",
    "",
    "the and of",
    "@@@ ### ???",
    "minimal vocabulary",
]


def format_results(query: str, results: List[SearchResult]) -> List[str]:
    lines = [f"Query: {query!r}"]
    if not query.strip():
        lines.append("  Empty or whitespace-only query. No indexable terms.")
        return lines
    indexable = normalize_query_terms(query)
    if not indexable:
        lines.append("  No indexable terms after tokenization and stop word removal.")
        return lines
    if not results:
        lines.append("  No matching documents.")
        return lines

    lines.append(f"  Matched documents: {len(results)}")
    for rank, result in enumerate(results, start=1):
        freq_part = ", ".join(
            f"{term}:{freq}" for term, freq in sorted(result.term_frequencies.items())
        )
        lines.append(
            f"  {rank}. {result.doc_id} | score={result.score} | term_freqs=({freq_part})"
        )
    return lines


def run_queries(queries: Iterable[str], index, print_output: bool = True) -> List[str]:
    output_lines: List[str] = []
    for query in queries:
        results = search_multi_term_and(index, query)
        block = format_results(query, results)
        output_lines.extend(block)
        output_lines.append("-" * 60)
        if print_output:
            print("\n".join(block))
            print("-" * 60)
    return output_lines


def run_interactive_mode(index) -> None:
    print("Interactive search mode. Type 'exit' to quit.")
    while True:
        query = input("search> ").strip()
        if query.lower() in {"exit", "quit"}:
            print("Exiting search.")
            return
        run_queries([query], index=index, print_output=True)


def run_demo_mode(index, output_file: Path | None) -> None:
    print("Running preset demo queries...")
    output_lines = run_queries(DEMO_QUERIES, index=index, print_output=True)
    if output_file is not None:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("\n".join(output_lines) + "\n", encoding="utf-8")
        print(f"Saved demo output to {output_file}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Mini Search Engine CLI")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run preset test queries instead of interactive mode.",
    )
    parser.add_argument(
        "--demo-output",
        type=Path,
        default=None,
        help="Optional file path to save demo query output.",
    )
    args = parser.parse_args()

    pages_dir = Path("data/pages")
    index = build_inverted_index(pages_dir)
    print(
        f"Indexed {len(index.documents)} documents and "
        f"{index.total_unique_terms} unique terms."
    )

    if args.demo:
        run_demo_mode(index=index, output_file=args.demo_output)
    else:
        run_interactive_mode(index=index)


if __name__ == "__main__":
    main()

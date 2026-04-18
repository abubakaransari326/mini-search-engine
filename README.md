# Mini Search Engine (Simplified Inverted Index)

## 1) Project Overview

This project implements a simplified search engine for a small local website, following the search engine model described in Section 23.6.4 (Search Engines / Inverted Files).

The system:
- parses a collection of local HTML pages,
- extracts text and hyperlinks,
- removes stop words and normalizes tokens,
- builds an inverted index,
- supports single-keyword and multi-keyword (AND) queries,
- ranks matching pages using a simple frequency-based score.

## 2) Textbook Compliance (Section 23.6.4)

The implementation mirrors the required architecture:

- **Compressed trie for index terms**  
  `src/compressed_trie.py` stores vocabulary terms.  
  Each terminal node stores an integer pointer (`occurrence_list_index`).

- **Occurrence lists stored outside the trie**  
  `src/postings_store.py` stores postings lists in an external array-like structure.  
  This follows the textbook idea: keep the dictionary compact in memory, while storing larger occurrence lists separately.

- **Intersection using sorted postings**  
  `src/search_engine.py` uses a merge-style intersection algorithm over postings lists sorted by document id.

## 3) Data Structures Used

- **Compressed trie (radix trie)**: term dictionary with pointer lookup.
- **Array/list of postings lists**: external occurrence storage.
- **Posting record**: `(doc_id, term_frequency)`.
- **Dictionary / defaultdict / Counter**:
  - term -> doc frequencies during index build,
  - ranking preparation.
- **Lists/Sets**:
  - query term normalization and deduplication.

## 4) Algorithms Used

### 4.1 Parsing and Normalization
Files: `src/parser.py`, `src/utils.py`, `src/stopwords.py`

1. Parse HTML with BeautifulSoup.
2. Remove script/style/noscript content.
3. Extract visible text and local hyperlinks.
4. Tokenize with a lowercase alphanumeric regex.
5. Remove stop words.

### 4.2 Inverted Index Construction
File: `src/inverted_index.py`

1. Parse each document and collect normalized terms.
2. Compute per-document term frequency (`Counter`).
3. Build term -> `{doc_id: frequency}` map.
4. For each term:
   - create a postings list in `PostingsStore`,
   - insert term into compressed trie with postings pointer index.

### 4.3 Query Processing
File: `src/search_engine.py`

- **Single term query**:
  - normalize term,
  - trie lookup,
  - return corresponding postings list.

- **Multi-term AND query**:
  - normalize query,
  - fetch each term's postings list,
  - intersect sorted postings lists using merge-style pointer traversal.

### 4.4 Ranking
File: `src/ranker.py`

Ranking score:

`score(document, query) = sum of frequencies of query terms in that document`

Tie-breaking is deterministic by document id (ascending).

## 5) Project Structure

```text
mini-search-engine/
├── main.py
├── requirements.txt
├── README.md
├── data/
│   └── pages/
│       ├── index.html
│       ├── algorithms.html
│       ├── data-structures.html
│       ├── crawler.html
│       ├── ranking.html
│       ├── testing.html
│       ├── python-tools.html
│       └── empty-note.html
├── output/
│   └── sample_runs.txt
└── src/
    ├── parser.py
    ├── utils.py
    ├── stopwords.py
    ├── compressed_trie.py
    ├── postings_store.py
    ├── inverted_index.py
    ├── search_engine.py
    └── ranker.py
```

## 6) Input Data

Input pages are local HTML documents in `data/pages/` (8 pages), with hyperlinks between pages to simulate a small website graph.

The corpus includes both normal content and boundary-style content (`empty-note.html`) to validate stop-word and sparse-content behavior.

## 7) How to Run

### 7.1 Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 7.2 Run interactive search mode

```bash
python3 main.py
```

Then enter queries at the `search>` prompt.  
Type `exit` or `quit` to stop.

### 7.3 Run preset demo queries and save output

```bash
python3 main.py --demo --demo-output output/sample_runs.txt
```

This executes a predefined query set (including boundary cases) and writes results to `output/sample_runs.txt`.

## 8) Boundary Conditions Tested

The demo query set includes:

- empty query (`""`)
- whitespace-only query
- punctuation-only query
- stop-word-only query (`the and of`)
- unknown term (`zephyrionxyz`)
- mixed known/unknown terms (`python unknownterm`)
- repeated term (`crawler crawler`)
- case/punctuation normalization (`CRAWLER!!!`)
- multi-term with empty intersection (`quartzite obsidian`)
- sparse-document hit (`minimal vocabulary`)

These cases are captured in `output/sample_runs.txt`.

## 9) Notes and Limitations

- Ranking is intentionally simple (frequency sum) for clarity.
- The crawler behavior is represented through local hyperlink extraction in the small corpus.
- This project is not optimized for very large corpora or distributed search.

## 10) Deliverables Checklist

- [x] README with approach, algorithms, and data structures
- [x] Well-commented source code (Python)
- [x] Input pages (`data/pages/`)
- [x] Output sample runs (`output/sample_runs.txt`)
- [x] Short demonstration video

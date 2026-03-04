# N-Grams Autocomplete

A character-based n-grams language model for probabilistic query autocomplete. Given a text prefix, it suggests the most likely completions based on a trained model.

## How it works

The model is trained on a corpus of queries (TSV format) and learns character-level n-gram statistics. It uses a priority queue-based beam search to generate ranked completions for any given prefix. A long-term memory component (hashed prefix) complements the short-range n-gram context.

## Dependencies

- Python 3.x
- [bottle](https://bottlepy.org/) — `pip install bottle`

## Sample Datasets

This repository includes two pre-processed query frequency datasets derived from the **AOL Search Query Logs** (2006):

| File | Queries |
|------|---------|
| `aol_top50k.tsv` | Top 50,000 most frequent queries |
| `aol_top500k.tsv` | Top 500,000 most frequent queries |

**Format:** tab-separated, two columns — `query<TAB>frequency`

### How it was generated

The raw AOL logs (10 files, ~36M query events) were downloaded from the
[McGill University mirror](https://cim.mcgill.ca/~dudek/206/Logs/AOL-user-ct-collection/).
All queries were lowercased, counted across all files, sorted by descending frequency,
and the top N rows were kept:

```bash
# Download raw files from McGill mirror, then:
python3 -c "
import gzip
from collections import Counter

counts = Counter()
files = ['user-ct-test-collection-01.txt'] + \
        [f'aol_{i:02d}.txt.gz' for i in range(2, 11)]
for fname in files:
    opener = gzip.open if fname.endswith('.gz') else open
    with opener(fname, 'rt', errors='replace') as f:
        next(f)  # skip header
        for line in f:
            parts = line.split('\t')
            if len(parts) >= 2:
                q = parts[1].strip().lower()
                if q:
                    counts[q] += 1
with open('aol_query_frequencies.tsv', 'w') as out:
    for q, c in counts.most_common():
        out.write(f'{q}\t{c}\n')
"
head -50000  aol_query_frequencies.tsv > aol_top50k.tsv
head -500000 aol_query_frequencies.tsv > aol_top500k.tsv
```

**⚠️ Note:** The AOL dataset is a 2006 data leak of real (anonymised) user queries.
It is widely used in academic research but may contain sensitive content.
Do not redistribute or use commercially.

## Usage

### 1. Train a model

Input: a TSV file with queries and their frequencies.

```bash
python ngrams_model.py [options] input_queries.tsv
```

Options:
- `-n` / `--ngrams_order` — number of preceding characters to use as context (default: 3)
- `-l` / `--long_term_order` — characters used for long-term memory hash (default: 2)
- `-c` / `--column_number_query` — zero-based column index of the query (default: 0)
- `-f` / `--column_number_frequency` — zero-based column index of the frequency (default: 1)
- `-v` / `--verbose` — print progress info

Output: a serialized model file named `ngrams<lterm>_<order>.model`.

### 2. Start the autocomplete server

```bash
python server.py [options] ngrams_model_filepath
```

Options:
- `-v` / `--verbose` — print loading info

The server starts on `http://localhost:8080`. Query suggestions are available at:

```
http://localhost:8080/ngrams/<prefix>/
```

### 3. Use the web UI

Open `ngrams.html` in a browser. Type in the search box and suggestions will appear after a short pause (requires the server to be running).

### 4. Filter junk queries (optional)

Use `filter_junk.py` to identify queries that have a very low likelihood under the trained model:

```bash
python filter_junk.py [options] ngrams_model_file input_queries.tsv output_junk.tsv
```

Options:
- `-t` / `--threshold_log_likelihood` — log-likelihood threshold below which a query is considered junk (default: -50.0)
- `-c` / `--column_number_query` — zero-based column index of the query (default: 0)
- `-f` / `--column_number_frequency` — zero-based column index of the frequency (default: 1)
- `-l` / `--line_limit` — stop after this many lines (default: no limit)
- `-v` / `--verbose` — print filtered queries

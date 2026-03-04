# N-Grams Autocomplete

A character-based n-grams language model for probabilistic query autocomplete. Given a text prefix, it suggests the most likely completions based on a trained model.

## How it works

The model is trained on a corpus of queries (TSV format) and learns character-level n-gram statistics. It uses a priority queue-based beam search to generate ranked completions for any given prefix. A long-term memory component (hashed prefix) complements the short-range n-gram context.

## Dependencies

- Python 3.x
- [bottle](https://bottlepy.org/) — `pip install bottle`

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

Output: a serialized model file named `ngrams<lterm>_<order>.model.gz`.

### 2. Start the autocomplete server

A pre-trained model (`ngrams2_3.model.gz`) trained on `aol_top500k.tsv` is included in the repository. To launch directly:

```bash
python server.py ngrams2_3.model.gz
```

Or with your own model:

```bash
python server.py [options] path/to/model.gz
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

## Sample Dataset

`aol_top500k.tsv` contains the top 500,000 most frequent queries from the **AOL Search Query Logs** (2006), in the format the model expects: `query<TAB>frequency`.

To regenerate it, run:

```bash
python download_aol_dataset.py
```

This downloads the raw logs from the [McGill University mirror](https://cim.mcgill.ca/~dudek/206/Logs/AOL-user-ct-collection/), counts query frequencies across all 10 files (~36M events), and writes the top 500k rows sorted by descending frequency.

**⚠️ Note:** The AOL dataset is a 2006 data leak of real (anonymised) user queries.
It is widely used in academic research but may contain sensitive content.
Do not redistribute or use commercially.

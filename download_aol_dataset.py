"""
Downloads the AOL 2006 search query logs from the McGill University mirror,
counts query frequencies, and writes the top 500k to aol_top500k.tsv.

Source: https://cim.mcgill.ca/~dudek/206/Logs/AOL-user-ct-collection/

⚠️  The AOL dataset is a 2006 data leak of real (anonymised) user queries.
    It is widely used in academic research but may contain sensitive content.
    Do not redistribute or use commercially.
"""

import gzip
import urllib.request
from collections import Counter
from pathlib import Path

BASE_URL = "https://cim.mcgill.ca/~dudek/206/Logs/AOL-user-ct-collection/"
FILES = (
    [("user-ct-test-collection-01.txt", False)]
    + [(f"user-ct-test-collection-{i:02d}.txt.gz", True) for i in range(2, 11)]
)
TOP_N = 500_000
OUTPUT = "aol_top500k.tsv"


def download(filename):
    dest = Path(filename)
    if not dest.exists():
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(BASE_URL + filename, dest)
    return dest


def count_queries():
    counts = Counter()
    for filename, compressed in FILES:
        path = download(filename)
        opener = gzip.open if compressed else open
        with opener(path, "rt", errors="replace") as f:
            next(f)  # skip header
            for line in f:
                parts = line.split("\t")
                if len(parts) >= 2:
                    q = parts[1].strip().lower()
                    if q:
                        counts[q] += 1
        print(f"  {len(counts):,} unique queries so far")
    return counts


if __name__ == "__main__":
    counts = count_queries()
    print(f"Writing top {TOP_N:,} queries to {OUTPUT}...")
    with open(OUTPUT, "w") as out:
        for q, c in counts.most_common(TOP_N):
            out.write(f"{q}\t{c}\n")
    print("Done.")

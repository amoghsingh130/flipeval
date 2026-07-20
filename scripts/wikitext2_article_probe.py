"""WikiText-2 article-reconstruction eligibility probe (Decision Point A).

Implements the level-1-heading reconstruction rule of the draft dated amendment
to PREREGISTRATION.md verbatim, and reports how many reconstructed articles
clear the registered 2,048-token eligibility threshold under the pinned Qwen
tokenizer.

This is calibration-eligibility data only. It computes no model output and
touches no benchmark; results-blind status is unaffected.

If Option A is signed, this file is the reference implementation: the builder's
reconstruction must match `reconstruct_articles` verbatim.
"""

import statistics

from datasets import load_dataset
from transformers import AutoTokenizer

DATASET_REPO = "Salesforce/wikitext"
DATASET_CONFIG = "wikitext-2-raw-v1"
DATASET_SPLIT = "train"
DATASET_REVISION = "b08601e04326c79dfdd32d625aee71d232d685c3"

MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
MODEL_REVISION = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"

SEQUENCE_LENGTH = 2048
REQUIRED_SAMPLES = 128

# Versioned with the artifact per the amendment's clause 4.
RECONSTRUCTION_ALGORITHM = "wikitext2-level1-heading-articles-v1"


def is_level1_heading(text: str) -> bool:
    """True iff `text` is a level-1 WikiText heading (`= Title =`).

    Deeper headings (`= = Subtitle = =` and lower) are not article boundaries.
    Matches the amendment's clause 2: a single `=`-delimited title, and not a
    deeper heading.
    """
    stripped = text.strip()
    if not (stripped.startswith("= ") and stripped.endswith(" =")):
        return False
    # A deeper heading opens with "= =" and closes with "= =".
    if stripped.startswith("= =") or stripped.endswith("= ="):
        return False
    return True


def reconstruct_articles(rows: list[str]) -> list[str]:
    """Reconstruct articles from raw rows in source order.

    An article begins at each level-1 heading and runs up to but excluding the
    next one. Rows preceding the first level-1 heading form no article and are
    discarded. Member rows are concatenated in source order exactly as stored,
    with no normalization beyond what the raw corpus already carries.
    """
    articles: list[str] = []
    current: list[str] | None = None
    for text in rows:
        if is_level1_heading(text):
            if current is not None:
                articles.append("".join(current))
            current = [text]
        elif current is not None:
            current.append(text)
        # else: preamble before the first level-1 heading, discarded
    if current is not None:
        articles.append("".join(current))
    return articles


def main() -> None:
    print(f"PROBE_ALGORITHM {RECONSTRUCTION_ALGORITHM}")
    print(f"PROBE_DATASET {DATASET_REPO}/{DATASET_CONFIG}@{DATASET_REVISION}")
    print(f"PROBE_TOKENIZER {MODEL_ID}@{MODEL_REVISION}")

    ds = load_dataset(
        DATASET_REPO,
        DATASET_CONFIG,
        split=DATASET_SPLIT,
        revision=DATASET_REVISION,
    )
    rows = list(ds["text"])
    print(f"PROBE_RAW_ROWS {len(rows)}")

    articles = reconstruct_articles(rows)
    print(f"PROBE_TOTAL_ARTICLES {len(articles)}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION)
    lengths = [
        len(tokenizer(article, add_special_tokens=False)["input_ids"])
        for article in articles
    ]

    eligible = [n for n in lengths if n >= SEQUENCE_LENGTH]
    print(f"PROBE_ELIGIBLE_ARTICLES {len(eligible)}")
    print(f"PROBE_REQUIRED_SAMPLES {REQUIRED_SAMPLES}")
    print(
        "PROBE_VERDICT "
        + ("SUFFICIENT" if len(eligible) >= REQUIRED_SAMPLES else "INSUFFICIENT")
    )

    ordered = sorted(lengths)

    def pct(p: float) -> int:
        if not ordered:
            return 0
        idx = min(int(p * (len(ordered) - 1)), len(ordered) - 1)
        return ordered[idx]

    print(
        "PROBE_TOKEN_LENGTHS "
        f"min={ordered[0]} p25={pct(0.25)} median={pct(0.50)} "
        f"p75={pct(0.75)} p90={pct(0.90)} max={ordered[-1]} "
        f"mean={statistics.mean(lengths):.1f}"
    )
    print(f"PROBE_TOTAL_TOKENS {sum(lengths)}")
    # Headroom: how far past the 128th-longest article the corpus reaches.
    if len(ordered) >= REQUIRED_SAMPLES:
        print(f"PROBE_128TH_LONGEST {ordered[-REQUIRED_SAMPLES]}")


if __name__ == "__main__":
    main()

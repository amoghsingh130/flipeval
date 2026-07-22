# flipeval-cli — equivalence and flip analysis for two lm-eval runs

A standalone CLI over the registered FlipEval analysis code. Point it at two
lm-eval `--log_samples` files scored on the same items and it answers the
question an accuracy table cannot: *is this model equivalent, and did its
behaviour change even where the aggregate looks unchanged?*

## THIS LAYOUT IS TEMPORARY

`packaging/` exists because the repository is mid-campaign. `pyproject.toml`,
`README.md` and `tests/` at the repository root are all inside the source-state
fingerprint (`scripts/freeze_prepace.py`), and the freeze is not refreshed while
confirmatory cells are in flight.

**Post-campaign migration**, ruled 2026-07-22 and tracked on the post-campaign
hygiene list:

1. Packaging metadata folds into the root `pyproject.toml`.
2. `packaging/tests/` moves into `tests/`.
3. This quickstart moves into the root `README.md`.
4. The in-image gate (`apptainer exec "$IMAGE" python -m pytest -q`) is run
   **first**, and its recorded expected count in `CLAUDE.md` is updated **in the
   same commit** that adds the tests — per the standing rule that a stale
   expectation is a gate that cannot fail.
5. Commit → freeze refresh → commit.

That batch is deliberately grouped with the other two post-campaign items (the
stale `pilot_eval` baked into the image's site-packages, and the end-of-run
JSONL write), because all three want the same quiet-tree window and one image
rebuild.

Until then this layer touches **no fingerprinted path**. Its tests live outside
the root `testpaths = ["tests"]`, so they are invisible to the registered gate
and cannot perturb its count.

## Install

```bash
pip install ./packaging
```

Requires the `flipeval` distribution (the registered analysis code) on the same
interpreter. `scipy` is a real dependency here and stays: this is the standalone
tool, not the numpy-and-stdlib-only upstream contribution.

## Quickstart

```bash
flipeval-compare compare baseline.jsonl candidate.jsonl --margin 0.02
```

`--margin` is your equivalence tolerance in accuracy points — `0.02` means "I am
willing to call a 2-point difference equivalent". There is no default worth
trusting blindly; pick the number your claim actually needs.

### Verdicts

| verdict | meaning | exit |
|---|---|---|
| `CERTIFIED-EQUIVALENT` | TOST rejects both one-sided nulls at your margin | 0 |
| `DEGRADED` / `IMPROVED` | McNemar significant; direction from the discordant counts | 0 |
| `UNDERPOWERED` | neither established — reports the n you would have needed | 1 |

Input errors (missing file, mismatched item sets, bad margin) exit 2.

`UNDERPOWERED` is the common case, and it is a real answer rather than a
failure. A non-significant McNemar result is **not** evidence of equivalence; it
is failure to reject. The tool says so instead of letting silence read as a
pass.

`CERTIFIED-EQUIVALENT` takes precedence over a significant McNemar result, since
a difference can be statistically real and still smaller than the margin you
declared. When both fire, the report says so in a note rather than hiding it.

### Example output

Run against the bundled `degraded` fixture:

Verbatim from the bundled `degraded` fixture (job `11359447`):

```
$ flipeval-compare compare tests/fixtures/degraded_baseline.jsonl \
                           tests/fixtures/degraded_candidate.jsonl --margin 0.02

items    : 400 (paired on item identity)

VERDICT: DEGRADED
  McNemar p=2.236e-05 < 0.05; net accuracy delta -0.0625
  note: Not equivalent at your margin and not consistent with no change:
        TOST p_low=0.9982, p_high=1.168e-08 (equivalence needs both < 0.05).

Accuracy
  baseline           0.7500
  candidate          0.6875
  net delta          -0.0625

Flips (McNemar discordant pairs)
  b  correct -> wrong  30   (0.0750)
  c  wrong -> correct  5   (0.0125)
  McNemar p            2.236e-05

Churn
  correctness-state    0.0875
  answer string        0.2075
  wrong -> other wrong 0.1200

Equivalence and power
  TOST margin          +/-0.02
  TOST p_low           0.9982
  TOST p_high          1.168e-08
  min detectable diff  0.0406  (80% power, this n)
  required n @ margin  1645  (to detect 0.02 at 80% power)
  required n @ observed  169  (to detect 0.0625)
```

Note the churn block: correctness changed on 8.75% of items, but the *answer
string* changed on 20.75% — the gap is wrong-to-different-wrong transitions
(12%) that no accuracy metric can see.

Note also `required n @ margin`: even this clearly-degraded pair would need
**1,645** items to certify equivalence at 2 points, against the 400 it has.
Certifying equivalence is far more expensive than detecting a difference, which
is why `UNDERPOWERED` is the usual answer.

## An honest example on real data

From an exploratory quantization pilot in this project: GSM8K under two public
4-bit checkpoints showed a net accuracy change of only **+1 to +2 points** — the
kind of delta usually reported as "lossless" — while **correctness state changed
on 22–25% of items** and the **extracted answer changed on 62–63%**. On the same
runs the GPTQ-vs-AWQ winner flipped in 42.4% of item bootstraps.

**Caveat, stated because the numbers are not load-bearing:** that pilot was
exploratory — n=200 GSM8K and n=400 MMLU, raw-text prompts without chat
templates, public checkpoints with undocumented calibration. It illustrates the
phenomenon the tool measures. It is not a measured result about those methods,
and it should not be cited as one.

## What this layer does and does not do

**Does:** packaging, argument parsing, input validation, verdict logic,
reporting.

**Does not:** compute any statistic. McNemar, TOST, the paired bootstrap, the
minimum detectable difference and the required-n calculation are all imported
from `flipeval.core` and used unchanged. `flipeval.io.from_lm_eval_harness` does
the sample parsing.

Two behaviours are added *around* the registered code rather than inside it:

- **Item-set equality is enforced.** `flipeval.core._align_pair` intersects the
  two id sets and proceeds on the overlap, which is right for its own callers
  (seeds known to share items) and wrong for a CLI pointed at two arbitrary
  files. The check happens in `loader.py` before `compare` is called; the
  registered behaviour is untouched.
- **Required-n is also evaluated at your margin.** `ComparisonResult` reports
  required-n for the *observed* delta. The report gives both, since "how many
  items would I have needed for the claim I wanted to make" is the question a
  user with a margin is actually asking.

Pairing is always on `item_id` (`"{task_name}:{doc_id}"`), never on row order.

## Why not `flipeval`

The root distribution already installs a `flipeval` console script bound to the
registered `flipeval.cli:main`, which has its own `compare` subcommand with
different output (a CSV summary for the research pipeline). Claiming the same
name here would mean whichever package was installed last silently shadows the
other — the same shadowing hazard that the stale `pilot_eval` in the image
represents, and not one worth reintroducing deliberately.

So the entry point is `flipeval-compare`. `python -m flipeval_cli compare ...`
is equivalent. At migration, when this merges into the root package, the
subcommand becomes a first-class `flipeval compare` with no collision.

## Tests

```bash
cd packaging && python -m pytest -q tests
```

Golden fixtures cover each verdict class plus the mismatched-item-set failure.
Regenerate them with `python tests/make_fixtures.py` — but note the tests assert
the verdict each fixture is built to produce, so a fixture that drifts fails the
suite rather than quietly changing what is covered.

On PACE the suite runs in the pinned image, not on the login node:

```bash
sbatch -A "$ACCOUNT" -q embers ~/scratch/flipeval/work/packaging_tests.sbatch
```

## Not published

This is local and private. No PyPI upload, no releases, no change to repository
visibility. Shipping is a human decision.

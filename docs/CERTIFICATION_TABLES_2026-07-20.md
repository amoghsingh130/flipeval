# Certification Tables — how many items to certify equivalence

Computed 2026-07-20 from the completed atlas per
`docs/ATLAS_MINING_REGISTRATION_2026-07-15.md` §5. Full table:
`results/certification_tables.csv` (12 benchmark families × 3 margins).

**How to read a row.** Pick your benchmark family and the equivalence margin you
want to certify. The three `required_n` columns are the item counts you need at
the 25th percentile, median, and 75th percentile of the discordance rates the
atlas actually observed for that family — optimistic, typical, and pessimistic
compression behaviour. Then compare with `required_n_independent_binomial`, the
count you would compute if you ignored pairing.

## The table at the registered 2 pp margin

| benchmark | atlas cells | discordance p25/med/p75 | **required n** p25/med/p75 | naive (indep.) | paired advantage |
|---|---|---|---|---|---|
| musr | 24 | 0.015 / 0.034 / 0.044 | 232 / **519** / 681 | 7,617 | **14.7×** |
| gpqa | 24 | 0.035 / 0.048 / 0.067 | 545 / **749** / 1,035 | 7,233 | 9.7× |
| bbh | 192 | 0.024 / 0.044 / 0.060 | 371 / **681** / 928 | 6,492 | 9.5× |
| mmlu_pro | 5 | 0.048 / 0.053 / 0.059 | 739 / **827** / 913 | 7,695 | 9.3× |
| hellaswag | 14 | 0.031 / 0.044 / 0.079 | 475 / **688** / 1,222 | 4,992 | 7.3× |
| arc_challenge | 8 | 0.076 / 0.078 / 0.087 | 1,172 / **1,211** / 1,344 | 7,524 | 6.2× |
| ifeval | 8 | 0.048 / 0.052 / 0.072 | 736 / **800** / 1,108 | 4,211 | 5.3× |
| mmlu | 798 | 0.098 / 0.137 / 0.216 | 1,510 / **2,123** / 3,343 | 7,355 | 3.5× |
| winogrande | 15 | 0.061 / 0.122 / 0.221 | 940 / **1,879** / 3,422 | 6,267 | 3.3× |
| math | 56 | 0.107 / 0.141 / 0.169 | 1,661 / **2,186** / 2,610 | 5,222 | 2.4× |
| gsm8k | 11 | 0.006 / 0.049 / 0.076 | 100 / **750** / 1,172 | 1,236 | 1.7× |
| **ALL (pooled)** | **1,155** | 0.056 / 0.113 / 0.180 | 872 / **1,739** / 2,783 | 7,663 | **4.4×** |

Worked example: *"MMLU, 2 pp margin, typical discordance → evaluate at least
2,123 items."* Ignoring pairing would have said 7,355 — 3.5× more compute for the
same conclusion. At 1 pp the same row needs 8,492 items; at 3 pp, 944.

## Why the naive column is in the table

The independent-binomial column is not a straw man; it is what you get by
treating the baseline and compressed runs as two unrelated samples and comparing
proportions. That is the default in most reporting, and it is wrong in a
specific, quantifiable way: **the two runs are the same items through two nearly
identical models**, so they agree on the large majority of items and their
difference has far less variance than independence implies.

The advantage column is exactly that gap. It ranges from 1.7× (GSM8K) to 14.7×
(MuSR) and sits at **4.4× pooled** — i.e. a practitioner using the paired design
reaches the same equivalence conclusion with roughly a quarter of the evaluation
budget. The variation across families is itself informative: low-churn families
(MuSR, BBH, GPQA) reward pairing most, while high-churn generative families
(MATH, MMLU) both need more items *and* gain less from pairing.

Note the ordering this produces is not the intuitive one. MMLU needs ~2,123 items
at 2 pp — more than GPQA's 749 — despite GPQA being the harder benchmark, because
what drives the requirement is answer churn under compression, not difficulty.

## Method

For discordance rate p_d and margin m, at 95 % confidence and 80 % power:

```
sd_paired      = sqrt(p_d)                     # Var(d) = p_d, d in {-1,0,+1}
sd_independent = sqrt(2 * p * (1 - p))         # p = family median baseline accuracy
required_n     = ceil( ((z_{1-alpha} + z_{1-beta}) * sd / m)^2 )
               = ceil( ((1.6449 + 0.8416) * sd / m)^2 )
```

`z_{1-alpha}` is **one-sided**: TOST rejects two one-sided nulls at α each.
Implemented in `scripts/audit_stats.py` as `required_n_for_tost`, with
`paired_flip_sd` and `independent_binomial_sd` supplying the two sd's;
`scripts/certification_tables.py` drives it. The paired sd is pinned against
`flipeval.core.minimum_detectable_difference` on synthetic delta vectors in
`tests/test_audit_stats.py`.

Quartiles are numpy's linear-interpolation `np.quantile` over each family's
per-cell `accuracy_state_churn` (= harmful + beneficial flip rate; verified
identical across all 1,254 non-excluded atlas rows). The naive column uses the
family's **median baseline accuracy**, since independent-binomial variance
depends on accuracy rather than churn.

## Scope and caveats

- Families with fewer than 4 analysable cells are omitted: a quartile over 3
  points is not an empirical distribution. This drops nothing from the
  registered set — all 12 surviving families appear above.
- `mmlu_pro` (5 cells), `arc_challenge` (8), `ifeval` (8), `gsm8k` (11) rest on
  thin evidence; their quartiles should be read as indicative. `mmlu` (798),
  `bbh` (192) and `math` (56) are well supported.
- The atlas collapses MMLU's 57 per-subject cells and BBH/MATH/MuSR/GPQA's
  per-subtask cells into families, so a family's spread mixes subject-level
  variation with model-level variation. This widens the p25–p75 band relative to
  what a single practitioner evaluating one model would see, making the
  quartile columns conservative rather than optimistic.
- Both disclosed probe pairs (99 cells) are excluded per §6. They are tiny
  hand-built sanity pairs — n as low as 10, discordance up to 0.9 — and would
  distort every quartile in the table.
- These n's certify **equivalence within ±m**; they are not the n's for detecting
  a difference, which are larger at the same margin.

## Provenance

| item | value |
|---|---|
| atlas | `results/atlas_cells_summary.csv`, sha256 `98201adef9939c00bef7d89b515cbadf907315eb8a052c7f00437b8910a4712d` |
| analysable cells | 1,155 (1,254 non-excluded − 99 probe) |
| image | cell 3, sha256 `8260d04cf1f76cb5961b6538dbeb9178006b29c5d8c93d2c639976bcd1db2007` |
| compute | embers CPU job `11287114`, in-image; α = 0.05, power = 0.80 |
| gate | 109 passed, 0 skipped |

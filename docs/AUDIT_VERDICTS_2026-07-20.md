# Published-Claim Audit — Verdicts

Computed 2026-07-20 per `docs/AUDIT_REGISTRATION_2026-07-15.md` §4–5, after the
§3.4 claim-table freeze. Full per-claim results: `results/audit_verdicts.csv`.

## Headline

> **5 of 17 audited "near-lossless" compression claims are underpowered for their
> own assertion, and a further 4 are indeterminate because the source does not
> report enough to check.** 3 of the 13 determinate claims are margin-sensitive.
> **0 of 17 release the per-item outputs a third party would need to run the
> paired test themselves.**

Secondary reading (all claims judged at the registered 2 pp margin rather than
their own): **1 of 17 underpowered**. The two readings differ by a factor of five
and the reason is interpretive, not statistical — see §"Interpretive choices" #1.
Both are in the CSV (`verdict`, `verdict_at_registered_2pp`).

No claim is described as false. The audited property is the **evidential
sufficiency of the reported evaluation**, not the truth of the underlying
equivalence — a claim can be perfectly correct and still be unsupported by the
evaluation offered for it.

## Method

For each claim, at its reported (or §3.2-imputed) n:

- **V1 — detection power.** Minimum detectable delta at 80 % power, two-sided
  α = 0.05, under the paired-flip model. Per-item accuracy difference
  d ∈ {−1, 0, +1}; under the null of no true difference, Var(d) = p_d, the
  discordance rate, so sd = √p_d. Reported as MDD and as MDD ÷ claimed margin.
- **V2 — equivalence support.** Items required for TOST at the applicable margin:
  n = ⌈((z₁₋α + z₁₋β)·sd / margin)²⌉. Note **one-sided** z₁₋α = 1.6449: TOST
  rejects two one-sided nulls at α each. Labelled *underpowered for its own
  assertion* iff reported n < required n.
- **V3 — reproducibility.** Binary, from the frozen `per_item_outputs_released`
  column, cross-checked against `docs/AUDIT_RECONCILIATION_2026-07-15.md`.
- **Robustness (§5).** Every quantity recomputed under the independent-binomial
  bound (sd = √(2p(1−p))) and swept over 1 pp / 3 pp margins.

**Discordance imputation.** p_d comes from the atlas's empirical distribution for
the nearest (method family, bit width, benchmark) cell. The matcher tries tiers
most-specific-first and takes the **median** over the first non-empty tier
(median, not mean: per-cell discordance is right-skewed):

| tier | matched on | claims |
|---|---|---|
| 1 | family + bits + benchmark | 1 |
| 2 | family + bits | 11 |
| 3 | bits + benchmark | 2 |
| 4 | bits | 1 |
| 5 | benchmark | 0 |
| 6 | global (all cells) | 2 |

A tier whose target field is `None` cannot match, so a claim with no bit width
(pruning) descends automatically rather than being forced into a wrong cell.
Both disclosed probe pairs (pair_index 2 and 50, 99 cells, n as low as 10) are
excluded per `ATLAS_MINING_REGISTRATION` §6.

**Statistical provenance.** `scripts/audit_stats.py`. The analytic sd is pinned
against `flipeval.core.minimum_detectable_difference` on synthetic delta vectors
in `tests/test_audit_stats.py`, so the audit cannot silently fork from the
project's tested implementation.

## Per-claim results

Underpowered at the applicable margin — the claim's own stated margin:

| claim | source | stated margin | reported n | required n | shortfall |
|---|---|---|---|---|---|
| **R04** | AWQ | 0.30 pp | 1,319 | 50,519 | **38.3×** |
| **R17** | Red Hat Llama-3-8B W8A16 | 0.15 pp | 28,659 | 369,856 | **12.9×** |
| **R07** | SparseGPT | 0.23 pp | 12,410 | 131,482 | **10.6×** |
| **R06** | Wanda | 0.30 pp | 18,904 | 77,282 | 4.1× |
| **R15** | Red Hat Llama-3.1-8B W8A8 | 0.20 pp | 42,701 | 86,556 | 2.0× |

Largest MDD ÷ claimed-margin ratios (V1) — how much coarser the evaluation's
resolution is than the difference it pronounces negligible:

| claim | MDD (paired) | claimed margin | ratio | ratio (indep. binomial) |
|---|---|---|---|---|
| R04 | 2.09 pp | 0.30 pp | **6.97×** | 12.57× |
| R17 | 0.61 pp | 0.15 pp | **4.05×** | 7.25× |
| R07 | 0.84 pp | 0.23 pp | **3.67×** | 7.07× |
| R14 | 2.27 pp | 0.70 pp | 3.25× | — (no baseline) |
| R06 | 0.68 pp | 0.30 pp | 2.28× | 4.52× |

The independent-binomial column is uniformly *worse* — roughly 2× the ratio.
Pairing is the generous assumption; these claims are underpowered even so.

**Margin-sensitive (3 of 13):** R01, R04, R14. Each flips between underpowered
and adequately powered across the 1 pp → 3 pp sweep, so their verdicts are an
artefact of margin choice rather than a robust finding, and are reported as such.

**V3 — reproducibility: 0 yes / 3 partial / 14 no.** The three "partial" cases
(R08, R15, R16, all Red Hat cards) release per-item outputs for Arena-Hard,
OpenLLM v2 and HumanEval but **not for the OpenLLM v1 tasks the audited claim is
actually about**. Not one of the 17 sources lets a third party recompute the
paired comparison it asserts. This is arguably the most actionable finding here:
underpowering is fixable by evaluating more items, but irreproducibility means
nobody outside can check the claim at any n.

## Indeterminate — insufficient reporting (4)

| claim | source | missing input |
|---|---|---|
| R02 | LLM.int8() | no n, no baseline, no numeric delta — Figure 1 is a chart image |
| R11 | Meta quantized-Llama blog | no n, no baseline, no numeric delta — bar charts only |
| R13 | vLLM FP8 docs | n = 250 stated, but **no on-page baseline run at all** |
| R14 | vLLM FP8 KV-cache blog | n imputable, margin stated (0.7 pp), but no baseline — Figure 8 only |

R13 and R14 retain a computable V2 (the paired sd depends on discordance, not on
baseline accuracy), reported in the CSV as supplementary but excluded from the
headline K. Both are underpowered at 2 pp on that supplementary basis.

**This category is a finding, not a gap in the analysis.** Two of the four are
among the most-cited results in the field, and their headline equivalence
evidence is a chart image with no extractable numbers. That a mechanical audit
cannot evaluate them is itself the reporting-standards problem the project
exists to address.

## Interpretive choices

Registered rules that were ambiguous enough to require a decision. Each is
recorded in code and reversible by re-running with the alternative.

1. **"Applicable margin" (§4 V2) — the choice that moves the headline.** §4 names
   the 2 pp registered margin first and adds "(and at the claim's own margin when
   it states one)", then labels the verdict *underpowered for its own assertion*
   "at the applicable margin". Read as *own margin where stated, 2 pp as
   fallback*, **K = 5**. Read as *2 pp always*, **K = 1**. I took the first: the
   label says "its own assertion", and judging a claim that asserts 0.15 pp
   parity against a 2 pp yardstick tests something the source never claimed. Both
   are computed and reported; if Amogh reads §4 the other way, the CSV column
   `verdict_at_registered_2pp` is the headline without recomputation.
2. **Claimed margin = the largest |delta| the source asserts is negligible.**
   Most claims cover several benchmarks with different deltas. Using the largest
   is the reading most favourable to the source. Using the delta matched to the
   n actually used would be harsher — for R01 (n is PIQA's 1,838, largest delta
   is ARC-Easy's) it would raise the MDD/margin ratio about 34×.
3. **R04 (AWQ) is scored on GSM8K, not on its own quoted benchmark.** The primary
   quote's benchmark is COCO **CIDEr**, a generation-quality metric with no
   per-item correct/incorrect state, so the registered accuracy-flip model
   cannot apply to it. Verdict computed on the source's own accuracy benchmark
   (GSM8K, −0.30 pp). R04 is the largest shortfall in the table, so this choice
   carries weight; scoring it as indeterminate instead would give K = 4, J = 5.
4. **Claim-level, not claim×benchmark.** §4 says "for each claim × benchmark",
   but the frozen table stores one pooled n per claim. Operating at the frozen
   table's granularity avoids inventing per-benchmark rows the freeze does not
   contain. Multi-task claims use the pooled n across their enumerated splits,
   with every summed task listed in the `n_basis` column.
5. **TOST sample size uses one-sided z₁₋α.** `flipeval.required_n_for_effect`
   uses two-sided z₁₋α/₂ — correct for *detection*, but TOST is two one-sided
   tests at α each. Reusing it unchanged would have inflated every required n by
   ~27 % under the name "TOST". The formula is implemented locally, documented,
   and cross-checked against flipeval on the shared quantities.
6. **"The two probe-tagged cells" means two probe _pairs_, 99 cells.**
   `contains_disclosed_probe_cell` is true for 99 rows spanning pair_index 2 and
   50. All 99 are excluded.
7. **Degenerate-row handling is per-input, not blanket.** R13/R14 keep the
   verdicts their available inputs support rather than being discarded whole;
   only genuinely absent inputs produce "indeterminate". Nothing is imputed
   beyond §3.2's own rule.

## Provenance

| item | value |
|---|---|
| claim table | `docs/audit_claim_table.csv`, sha256 `842b9756d668618374c710f97637311b70ac7278e8b74c06960e651fc5af7b15` |
| claim-table freeze commit | `715a7ce` |
| atlas | `results/atlas_cells_summary.csv`, sha256 `98201adef9939c00bef7d89b515cbadf907315eb8a052c7f00437b8910a4712d` |
| analysable cells | 1,155 (1,254 non-excluded − 99 probe) |
| image | cell 3, sha256 `8260d04cf1f76cb5961b6538dbeb9178006b29c5d8c93d2c639976bcd1db2007` |
| compute | embers CPU job `11287114`, in-image; α = 0.05, power = 0.80 |
| gate | 109 passed, 0 skipped |

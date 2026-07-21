# Atlas Rev-2 — Correction Memo (2026-07-21)

**The registration is not amended. The code is corrected to comply with it.**
`docs/ATLAS_MINING_REGISTRATION_2026-07-15.md` is unchanged and its Dated
Amendments section remains empty. This memo records a defect in the
*implementation* of that frozen protocol, the clause each fix answers to, and
the disclosure that results had been inspected when the defect was found.

## 1. Disclosure — results were inspected first

The defects were found on **2026-07-21** by the independent spot-check
commissioned to clear the provisional-for-external-quoting caveat on
`docs/RESULTS_2026-07-15_ATLAS_AUDIT.md`. By then the rev-1 atlas had been
computed and read, the certification tables had been built on it, and the audit
verdicts (K = 4, J = 5) had been published internally using its discordance
distribution. **This correction is therefore made with results in view, and we
say so plainly rather than presenting it as a pre-specified step.**

The compliance argument for why this is nonetheless not post-hoc tuning is in
§3. The reader is entitled to weigh it knowing the order of events.

## 2. What was wrong

The spot-check reconciled **10 stratified cells, 262 of 262 compared fields,
with zero discrepancies** — the per-cell arithmetic of rev-1 is sound, and no
upstream drift was found. The defects are in *which cells reached the
arithmetic*.

| id | defect | effect |
|---|---|---|
| **F1** | The §3.2 earlier-run fallback was never implemented. `find_s1_task_file` took the newest run per side and never revisited. | 11 S1 pairs contributed **zero** analyzed cells. Pair 1 (`orca_mini_v3_7B-GPTQ`) contributes 0 of 63; its earlier quantized run joins cleanly at n = 1168, prompt-pass 1.0000, Δ = −0.2671, churn = 0.4966. |
| **F2** | The parser read only top-level `acc_norm`/`acc` and only the `hashes` struct. The newer lighteval schema nests metrics under `metrics` and stores raw `example`/`full_prompt`. | **583 of the 643** cells filed as "no binary correctness column (float-scored tasks)" were binary-scored cells the parser could not see. |
| **F4** | `join_cell` recorded the symptom "no joinable items", and `run_pair` discarded the computed join whenever a later `CellSkip` fired. | Exclusions were unauditable from the archived cell. **This is what hid F2 for six days.** |
| **F5** | `list_repo_files` ignored `Link: rel="next"`. | Latent: a details repo larger than one page would truncate into spurious "no parquet found" skips. No rev-1 cell was affected (max page 486 entries). |

**F1 is the serious one, because its loss is not random.** It removes exactly
the pairs whose quantized side was re-run later — a selection rule correlated
with the model being popular enough to re-evaluate — while §6 promises that
"all enumerated, non-excluded cells are reported."

## 3. Why this is compliance, not tuning

Three properties, each checkable:

1. **The governing text predates every result.** §3.2's fallback clause and §5's
   correctness-column rule were frozen at commit `b74fd58`, before any flip
   statistic existed. We are not choosing a rule that flatters an outcome; we
   are executing a rule that was already binding and had been under-implemented.
2. **The text fully determines the fix's direction.** §3.2 specifies the search
   order ("reverse-chronological") and the obligation ("record the choice"),
   leaving no free parameter to tune. `s1_run_combinations` is a **strict
   generalisation** of rev-1: its first element is exactly rev-1's choice, so
   the fallback can only *add* cells, never silently change one that already
   succeeded.
3. **No registered quantity moved.** The margin (2 pp), bootstrap (1000), seed
   (0), 99% prompt-hash threshold, metric suite, and every decision rule are
   untouched. Only cell *eligibility* changed, and only toward the population
   the registration already described.

The honest counter-argument, stated for the reader: had the spot-check found
that the missed cells *strengthened* the paper's thesis, we might have been
less motivated to look. We cannot disprove that. What we can offer is that the
direction of the correction was not ours to choose, that both revisions are
published, and that the delta between them is reported rather than absorbed.

## 4. The R2(b) eligibility determination

The ruling asked which reading of the registration governs: eligibility by
**scoring type** (binary correctness available in the data) or **operationally
by parser behaviour**. The registration's own text answers it:

- **§4** is the exhaustive mechanical exclusion list — join-key dedup (4.1), the
  99% prompt-hash identity gate (4.2, the only stated exclusion), and 4.3, which
  goes out of its way to say differing harness SHAs *do not* exclude a cell.
  There is no parser-reachability clause.
- **§5**: "Primary correctness column: `acc_norm` **where present**, else `acc`
  … **No cell-level results drive inclusion/exclusion decisions.**" Presence is
  a property of the data, not of the file layout.
- **§6**: "**All enumerated, non-excluded cells are reported** in the atlas
  regardless of outcome."

**Determination: eligibility is defined by scoring type.** The 583
nested-metrics cells are registered-population cells that rev-1 missed, and they
are included in rev-2. `harness_truthfulqa_mc_0` remains excluded on its merits:
mc1/mc2 are genuinely float-valued, so no binary correctness column exists.

### Interpretive choice (recorded)

§4.1 names `hashes.example` as the join key and §4.2 names `hashes.full_prompt`,
because that is what the older schema exposes. Rev-2 falls back to the raw
`example` / `full_prompt` columns when the `hashes` struct is absent. The
justification is that these clauses' operative content is **item identity** and
**prompt identity**; comparing the raw strings tests exactly that, at least as
precisely as comparing hashes of them. Reading them as identity clauses rather
than field-path clauses is what admits the newer schema. A reader who prefers
the literal field-path reading would exclude the newer-schema cells entirely and
land back at rev-1's population — that alternative is reachable by reverting
`s1_key` / `s1_prompt`.

## 5. What rev-2 changes

Per ruling R5, rev-2 uses the **same frozen 59-pair manifest**, the **same
bootstrap 1000 / seed 0**, and writes **versioned rev-2 artifacts that do not
overwrite rev-1**. Both revisions stay in the record; the delta is part of the
paper's correction narrative.

Superseded-pending-rev2 as of this memo — every denominator-dependent number:

- atlas cell counts (2,055 / 1,254 / 1,155) and all S1/S2 descriptives
- certification tables (all `required_n`, all paired-advantage ratios)
- audit discordance imputation, and therefore **K and J may move** — if they do,
  that is a new verdict computation and is documented as one
- the identical-score figures (113 / 1,155, 9.78%, 6.22%) in
  `docs/IDENTICAL_SCORE_CHURN_2026-07-21.md`

## 6. Verification

- Gate: **157 passed, 0 skipped**, in-image, `IN_IMAGE_PYTEST_EXIT=0` (embers
  job `11339898`). 12 regression tests added covering F1/F2/F4/F5.
- One pre-existing assertion updated:
  `test_join_gate_excludes_empty_intersection` asserted the old symptom string
  `"no joinable items"`. The gate decision it checks is unchanged; only the
  recorded reason is now root-cause.
- Source fingerprint refreshed and verified after the commit.
- Rev-2 must pass a **targeted second spot-check** before the blog's
  DO-NOT-PUBLISH stamp lifts: the recovered F1 pairs plus a sample of newly
  included F2 cells, same independent-reimplementation method.

## 7. Provenance

| item | value |
|---|---|
| spot-check | 2026-07-21, 10 cells, 262/262 fields, 0 discrepancies; embers jobs `11338401`, `11338619`, `11338712`, `11338745` |
| code fix commit | `4dc9db0` |
| registration (unchanged) | `docs/ATLAS_MINING_REGISTRATION_2026-07-15.md`, frozen `b74fd58` |
| manifest (unchanged) | `docs/atlas_pair_manifest.json`, frozen `f06348f` |
| rev-1 artifacts (retained) | `results/atlas_cells_summary.csv`, `results/atlas_exclusions.csv`, `results/atlas_run_20260715.tar.gz` |
| rev-2 run | embers job `11339935` |

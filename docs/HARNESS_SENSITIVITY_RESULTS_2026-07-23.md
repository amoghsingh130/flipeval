# Harness-Defaults Sensitivity Study — Results (2026-07-23)

The dated results note required by
`docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md` § 10. It reports the
registered § 5 quantities for Qwen2.5-1.5B, the pre-named headline ratio
`R = C_cond / Q̄` with both inputs beside it (§ 5.1), and the MMLU `C ≡ D`
equivalence as ruled (§ 3.3). It introduces no statistic the registration did not
already define; the study is exploratory and descriptive (§ 7).

**Scope of this note.** Phase-1 numerators `C_cond` are computed here from the
FP16 config-churn cells on the bridge subsets (§ 4). The Phase-2 denominator `Q̄`
is **not** recomputed here — it is read verbatim from the committed artifact
`results/harness_sensitivity/qbar_qwen25-1p5b.json`
(`docs/HARNESS_SENSITIVITY_QBAR_2026-07-23.md`). No confirmatory mini-grid cell is
read by this analysis. `Q̄(mmlu) = 0.199000`, `Q̄(gsm8k) = 0.287000`; neither is 0,
so no undefined-ratio case arises (§ 5.1).

## Provenance

| item | value |
|---|---|
| model | `Qwen/Qwen2.5-1.5B-Instruct` @ `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`, `dtype=float16` |
| stack | `lm_eval` 0.4.12 in frozen cell-3 image, sha256 `8260d04cf1f76cb5961b6538dbeb9178006b29c5d8c93d2c639976bcd1db2007` |
| condition runs | array job `11368976` (`--array=0-5`), embers, `--seed 0,1234,1234,1234`, `--batch_size 1`, `--log_samples` |
| driver | `~/scratch/flipeval/work/sensitivity_qwen.sbatch` (index map: 0 mmlu_ref · 1 mmlu_cd · 2 gsm8k_ref · 3 gsm8k_a · 4 gsm8k_c · 5 gsm8k_d) |
| analysis | `~/scratch/flipeval/work/sensitivity_analysis.py`, stdlib only |
| Q̄ source | `results/harness_sensitivity/qbar_qwen25-1p5b.json` (job `11376178`) |
| output artifact | `results/harness_sensitivity/sensitivity_results_qwen25-1p5b.json` |

**Reference config** (the baseline all conditions are compared against, § 3):
chat template on; GSM8K 3 inline exemplars with `--fewshot_as_multiturn false`;
MMLU zero-shot; `flexible-extract` scoring. Verified non-degenerate: REF, A, C, D
produced **distinct rendered-prompt hashes** on GSM8K doc 0
(`0ed67c2f…` / `b2c2bc19…` / `956074d0…` / `32680f26…`), so the REF≠A contrast is
real and the `fewshot_as_multiturn` auto-enable defect is not present in these runs.

Full per-condition commands are `python -m lm_eval run --model hf
--model_args pretrained=…,revision=989aa79…,dtype=float16 --tasks <T> --limit
<L> --batch_size 1 --seed 0,1234,1234,1234 --log_samples --output_path … <FLAGS>`
with, per condition:

| id | task(s) | limit | FLAGS |
|---|---|---|---|
| REF (mmlu) | 4 bridge subjects | 100 | `--apply_chat_template` |
| C ≡ D (mmlu) | 4 bridge subjects | 100 | *(none)* |
| REF (gsm8k) | gsm8k | 200 | `--apply_chat_template --num_fewshot 3 --fewshot_as_multiturn false` |
| A (gsm8k) | gsm8k | 200 | `--apply_chat_template --num_fewshot 3 --fewshot_as_multiturn true` |
| C (gsm8k) | gsm8k | 200 | `--num_fewshot 3` |
| D (gsm8k) | gsm8k | 200 | *(none)* → stock `num_fewshot=5` |

## Item counts (§ 10 validity gate)

Every condition realized its registered count exactly, so none is void:
MMLU REF 400, MMLU C≡D 400; GSM8K REF/A/B/C/D 200 each. (Condition B carries no
count of its own — see below.)

## Registered § 5 quantities and R — GSM8K (n = 200, REF acc = 0.5750, Q̄ = 0.287000)

| cond | config vs REF | acc | net Δacc | **C_cond** (correctness churn) | answer churn | c→i / i→c | **R = C_cond / Q̄** |
|---|---|---|---|---|---|---|---|
| A | exemplars as separate turns (`fewshot_as_multiturn true`) | 0.5150 | −0.0600 | **0.2400** (48/200) | 0.6600 | 30 / 18 | **0.836** = 0.2400 / 0.287 |
| B | `strict-match` scoring, same generations | 0.1200 | −0.4550 | **0.4550** (91/200) | 0.8300 | 91 / 0 | **1.585** = 0.4550 / 0.287 |
| C | chat template off, 3-shot | 0.4750 | −0.1000 | **0.3200** (64/200) | 0.8950 | 42 / 22 | **1.115** = 0.3200 / 0.287 |
| D | stock defaults (chat off, 5-shot) | 0.4950 | −0.0800 | **0.3000** (60/200) | 0.8350 | 38 / 22 | **1.045** = 0.3000 / 0.287 |

- **Condition B costs zero GPU time and has no separate run** (§ 3.1): it is
  read out of REF's own samples file, rescoring the *identical* generations under
  `strict-match` instead of `flexible-extract`. Its correctness churn (0.4550) is
  therefore the pure scoring-filter effect; its `c→i / i→c = 91 / 0` shows every
  changed item went correct→incorrect (strict is a strict subset of flexible
  correctness here), so `|Δacc|` equals the churn exactly. Its "answer churn"
  compares the two filters' extracted strings on the same generations.

## Registered § 5 quantities and R — MMLU (n = 400, REF acc = 0.4150, Q̄ = 0.199000)

**C ≡ D, reported once as ruled (§ 3.3).** For MMLU, stock defaults and the
reference differ *only* in the chat template (stock `num_fewshot` resolves to 0,
MMLU ships no `filter_list`), so conditions C and D are byte-identical
configurations. Amogh ruled 2026-07-22: run once, report as `C ≡ D`. Conditions A
and B are inapplicable to MMLU (zero-shot, no extraction filter), as registered.

| cond | config vs REF | acc | net Δacc | **C_cond** (correctness churn) | answer churn (letter) | c→i / i→c | **R = C_cond / Q̄** |
|---|---|---|---|---|---|---|---|
| C ≡ D | chat template off, zero-shot | 0.4600 | +0.0450 | **0.2100** (84/400) | 0.3925 | 33 / 51 | **1.055** = 0.2100 / 0.199 |

## Conditions dropped as infeasible

None. All registered conditions ran (or, for B, were derived as registered). The
only collapses are the two the registration already ruled: MMLU `C ≡ D` (§ 3.3)
and GSM8K B as a filter rescore of REF (§ 3.1). No condition was approximated by a
hand-built substitute (§ 8).

## Notes on reading these numbers

- `R` is reported per condition with `C_cond` and `Q̄` always beside it (§ 5.1);
  the ratio is never shown without its inputs. `Q̄` is the mean over the ten Qwen
  quantized variants of correctness-state churn vs FP16 on the same § 4 subset
  (`docs/HARNESS_SENSITIVITY_QBAR_2026-07-23.md`).
- This is Qwen2.5-1.5B only. Llama-3.2-3B is admitted by § 2 "only after its
  seed-0 canary pair passes"; that sensitivity canary has not run, so no Llama
  numerator exists and no Llama `R` is reported. (A Llama `Q̄` is separately
  computable per § 5.2 but is not the numerator's blocker.)
- The secondary external comparator (atlas rev-2, § 5.3) is a different
  population and is never `Q̄`; it is not restated here.
- Exploratory and descriptive (§ 7): no value here adjusts any registered gate,
  the mini-grid escalation rule, or any confirmatory analysis.

## Fingerprint / gate status

Doc-and-results only. `docs/` and `results/` are outside the source fingerprint
(`INCLUDED_PATHS` in `scripts/freeze_prepace.py`: `configs`, `flipeval`,
`pilot_eval`, `scripts`, `tests`), so no in-image gate run and no freeze refresh is
owed by this note — the same basis recorded in the Q̄ note's provenance.

## Dated Amendments

None.

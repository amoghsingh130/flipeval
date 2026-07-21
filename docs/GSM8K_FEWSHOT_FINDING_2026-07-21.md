# Finding: `fewshot: 1` in the bridge config ran **three** exemplars, not one

**Raised 2026-07-21 by the mini-grid preparation pass, from source inspection of
`pilot_eval/tasks.py`. No accuracy result of any kind was inspected in finding
or reporting this.** Amogh ruled the same day (§ 4); the ruling still needs a
dated amendment in his hand under
`docs/MINIGRID_REGISTRATION_2026-07-15.md` § Dated Amendments.

## 1. The finding

`pilot_eval/tasks.py` treats `fewshot` as a **boolean switch**, not a count:

```python
GSM8K_FEWSHOT = """Question: Natalia sold clips ...        # exemplar 1
Question: Weng earns $12 an hour ...                       # exemplar 2
Question: Betty is saving money for a new wallet ...        # exemplar 3
"""

def load_gsm8k(split, limit, fewshot):
    prefix = GSM8K_FEWSHOT if fewshot else ""      # tasks.py:99
```

`GSM8K_FEWSHOT` is a fixed block of **three** worked examples. Any nonzero
`fewshot` value yields all three; `fewshot: 1`, `fewshot: 3` and `fewshot: 99`
are byte-identical in effect. `configs/pace_bridge_chat.yaml` sets `fewshot: 1`,
so **the validated bridge ran GSM8K 3-shot.**

This is not a defect in the bridge run. The prompt was well-formed, identical
across all seven methods, and the validator's prompt-parity checks passed
exactly as designed. The defect is purely in the *description*: a config field
whose name implies a count while behaving as a flag.

## 2. Why it matters here

`docs/MINIGRID_REGISTRATION_2026-07-15.md` § 2 (FROZEN 2026-07-15) reads:

> GSM8K few-shot count for all mini-grid (and any later confirmatory) cells:
> **1 few-shot example, inline in the user message — matching the validated
> bridge configuration `configs/pace_bridge_chat.yaml`**.

The two halves of that sentence name different prompts. "1 few-shot example" is
one prompt; "matching the validated bridge configuration" is a different,
3-exemplar prompt. The registration is internally inconsistent, and the mini-grid
cannot be configured without resolving which half binds.

`PREREGISTRATION.md` does not settle it — it fixes only placement, not count:
"GSM8K few-shot examples are inline within the user message" (line 43). This
silence is precisely why registration § 2 existed.

## 3. The two readings

| | **A — the artifact binds** | **B — the number binds** |
|---|---|---|
| mini-grid GSM8K prompt | 3 exemplars, byte-identical to the bridge | 1 exemplar, never yet run |
| code change | none | `tasks.py` must honour a count; fingerprinted, full in-image gate |
| bridge canary value | preserved — the mini-grid runs the prompt that was validated | weakened — the canary validated a prompt the mini-grid will not use |
| GSM8K FP16 gate | derivable against the same prompt family | bridge's `[0.55, 0.65]` describes a prompt the mini-grid abandons |
| risk | the registration's literal "1" is recorded as a drafting error | a prompt change lands on confirmatory cells with no canary behind it |

## 4. Ruling (Amogh, 2026-07-21, results-blind)

**Reading A. The bridge artifact governs; the mini-grid runs the 3-exemplar
prompt.** `configs/pace_minigrid_h3.yaml` keeps `fewshot: 1` so that the emitted
prompt is byte-identical to the validated bridge canary, and the literal "1" in
registration § 2 is recorded as a drafting error rather than a protocol choice.

Basis stated at the time of ruling: source inspection only. No mini-grid job
existed, no quantized accuracy had been inspected, and the only accuracy figures
in scope were the two FP16 bridge baselines already in the signed bridge decision
record.

Consequences, all applied in this change:

1. The mini-grid config's GSM8K block matches the bridge's byte for byte, and
   carries an inline comment stating the true exemplar count so the field is
   never read as a count again.
2. `docs/MINIGRID_FP16_GATE_DERIVATION_2026-07-21.md` runs its GSM8K reference at
   `--num_fewshot 3`, matching the pilot's actual shot count.
3. The mini-grid validator asserts the GSM8K prompt hashes are identical across
   every variant within a model, which would catch any future drift in this block
   mechanically rather than by reading.

## 5. Amendment — CLOSED 2026-07-21

The frozen registration has been amended. `docs/MINIGRID_REGISTRATION_2026-07-15.md`
§ Dated Amendments now carries **Amendment 2 (2026-07-21, Amogh Singh): GSM8K
few-shot binding**, dictated by Amogh and appended verbatim. It binds the
mini-grid to the validated bridge configuration — 3 inline examples,
byte-identical prompt path — records the literal "1" as a drafting error,
confirms that `fewshot` keeps its boolean semantics, and states the results-blind
status (no mini-grid accuracy exists or has been inspected; the inspected bridge
figures are operational validation outside the confirmatory set).

This document is the supporting finding; the amendment is the governing text. No
mini-grid GSM8K job was submitted before it landed.

*Numbering note, for the record:* the amendment is labelled **Amendment 2** in a
section that previously read "None.", so there is no Amendment 1 in this
document. The label is Amogh's and was appended as dictated rather than
silently renumbered.

## 6. Separate, non-blocking: the field name

`fewshot: int` reading as a flag is a live trap for any future config author, and
the three-exemplar block is not parameterisable at all. Fixing it is a
fingerprinted change to the registered eval path with zero numerical benefit to
the mini-grid under Reading A, so it is **deliberately not done now**. Logged
here as debt to be repaid when the eval path is next legitimately opened —
never as a silent cleanup.

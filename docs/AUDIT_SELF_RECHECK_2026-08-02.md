# Audit self-recheck worksheet: R01, R10, R09, R17 (2026-08-02)

Author re-verification under decision 4 (C + D) of
`docs/SESSION_HANDOFF_2026-08-02.md`, scoped to the four claims Amogh named.
Run by Claude Code at Amogh's direction.

**This document changes no frozen file, no verdict, and no count.** It records
what was found and what a decision would cost. Two findings need Amogh's
signature before anything moves; neither is applied here.

**This is not independent verification.** It is a second automated pass by the
same class of tool that produced the record being checked. Nothing in it may be
described as inter-rater agreement, dual coding, or independent verification.

---

## 1. What was checked, and against what

The gap this addresses, from the handoff: the 2026-07-31 review verified quote
*accuracy* for all 17 sources but verified quote *location* for **R10 only**,
which is how R10's defect was found. The other 16 carry a bare
`meets §3.1 inclusion` with no recorded location, so the same defect class was
unruled-out.

Inputs, all read-only:

| Input | Role |
|---|---|
| `/storage/project/.../private/audit_sources_20260731/` | the archived sources, sealed copy, not re-fetched |
| `docs/audit_claim_table.csv` | FROZEN. The recorded `exact_quote` and `source_sha256` |
| `docs/AUDIT_REGISTRATION_2026-07-15.md` | FROZEN, including signed Amendment 2 |
| `results/audit_verdicts_rev3.csv` | sealed `0444`, paper-cited. The decision record |

**On the naming.** The request named a "frozen verification packet". No artifact
by that name exists. `results/audit_verdicts_rev3.csv` is what was checked: it is
sealed, paper-cited, and its columns are exactly the five decision fields named
(`eligible`/`eligibility_basis`, `margin_category`/`margin_category_basis`,
`benchmark`/`n`/`n_basis`, `indeterminate`/`indeterminate_kind`/
`indeterminate_reason`). If a different artifact was meant, this needs redoing.

### Provenance, re-established independently

All four target files were re-hashed against the **frozen claim table's**
`source_sha256`, not against the 2026-07-31 manifest, so the check does not
depend on the document it is checking.

| Claim | File | Bytes | Full sha256 vs frozen table |
|---|---|---|---|
| R01 | `R01.html` | 451,835 | MATCH |
| R09 | `R09.md` | 9,543 | MATCH |
| R10 | `R10.md` | 11,978 | MATCH |
| R17 | `R17.md` | 7,261 | MATCH |

The sealed tarball also re-hashed to `a912a1e7…40259` before extraction.

---

## 2. The search method, and its controls

`grep` is line-based and these sources are single-line HTML and Markdown blobs,
so a line-oriented search silently returns nothing on a string that is present.
Everything below uses a whole-file character-window matcher
(`quote_locate.py`, in this session's scratchpad, not committed; see §7).

Four normalizers, each mapping normalized offsets back to real file offsets:
`literal`, `whitespace`, `markdown_links` (reduces `[label](url)` to `label`),
`html_text` (strips tags, decodes entities). Plus a `splice` matcher for quotes
containing an ellipsis, which requires every fragment to be found **in order**.

### Every method carries three controls

A method's result is not reported unless all three pass.

| Control | What it rules out |
|---|---|
| **Positive** | a span lifted from the file must be found. A method that cannot find it is broken, and its negatives mean nothing |
| **Negative** | the same span with one character mutated must NOT be found. A method that still finds it is matching too loosely, and its positives mean nothing |
| **Differential** | a span crossing markup must be found by the normalizer and MISSED by `literal`. Without this a normalizer can pass the first two while silently no-opping |

Results: 12 of 12 positive and negative controls passed. Differential passed for
`html_text` on R01 and `markdown_links` on R09, R10 and R17.

The R10 differential needed a second probe. The first (`of Qwen2.5-7B-Instruct
to`) was also found by `literal`, because that text occurs unlinked elsewhere in
the file, so it never exercised link handling and was **inconclusive rather than
passing**. Replaced with `The GPTQ algorithm`, which spans
`The [GPTQ](https://arxiv.org/abs/2210.17323) algorithm`: `literal` 0 hits,
`markdown_links` 1 hit. This is the fifth time on this project that a checker
needed its own control before its output was worth anything.

Splice controls: positive on a real spliced sentence; negative on a mutated
final fragment; **and a negative on the correct fragments in the wrong order**,
which is the failure a naive fragment-wise search would miss.

`--limit 250` in R13 is a live example of why this matters: absent from the raw
HTML under a literal search because tags break it, present under `html_text`.

---

## 3. Quote and location findings

Offsets are into the decoded UTF-8 text; byte offsets given where they differ.
The archived artifacts for R09, R10 and R17 are raw Markdown and for R01 is
ar5iv HTML, **none of which is paginated**, so no page number exists to record.
Structural path is given instead, which is the reproducible locator.

### R01: CONFIRMED, prose

| | |
|---|---|
| Recorded quote | `negligible accuracy degradation relative to the uncompressed baseline` |
| Found by | `literal` (also `whitespace`, `html_text`), 1 hit, no normalization needed |
| Char span | 4625–4694 (bytes 4627–4696), line 74 |
| Structural path | `<div class="ltx_abstract">` → `<h6>Abstract</h6>` → `<p id="id2.id1" class="ltx_p">` |
| §3.1 location | **Prose.** Abstract body |

Verbatim, in the abstract, exactly as recorded. This is the claim carrying the
entire surviving power flag, and it holds. **No disagreement.**

### R09: quote accurate, but see §4.1

| | |
|---|---|
| Recorded quote | `achieves an average score of 73.44 on the OpenLLM benchmark` |
| Found by | `markdown_links` only. `literal` and `whitespace` both return **0 hits** |
| Char span | 1109–1243, line 36 |
| Structural path | body prose, after the Model Overview bullet list |
| §3.1 location | **Prose** |

The literal string is absent because the quote runs through a Markdown link. The
full sentence is: *"It achieves an average score of 73.44 on the
[OpenLLM](…) benchmark (version 1), whereas the unquantized model achieves
73.79."* The recorded quote is a faithful contiguous span of what a reader sees.
Accuracy confirmed. **Its eligibility is a separate matter: see §4.1.**

### R10: DEFECT CONFIRMED, independently

| | |
|---|---|
| Recorded quote | `average recovery percentage across all benchmarks is 98.6%` |
| Found by | **nothing.** 0 hits under `literal`, `whitespace` and `markdown_links`, all three controlled |
| Where `98.6` actually occurs | char 11163 (bytes 11167–11173), line 371, `<td>98.6%`, the **MMLU row**; and char 11932 (bytes 11936–11942), line 431, `<td><strong>98.6%</strong>`, the **Average row** |
| Where `Recovery` occurs | char 11049, line 361, `<th>Recovery`, a column header |
| §3.1 location | **Bare table cell.** Neither prose nor a table caption |

The card contains **no `<caption>` element at all** (verified: 0 in R09, R10 and
R17). The recorded sentence exists nowhere in the source; it was composed from
tabular data. This reproduces the 2026-07-31 finding by an independent route and
confirms the eligibility correction in Amendment 2. **No disagreement.**

Also confirmed independently: the Average recovery cell is wrong. 72.69/73.16 =
**99.36%**, and the mean of the six per-task recoveries is **99.37%**, but the
cell reads 98.6%, which is the MMLU row's value (73.19/74.24 = 98.59%). A
copy-down error in the source.

### R17: quote is a splice; source contradicts itself

| | |
|---|---|
| Recorded quote | `achieves an average score of 68.69 ... whereas the unquantized model achieves 68.54` |
| Found by | `splice` over `markdown_links`. `literal`, `whitespace` and `markdown_links` all return **0 hits** on the quote as written |
| Fragment 1 | `achieves an average score of 68.69`, chars 975–1009, line 25 |
| Fragment 2 | `whereas the unquantized model achieves 68.54`, chars 1123–1167, line 25 |
| Full span | 975–1167, line 25 |
| Elided by the `...` | `' on the [OpenLLM](…) benchmark (version 1), '` |
| §3.1 location | **Prose** |
| Same figures as table cells | 68.69 at char 7143 line 250; 68.54 at char 7182 line 252 |

The ellipsis hides a link and a parenthetical, not a substantive qualifier, so
the splice does not distort the claim. It is still a splice and should be marked
as one wherever the quote is shown. **Its eligibility is a separate matter: see
§4.1.**

**The self-contradiction, confirmed by arithmetic.** The table header is
`Benchmark | Meta-Llama-3-8B-Instruct | …quantized.w8a16 (this model) | Recovery`
and the Average row is `68.69 | 68.54 | 99.8%`. Under the table's own header the
baseline is 68.69 and the quantized model 68.54, the opposite of the prose. The
recovery cell settles which the source meant: 68.54/68.69 = **99.782%**, matching
the printed 99.8%, whereas 68.69/68.54 = 100.219% would print as 100.2%. So the
table and its own recovery figure agree with each other and disagree with the
prose about the **sign** of the delta.

`rev3` records `baseline_accuracy = 0.6854`, which follows the prose reading. The
table reading would give 0.6869. Magnitude is 0.15 pp either way and the effect
on any computed quantity is immaterial, so nothing moves. Recorded for accuracy.

---

## 4. Disagreements with the sealed record

### 4.1 R09 and R17 have no trigger vocabulary in prose (MATERIAL, needs Amogh)

This is the one finding that would move published counts.

§3.1 admits a claim only if the source asserts equivalence **"in prose or a table
caption"**, with trigger vocabulary: *near-lossless, negligible, no (significant)
degradation, matches, preserves accuracy, "X% recovery" with X ≥ 98, or an
explicit ≤1 pp delta framed as parity.*

A controlled sweep of all six Red Hat cards for that vocabulary, classifying each
hit as prose or table cell:

| Claim | Trigger vocabulary in **prose** | Verdict |
|---|---|---|
| R08 | `achieves 93.0% recovery … 98.9% for OpenLLM v1` | 98.9 ≥ 98, qualifies |
| R15 | `… 100.3% for OpenLLM v1` | qualifies |
| R16 | `… 99.4% for OpenLLM v1` | qualifies |
| **R09** | **none** | see below |
| **R10** | **none** | already excluded |
| **R17** | **none** | see below |

I then read the complete prose of R09 and R17 by hand, outside tables and code
fences, to adjudicate rather than trust the sweep. Each card contains exactly one
comparative sentence, and it is a bare score report:

> It achieves an average score of 68.69 on the [OpenLLM](…) benchmark
> (version 1), whereas the unquantized model achieves 68.54.

No trigger term appears. The recovery figures that would qualify (99.52% for R09,
99.8% for R17) exist **only as table cells**, under a `<th>Recovery` header, with
no `<caption>` anywhere in either file. **That is the identical structural
position that made R10 ineligible.**

The one arguable trigger is "an explicit ≤1 pp delta framed as parity". Both
deltas are ≤1 pp (0.35 pp and 0.15 pp), and both are stated in prose. The
question is whether they are *framed as parity*. My reading is that they are not:
`whereas` is a neutral contrastive, and the sentence asserts two scores without
characterising the gap. Nothing in either card's prose says the gap is small,
acceptable, or negligible.

**Consequence if applied.** Excluding R09 and R17 by the same reasoning that
excluded R10 would take eligible from 16 to 14 and assessable from 11 to 9. The
five non-assessability decisions are untouched, since both claims are determinate.
K stays 1, because R01 is the only flagged claim. The paper's arithmetic
identities (17−1=16, 11+5=16) would need to become 17−3=14 and 9+5=14.

**Why this is escalated and not applied.** Amendment 2 records that R10's
exclusion "did not improve any count in the direction favourable to the audit's
thesis". This one would: K/assessable moves from 1/11 (9.1%) to 1/9 (11.1%). A
correction that improves the headline fraction is exactly the kind that must be
signed by the decision owner, with the direction disclosed, and must never be
made by an agent mid-session. Amendment 2's scope clause also permits reopening
§3.1 only "to apply the existing inclusion rule to R10", so extending it to R09
and R17 requires a new dated amendment even though the reasoning is identical.

**Resolution: unresolved, escalated to Amogh.** No file changed.

### 4.2 R14's quote is in a figure caption (MINOR, disclose)

R14's frozen quote sits at chars 33316–33395 inside
`<p align="center"> … <img …> <em>Figure 8: …</em></p>`. It is a **figure**
caption. §3.1 permits "prose or a table caption" and names neither figure
captions nor, by R10's precedent, bare cells.

Unlike R10's bare cell, caption text is continuous prose that a reader reads as
the source's own assertion, so the permissive reading is defensible. R14 is
non-assessable regardless, so no verdict depends on it, but the eligible
denominator does.

**Resolution: recommend no change, disclose the location.** Flagged so it is not
discovered later as an unruled-out case.

### 4.3 `source_reported_delta_pp` uses two conventions (retained column)

Five structurally identical Red Hat cards, two different rules:

| Claim | Convention | Value |
|---|---|---|
| R09, R10 | largest per-task delta | 0.84 (GSM8K-cot), 1.05 (MMLU) |
| R15, R16, R17 | OpenLLM v1 **average** | 0.2, 0.52, 0.15 |

Both bases are stated honestly in `reported_delta_basis`, so nothing is hidden,
but they are not the same quantity. R17 is the case where it bites: its largest
per-task delta is **1.11 pp on ARC-Challenge**, not the 0.15 pp average it uses.

This drives `sens_underpowered_at_reported_delta`, and the flag is an artifact of
the choice:

| R17 convention | Required n | Reported n | Flag |
|---|---|---|---|
| average, 0.15 pp (used) | ~369,956 | 28,659 | **True** |
| largest per-task, 1.11 pp | ~6,756 | 28,659 | False |

The recorded 369,856 confirms the 0.15 pp convention. R09 stays False under
either convention, so R17 is the only one that flips.

**Resolution: no action, already withdrawn.** Amendment 2 withdrew every quantity
computed at a source's own reported delta, and
`appendix_audit_table.tex:141-146` names those columns as retired and absent from
rev-3. `audit.tex:352` records that the four rows flagged at their own reported
deltas are all robustly above threshold at 2 pp. The inconsistency sits in a
transparency column that is explicitly not a verdict. Recorded here so that if
anyone ever revives that column, they revive it knowing it is convention-
dependent.

### 4.4 Two taxonomies that must not be conflated (clarification)

`AUDIT_SOURCE_VERIFICATION_2026-07-31.md` §7 classifies claims (a)/(b)/(c), and
Amendment 2 defines categories 1/2/3. They look parallel and are not.
§7's (c) "generic adjective, no numerical bound" holds 10 claims including R01,
whereas Amendment 2's category 3 "unquantified" holds 3 and is tied to the
indeterminacy rules.

R01 is (c) but `margin_category = 2`, which is **correct**: its abstract
characterises a result the paper's Appendix A.4 tables report numerically, so it
is an informal near-lossless claim, and `evidence_form = generic_adjective`
records the quote's form on a separate axis. The rev-3 schema carries both
dimensions and is right. **No disagreement**, but the paper must not present
(a)/(b)/(c) and 1/2/3 as the same partition.

---

## 5. The five non-assessability decisions

Each checked against the archived source. **All five confirmed.**

| Claim | Recorded reason | What the source shows | Verdict |
|---|---|---|---|
| **R02** | no n, no baseline, no numeric delta | Quote is in the abstract (prose, chars 5499–5534). The four tasks it covers (WinoGrande, HellaSwag, PIQA, LAMBADA) each appear **exactly once and never inside a `<table>`**, across 19 tables and 12 figures. The headline comparison is Figure 1, a chart image | CONFIRMED |
| **R04** | metric-incompatible: COCO CIDEr | Quote sits in the **caption of Table 5** (`<figure id="S3.T5">`, caption at char 193294), whose header row is `COCO (CIDEr ↑) | 0-shot | 4-shot | …`. CIDEr is a generation metric with no per-item correct/incorrect state, so the flip model does not apply | CONFIRMED. Also validates `eligible=True` via the table-caption branch of §3.1 |
| **R11** | chart-image only | **0 `<table>` elements, 34 `<img>`**. No numeric accuracy anywhere | CONFIRMED |
| **R13** | n stated, no baseline run | `--limit 250` present (only under `html_text`; tags break it for a literal search), followed by "Here's an example of the resulting scores". Single scores table, quantized model only, no baseline column | CONFIRMED |
| **R14** | no baseline stated, Figure 8 chart only | Quote in the Figure 8 caption over an `<img>`; the figure is the only carrier of the numbers | CONFIRMED, with the §4.2 caveat about where the quote lives |

R04's `n_basis` deserves a note in its favour: it overrides the frozen row's own
n (COCO 5000) with GSM8K 1319, on the stated ground that the frozen n belongs to
the CIDEr claim. That is a defensible reading recorded transparently.

---

## 6. Task and output matching

`n` reconstructs exactly from standard OpenLLM v1 task sizes:

- 6-task (MMLU 14042 + ARC-C 1172 + GSM8K 1319 + HellaSwag 10042 + Winogrande
  1267 + TruthfulQA 817) = **28,659**, matching R10 and R17.
- 7-task (adding MMLU-CoT 14042) = **42,701**, matching R09.

`reported_delta_basis` verified against the archived tables: R09's largest
per-task delta is 0.84 pp on GSM8K-cot (correct), R10's is 1.05 pp on MMLU
(correct), R17's largest is 1.11 pp on ARC-C but it records the 0.15 pp average
(see §4.3). R01's recorded 2.35 pp on ARC-Easy is correct.

**One standing mismatch, already disclosed in the record.** For R09, R10 and R17
the `benchmark` label is `mmlu` while `n` is a pooled multi-task count and the
delta comes from a third task. For R09 and R10 this is inert, since their
discordance tier is `family+bits` and ignores the benchmark. **For R17 it is
load-bearing**: its tier is `bits+benchmark`, so the `mmlu` label selects the
atlas cells supplying its discordance rate, while its n is the 6-task pool and
its delta is the pooled average. Three different task scopes in one row.

R01 carries the same shape and `rev3.notes` says so outright: *"n is PIQA's; the
largest delta is ARC-Easy's."* R17 has no equivalent note.

**Resolution: recommend a note on R17 mirroring R01's**, in the appendix rather
than the sealed CSV, since `notes` is emitted data and editing it would break
reproduction of a released artifact (the R06 precedent). Not applied.

---

## 7. Status and what needs a decision

Nothing in the repository was modified. No frozen file, no sealed CSV, no count.

**Needs Amogh:**

1. **§4.1, R09 and R17 eligibility.** The material one. Same defect class as R10,
   would move eligible 16 → 14 and assessable 11 → 9, and would move the headline
   fraction in the direction favourable to the thesis. Needs a dated amendment
   either way, including a decision to leave them in.
2. **§4.2, R14's figure caption.** Recommend disclose, do not change.
3. **§6, an R17 note** mirroring R01's task-scope disclosure.

**Not done, and why:** the matcher `quote_locate.py` lives in this session's
scratchpad. Committing it to `scripts/` would put it in a fingerprinted tree,
requiring the in-image gate (`207 passed, 0 skipped`), a freeze refresh, and the
expected-count update if it ships with tests. That is a clean piece of work but a
separate commit cycle, and it is a natural companion to
`scripts/fetch_audit_sources.py` for deliverable (D). Ask before doing it.

**Unrelated blocker.** The request to "review the validation-case memo" could not
be actioned: no such document exists in the repository, in `~/scratch/flipeval`,
or in the private sealed copy. Checklist item 10, the J2C-facing validation case,
is listed as **Not started** in `docs/SESSION_HANDOFF_2026-08-02.md` §6.

# Published-Claim Audit Registration

Status: **FROZEN 2026-07-15**, by the commit containing this line — before any
per-claim power computation was run. The claim list itself must also be frozen
(§3.4) before verdicts are computed. Deviations require a dated entry under
Dated Amendments stating whether results were inspected before the decision.

Purpose: systematically assess whether published "near-lossless" compression
claims are statistically supported at their reported evaluation sizes. Framing
is constructive — the field lacks reporting standards; flipeval and the
certification tables are the proposed fix — not an indictment of specific
papers. Every verdict is mechanical and recomputable.

## 1. Disclosure of pre-registration data contact

Five candidate claims were collected with exact quotes on 2026-07-15 (GPTQ,
LLM.int8(), SmoothQuant abstracts; the RedHatAI W4A16 Llama-3.1-8B model card;
Meta's quantized Llama 3.2 blog) during a feasibility sweep. No power
computation has been run on any of them. They enter the pool through the same
§3 criteria as later-collected claims.

## 2. Population and sampling frame (fixed)

Claim sources, enumerated exhaustively within each frame:

- **F1 — Method papers:** the published versions of GPTQ, AWQ, SmoothQuant,
  LLM.int8(), SpinQuant, QuIP#, SqueezeLLM, Wanda, and SparseGPT, plus any paper
  citing one of these that appears in the related-work sweep
  (`docs/related_work_checklist.md`) and makes an equivalence-type claim.
- **F2 — Official quantized model cards:** Meta, Qwen, Mistral, and Red Hat
  AI/Neural Magic quantized releases of models in the Llama-2/3.x and Qwen2.5
  families on Hugging Face.
- **F3 — Inference-stack vendor posts:** vLLM, TensorRT-LLM, and llama.cpp
  official blog/docs pages making quantization-quality claims.

Target: **at least 10** claims; all claims meeting §3 inclusion are audited
(no discretionary sub-selection).

## 3. Claim inclusion and extraction (mechanical)

1. **Inclusion:** the source asserts, in prose or a table caption, that a
   compressed model's benchmark quality is equivalent-or-negligibly-different
   from its uncompressed baseline (trigger vocabulary: "near-lossless",
   "negligible", "no (significant) degradation", "matches", "preserves
   accuracy", "X% recovery" with X ≥ 98, or an explicit ≤1 pp delta framed as
   parity). Perplexity-only claims are included only if a benchmark-accuracy
   claim also appears.
2. **Extraction fields (per claim):** exact quote (≤15 words), source and
   version/date, benchmark(s), reported n per benchmark (as stated, else the
   benchmark's standard size, recorded as `imputed`), reported baseline
   accuracy, reported delta, whether per-item outputs are released, whether
   any statistical test or interval is reported.
3. **Double extraction:** each claim's fields are extracted twice on different
   days (solo-author substitute for dual coding) and discrepancies resolved
   before the verdict stage.
4. **Freeze:** the completed claim table is committed as
   `docs/audit_claim_table.csv` before any verdict is computed. Claims found
   after that commit go into a separately reported "post-freeze" stratum.

## 4. Verdict rules (mechanical, computed only after §3.4 freeze)

For each claim × benchmark, at the claim's reported n and baseline accuracy:

- **V1 — Detection power:** minimum detectable accuracy delta at 80% power,
  two-sided α=0.05, under the paired-flip model with the discordance rate
  imputed from the atlas's empirical flip-rate distribution for the nearest
  (method family, bit width, benchmark) cell — sensitivity-checked against the
  independent-binomial bound. Report MDD/claimed-margin ratio.
- **V2 — Equivalence support:** the n required for TOST at margin
  **2 pp** — matching the registered main-grid TOST margin — (and at the
  claim's own margin when it states one). A claim is
  labeled **"underpowered for its own assertion"** iff reported n < required n
  at the applicable margin.
- **V3 — Reproducibility:** binary — could a third party run a paired test
  from released artifacts (per-item outputs public)?

Headline statistic: the fraction of audited claims labeled underpowered under
V2, reported with its count and the full claim table. No claim is described as
"false" or "wrong"; the audited property is the evidential sufficiency of the
reported evaluation, not the truth of the underlying equivalence.

## 5. Robustness reporting

Verdicts are recomputed under (a) the independent-binomial bound instead of the
atlas-imputed discordance rate and (b) a margin sweep over 1 pp and 3 pp; a claim's
verdict is called margin-sensitive if it changes across the sweep, and the
count of margin-sensitive verdicts accompanies the headline number.

## Dated Amendments

**2026-07-15 — Amendment 1 (§3.3 independence mechanism).** The requirement
that the two extractions occur "on different days" is replaced by an
extractor-independence requirement: the second extraction is performed in a
fresh agent session with **no access to pass-1 outputs** — the extractor is
withheld `docs/audit_claim_table_pass1.csv`, instructed not to read it or
retrieve it from git history, and receives only the frozen protocol and the
source frames. Rationale: temporal separation was a proxy for extractor
independence calibrated to human memory; a fresh agent session carries no
memory of pass 1, so blind same-day extraction provides at least the intended
independence; the source-stability benefit of a second-day fetch is instead
obtained by recording source content hashes in both passes where feasible.
Decision context: made after pass-1 extraction results were known, but before
any verdict, power, MDD, or required-n computation was run; the §4 verdict
rules and the §3.1–3.2 inclusion/extraction rules are unchanged.

**2026-07-31 — Amendment 2 (§4 V2, the applicable margin).**

*Defect.* §4 V2 computes the required $n$ "at margin 2 pp … (and at the claim's
own margin when it states one)". The phrase "when it states one" was never
operationalised in this registration, and §3.2 does not extract a margin: the
frozen claim table `docs/audit_claim_table.csv` has no margin field. The
implementation in `scripts/audit_verdicts.py` supplied one after the freeze, by
taking the largest delta the source reports and treating it as the margin the
source states. Those are different quantities. A reported delta is an outcome of
the evaluation; a margin is a threshold against which an outcome is judged.
Every `margin_basis` value in `results/audit_verdicts_rev2.csv` cites an
observed quantity — for example "max |delta| over the 5 OPT-175B tasks" (R01),
"the larger of the two stated deltas" (R06), "+0.15pp (68.69 vs 68.54)" (R17).
Verdicts labelled "underpowered for its own assertion" therefore rest, for those
claims, on a margin the source did not assert.

*Amendment.* The applicable margin is determined by the following rule, which
replaces the parenthetical in §4 V2. Each audited claim is assigned to exactly
one category:

1. **Formal equivalence claim** — the source states a numeric tolerance that is
   logically prior to the observed result: a threshold that could have been
   written down before the evaluation was run. Qualifying forms include "within
   $X$", "no more than $X$", "at most $X$" used as a requirement, "a tolerance
   of $X$", and equivalent constructions that bound what the source would accept.
2. **Informal near-lossless claim** — the source reports a result and
   characterises it as negligible, but states no threshold prior to it. This
   includes deltas subsequently described as small, recovery percentages
   computed from the result, and phrases such as "at most $X$" used to describe
   the spread of observed differences rather than to set a bound.
3. **Unquantified claim** — the source uses equivalence language without
   sufficient numerical information to evaluate either way. This category does
   not change; it continues to be handled by the §4 indeterminacy rules.

The determination is made against the frozen `exact_quote` for each claim and,
where the quote alone is inconclusive, against the source at the version and
content hash recorded in the frozen claim table. It is recorded per claim, with
the quoted text supporting it, in a new column of the verdicts CSV. **No claim is
re-extracted and no source is re-fetched for extraction purposes**; the frozen
claim table is unchanged. Sources were re-fetched for verification only, under
the eligibility-and-provenance scope recorded below.

Verdicts are then computed as follows:

- The **primary verdict for every claim** is at the registered 2 pp margin,
  which §4 already names first. The headline count is the number of determinate
  claims underpowered at 2 pp.
- A claim in category 1 is **additionally** evaluated at its declared margin,
  reported alongside the primary verdict, and never in place of it.
- Claims in category 2 are reported against the registered 1 pp / 2 pp / 3 pp
  sweep of §5. **No margin derived from a claim's own reported results is
  described as that claim's stated, declared, asserted or own margin**, in the
  paper or in any released artifact.

*Consequential quantities.* Every reported quantity that divides by the
applicable margin is recomputed with it and re-reported: the V1
MDD-to-claimed-margin ratios, the required-$n$-to-reported-$n$ shortfall ratios,
and the §5 margin-sensitivity flag. Values previously reported against a
result-derived margin are withdrawn, not silently updated; both the superseded
and the corrected values remain in the released artifacts.

*Analysis discipline.* The recomputation is run **once**, over the frozen claim
table, and whatever it returns is reported — including if the headline count
falls, rises, or reaches zero. No variant of this rule is constructed after the
recomputed values are seen.

*Eligibility correction (R10).* A full-text review of every source, run
2026-07-31 and recorded in `docs/AUDIT_SOURCE_VERIFICATION_2026-07-31.md`,
established that R10's recorded `exact_quote` — "average recovery percentage
across all benchmarks is 98.6%" — appears nowhere in its source. The card
contains no prose equivalence claim; `98.6%` is a table cell, and the extraction
composed a sentence from tabular data and recorded it as a quotation. §3.1
requires the assertion to appear "in prose or a table caption", and it appears in
neither. **R10 is therefore excluded from the eligible population by applying the
inclusion rule already registered in §3.1, not by any new criterion.** The
eligible population becomes 16. The frozen claim table is not edited; the
exclusion is recorded in the verdicts CSV with the verification finding beside
it, and the original row remains in the immutable frozen file and in the
published v1.0.0 artifact.

This correction moves the eligible denominator. It changes neither the number of
claims below the planning threshold nor the V3 per-item-outputs result: R10 was
adequately powered at the registered 2 pp margin and recorded `no` on V3, so its
removal cannot reduce the count of flagged claims. **The correction did not
improve any count in the direction favourable to the audit's thesis.**

*Scope.* This amendment changes the applicable margin, and reopens §§3.1–3.2
**only** to correct eligibility and provenance — that is, to apply the existing
inclusion rule to R10 and to record source provenance. No inclusion criterion is
added, widened or narrowed, no claim is re-extracted, and no source is re-fetched
for extraction purposes. Unchanged and not reopened: the frozen claim table
itself; the §4 V1 detection-power formula; the §4 V3 reproducibility verdict; the
indeterminacy rules and the claims currently indeterminate; the discordance
imputation and its tier matching; the atlas; and every registration other than
this one.

*Reporting the surviving power result.* The claim below the planning threshold at
the registered 2 pp margin is reported as a **sensitivity-dependent planning
flag, not a stable binary verdict**, and never without its reversal point. The
required $n$ is a planning quantity computed under an assumed true difference of
zero and a point imputation of discordance; for the single flagged claim the
classification reverses at approximately $d = 0.1189$ against an imputed
$d = 0.13$, and 43.6% of the 792 atlas cells supplying that imputation fall below
the reversal point. Any report of this flag states the imputed value, the
reversal point, and that fraction.

*Decision context.* **Results were inspected before this decision, and so was the
full-text classification.** The audit verdicts were computed on 2026-07-20,
revised to rev-2 on 2026-07-21, reported in the paper, and released in the v1.0.0
artifact; the headline $K = 4$ of 12 has been public since 2026-07-30. The
full-text verification of all 17 sources was run on 2026-07-31, **before this
amendment was signed and at the decision owner's direction**, and its
classification of every claim — including the finding that no source declares a
margin — was known at signature. The rule in this amendment was not constructed
against that classification: it was written and committed on 2026-07-31 at
`19d485c`, before the verification ran, and that committed draft names R14 as its
hard case and resolves it by the same priority test the verification later
applied. The rule is unchanged from that commit. The eligibility correction was
made by applying §3.1 as already registered, and is verdict-neutral in the sense
recorded above. The original immutable version of every superseded value remains
accessible in the frozen claim table and the published v1.0.0 artifact.

*Signed.* Amogh Singh, 2026-07-31. Drafted by Claude Code at `19d485c`, revised at `bb45528` after the full-text source verification, and appended on the verbatim instruction "sign and append". The rule in the *Amendment* clause above is unchanged from `19d485c`.

**2026-08-03 — Amendment 3 (§3.1 inclusion, applied to R09 and R17).**

*Occasion.* Amendment 2 excluded R10 from the eligible population by applying
§3.1 as registered: the recorded quotation appeared nowhere in the source, and
the assertion appeared in neither prose nor a table caption. That correction
rested on a full-text review which, as recorded in
`docs/AUDIT_SOURCE_VERIFICATION_2026-07-31.md`, verified quotation *accuracy* for
all seventeen sources but quotation *location* for R10 alone. The remaining
sixteen therefore carried an unexamined §3.1 basis. An author re-verification of
the four claims named in that document's open items, recorded in
`docs/AUDIT_SELF_RECHECK_2026-08-02.md`, examined location directly against the
archived sources.

*Finding.* Three of the six quantized-model cards in the population, R09, R10 and
R17, contain no §3.1 trigger vocabulary anywhere in their prose. In each, the
recovery percentage that would satisfy the trigger list exists only as a table
cell, beneath a column header, and none of the three files contains a table
caption element of any kind. R08, R15 and R16 are unaffected: each states a
recovery percentage in prose at or above the registered threshold of 98. With
respect to those recovery figures R09 and R17 occupy the same structural position
that excluded R10, which is what makes their eligibility a live question. They
differ from R10 in another respect, addressed below.

*Determination.* **R09 and R17 remain in the eligible population.** The ground
for retaining them is that §3.1 does not decide the case, not that it decides the
case in their favour.

§3.1 admits a claim on "an explicit ≤1 pp delta framed as parity". That trigger
has two limbs, and R09 and R17 satisfy the first without satisfying the second.
Each card contains exactly one comparative sentence in prose, and it states both
the compressed and the uncompressed score: 73.44 against 73.79 for R09 and 68.69
against 68.54 for R17, differences of 0.35 pp and 0.15 pp. A delta below one
percentage point is therefore explicit on the face of the prose. Neither sentence
characterises that difference. "Whereas" is a neutral contrastive, no trigger term
appears in the prose of either card, and the recovery figures that would qualify
outright, 99.52% and 99.8%, exist only as table cells beneath a `<th>Recovery`
header in files carrying no table caption element at all. The registration does
not say what follows when a source supplies the quantity and withholds the
characterisation. **That is a gap in a rule §3 declares to be mechanical, and it
was not anticipated when the protocol was frozen on 2026-07-15.**

**R10 is excluded on a ground that does not depend on how that gap is resolved.**
Its card contains no comparative sentence of any kind: the strings "whereas",
"unquantized", "baseline" and "compared" do not occur anywhere in it, its
evaluation section is a single table with no accompanying prose, and the sentence
recorded for it in the frozen claim table was composed from tabular data and
appears nowhere in the source. R10 therefore fails the first limb as well as the
second, and its exclusion under Amendment 2 stands under the strict and the
permissive reading alike. The difference in outcome between R10 and these two
rests on a difference between the documents, not on this determination. Verified
against the sealed source archive `a912a1e7…40259` on 2026-08-03, by a route
independent of the vocabulary sweep recorded in
`docs/AUDIT_SELF_RECHECK_2026-08-02.md` §4.1.

Two resolutions of the gap were therefore available, and both are defensible. The
strict reading requires both limbs and excludes R09 and R17. The permissive
reading treats an explicit sub-point delta, stated in prose in a document whose
function is to offer the compressed model in place of the uncompressed one, as an
assertion of negligible difference in substance, and retains them. **The tie is
broken against the interest of this audit.** The strict reading shrinks the
eligible and assessable populations and raises the proportion of assessable claims
falling below the planning threshold; the permissive reading leaves every
published count exactly where it stands. Where a frozen rule is genuinely silent
and the author is choosing after having seen results, the only choice a reader can
credit without also having to credit the author is the one that cannot improve the
author's own finding. **This is an interpretation of a registered rule that is
silent, not an extension of a rule that speaks**, and it is recorded here so that
a reader sees the reasoning rather than inferring it from a denominator.

*Quantities unchanged.* The eligible population remains 16 and the numerically
assessable population remains 11. No verdict, no threshold classification, no
per-item-outputs result and no imputation changes. The frozen claim table is not
edited.

*The alternative, and its direction.* Excluding R09 and R17 by the strict reading
was available and was declined. It would have moved the eligible population from
16 to 14 and the assessable population from 11 to 9, left the count below the
planning threshold at 1, and moved that count as a proportion of the assessable
population from 9.1% to 11.1%. **That is the direction favourable to this
audit's thesis.** Amendment 2 recorded that the R10 correction did not improve
any count in that direction; this determination likewise does not, and it is the
conservative of the two readings available. The quantities in this paragraph are
recorded so that the choice is auditable rather than merely asserted.

*Reporting.* The locus finding is reported in the paper as a result in its own
right rather than as an eligibility adjustment: across the six cards, with the
underlying evidence held constant, three assert recovery in prose, two state two
scores and characterise neither, and one makes no comparative statement at all.
The consequence reported alongside it is that an inclusion rule keyed to prose,
which §3.1 is, captures equivalence claims non-randomly, so the frozen candidate
count of 17 is a floor on the population rather than a census of it. Any report
of the eligible population states that the boundary cases were retained under
this amendment.

*Verification status.* The locus review supporting this amendment is author
re-verification against archived sources, by a second automated pass of the same
class of tool that produced the record it checked. It is **not** independent
verification, and neither it nor any agreement between it and the 2026-07-15
passes may be reported as dual coding or inter-rater reliability. §3.3 and
Amendment 1 are unchanged.

*Scope.* This amendment applies §3.1 to two claims and records the reasoning. No
inclusion criterion is added, widened or narrowed; no claim is re-extracted; no
source is re-fetched for extraction purposes; the frozen claim table, the §4
verdict rules, the indeterminacy rules, the discordance imputation, the atlas,
and every other registration are unchanged and not reopened. Amendment 2 remains
in force in full.

*Decision context.* **Results were inspected before this decision.** The rev-3
verdicts were computed on 2026-07-31 and the locus classification on 2026-08-02,
and both were known at signature. The determination reached is the one that
leaves every published count where it stood and declines the change that would
have improved the headline proportion. The superseded and the current readings
of §3.1 as applied to R09 and R17 are both recorded above.

*Signed.* Amogh Singh, 2026-08-03. Drafted by Claude Code at `2857cd0`; its *Determination* was redrafted at `adaf263`, after the distinction it rests on was verified directly against the sealed source archive, to concede that §3.1 is silent at this boundary rather than to assert that it is satisfied. Appended on the verbatim instruction "sign it and append".

**2026-08-04 — Amendment 4 (provenance remap; no protocol change).**

*Occasion.* `docs/audit_sources_20260731.tar.gz`, holding the full-text captures
of all seventeen audited sources, entered the repository at `cc357db` and was
never deleted, so every commit from there to HEAD carries it. `origin` is a
public GitHub repository, so pushing any commit in that range publishes the
corpus. That contradicts the redistribution review of 2026-08-02, which found
four of the seventeen carry no grant permitting a third party to republish their
text, and the seven method papers sitting under arXiv's default licence, which
authorises arXiv to distribute them rather than authorising us to. It also
contradicts `README.md`, which states the captures are not redistributed. The
repository has therefore been unpushable since 2026-08-02, and the resolution of
record was to leave it so.

*Finding.* Removing the blob rewrites 54 commits. `bb45528` is one of them, and
Amendment 2 cites it in its own signature line above. The rewrite was computed
on a throwaway clone and verified there before this amendment was drafted: 251
commits before and after with nothing pruned, author, email, date and subject
byte-identical for every commit, and the only tree difference across the entire
range the removed tarball. `19d485c`, also cited in that signature line, is an
ancestor of `cc357db` and does not change. `987377a`, tag `v1.0.0`, is likewise
an ancestor, so the release tag and its Zenodo archive lie outside the rewrite.
The private sealed copy hashes
`a912a1e7af0efd58459dcf57ade84be96cfea8337147a13d336dacfdb9240259`, identical to
the blob in git, so removal loses nothing.

*Determination.* **The tarball is removed from the repository's history, and
`bb45528` is superseded by `ed92ae8` on the record rather than in the text.**
The corpus remains identified and digest-checkable: the `.sha256` and
`docs/audit_sources_manifest.tsv` are retained, and
`scripts/fetch_audit_sources.py` rebuilds it from each publisher. The signature
line of Amendment 2 is to be read as citing `ed92ae8` wherever it cites
`bb45528`, and the full mapping at
`docs/audit_source_tarball_hash_map_20260804.tsv` governs any other stale
identifier. **The original text of Amendment 2 is not edited.** The superseded
identifier stays exactly as signed, because correcting it in place would leave a
record reading as though the chain never broke, and that it broke is what this
amendment exists to preserve.

*The alternative, and its direction.* The alternative was abandoning the rewrite
and never pushing, which was the resolution of record from 2026-08-02. It is
rejected because it makes the repository permanently unpublishable, and the
artifact link in a submitted paper cannot point at a repository that does not
exist. The cost of the rewrite is borne once and is documented in the mapping
file; the cost of not pushing recurs indefinitely. What the rewrite concedes is
that it is irreversible once pushed, and that 54 commit hashes cited anywhere
outside the mapping file go stale without warning.

*Quantities unchanged.* No inclusion rule, eligibility rule, verdict rule,
indeterminacy rule, discordance imputation, denominator or count is reopened.
The eligible population remains 16. Amendments 1, 2 and 3 remain in force in
full, and every published number stands.

*Scope.* This amendment records a change to commit identifiers and to what the
repository distributes. It changes no analysis and no audited property.

*Decision context.* **Results were inspected before this decision.** The rev-3
verdicts were computed on 2026-07-31, the locus classification on 2026-08-02,
and Amendment 3 was signed on 2026-08-03; all were known at signature. This
amendment changes no analysis, no count and no verdict, so there is no outcome
for that knowledge to have biased. It is recorded because the standing
requirement applies to every amendment to a frozen protocol, not only to those
that could move a number.

*Signed.* Amogh Singh, 2026-08-04. Drafted by Claude Code at `df1615b` after the rewrite was computed and verified on a throwaway clone; its *Determination* and *Decision context* were completed on the verbatim instruction "i read the draft, fill in the two sections as approved and append". The rewrite itself was not applied at the time of signature.

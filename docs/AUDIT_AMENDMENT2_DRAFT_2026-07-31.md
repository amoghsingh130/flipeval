# DRAFT — Audit Registration, Amendment 2 — UNSIGNED

**Status: DRAFT. Not in force. Not appended to any frozen file.**

Drafted by Claude Code, 2026-07-31, at Amogh's request, following the precedent
of `docs/BRIDGE_DECISION_RECORD_2026-07-20.md` ("drafted by Claude Code; signed
by Amogh Singh"). Under `CLAUDE.md`, amendments to frozen protocols are written
by the human. This file is a draft for review only. **Nothing in it takes effect
until Amogh signs it and the amendment text is appended to
`docs/AUDIT_REGISTRATION_2026-07-15.md` under its "Dated Amendments" heading.**

**Revised 2026-07-31, after the full-text source verification.** The original
draft recorded that no classification had been computed and that the impact on
`K` was deliberately unknown. **Both of those statements are now superseded and
must not be restored.** At Amogh's direction the full-text verification of all 17
sources was run before signature
(`docs/AUDIT_SOURCE_VERIFICATION_2026-07-31.md`, commit `cc357db`), so the
classification is known: 0 sources declare a prospective margin, 7 describe an
observed delta, 10 use a generic adjective. `K` at the registered 2 pp margin was
already public in the v1.0.0 artifact as the secondary reading.

**The RULE in Part 1 is unchanged from commit `19d485c`**, which predates the
verification. That is what the *Decision context* paragraph rests on, and it is
checkable in git. Changing the rule now would forfeit it.

Still true: no recomputation of the verdicts has been run.

This file has two parts. **Part 1 is the amendment text**, written to be
appended verbatim. **Part 2 is reviewer's notes** — the choices behind the
draft and the alternatives rejected. Part 2 is *not* part of the amendment and
is not appended.

---

## Part 1 — Amendment text (append this, verbatim, and nothing else)

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
the quoted text supporting it, in a new column of the verdicts CSV. **No source
is re-fetched and no claim is re-extracted**; §§3.1–3.2 and the frozen claim
table are unchanged.

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

---

## Part 2 — Reviewer's notes (NOT part of the amendment; do not append)

### The four choices this draft makes for you

**1. The test for "declared" is priority, not phrasing.** The draft asks whether
the number could have been written down before the evaluation ran. The
alternative — a keyword list — fails on R14, whose source says "at most 0.7
points" in what appears to be a description of observed spread rather than a
bound. A keyword test would admit it; a priority test makes you look at what the
sentence is doing. The cost is that the test needs a judgement per claim, which
is why the draft requires the supporting quote to be recorded per claim.

**2. The primary headline moves to the uniform 2 pp margin.** This is the
draft's biggest substantive choice. The argument for it: §4 names 2 pp *first*
and calls it "matching the registered main-grid TOST margin"; the own-margin
clause is parenthetical. Reverting to 2 pp as primary is therefore the most
faithful available reading of the frozen text, it requires no new analysis, and
the value is already computed (`verdict_at_registered_2pp`) and already public
as the paper's secondary reading.

You should know what this costs before signing: the paper currently leads with
$K = 4$ of 12, and the 2 pp reading has been reported throughout as $K = 1$ of
12. If you sign this, expect the audit's headline underpowering count to fall to
roughly that, and the "$2.0\times$ to $12.9\times$" shortfall range to change or
disappear.

**Updated 2026-07-31 — the power result should not be the headline.** With the
eligibility correction the count is 1 of 11 assessable claims, and it is not
robust: it reverses at $d \approx 0.1189$ against an imputed $d = 0.13$, with
43.6% of the 792 supporting atlas cells below that point (IQR $[0.088, 0.280]$,
a threefold span). **The two readings are also nearly disjoint, not nested** —
the four claims flagged under the old result-derived margins (R06, R07, R15,
R17) are all adequately powered at 2 pp, and R01, which is flagged at 2 pp, was
adequately powered under its own derived margin. Amogh's chosen ordering,
2026-07-31, is to lead with the reporting findings and place the power flag
beneath them:

1. 0 of 16 reported an a priori numerical equivalence margin.
2. 0 of 16 released per-item outputs for the tasks supporting the claim.
3. 5 of 16 cannot be assessed under the registered binary paired-outcome framework.
4. 1 of 11 assessable claims below the planning threshold under point imputation,
   reversing to 0 under plausible sensitivity.

The instability in (4) is evidence for the certification argument, not a defect
to be minimised: it is precisely what a point imputation of a nuisance parameter
does to a binary verdict.

**Two of the audit's three headlines are untouched.** $J = 5$ indeterminate
depends on absent inputs, not margins. **$V3 = 0$ of 17 releasing per-item
outputs** — the finding the paper itself calls the most actionable — does not
involve a margin at all. The audit does not collapse; its power result gets
smaller and better founded.

*Alternative, if you prefer:* report the three categories separately with no
single $K$. More faithful to the advisor's suggestion, less quotable, and it
means the abstract needs restructuring rather than renumbering.

**3. Superseded values are withdrawn, not overwritten.** The v1.0.0 Zenodo
artifact (`10.5281/zenodo.21708923`) is public and contains the current
verdicts. Keeping both sets in the released artifacts is what lets the paper and
the citable record disagree without either being wrong. See the open item below.

**4. One-run discipline, mirroring H3.** Included so the recomputation cannot
become an iterative search for a better headline. This is the same protection
the H3 analysis had and it is worth repeating here explicitly.

### What this draft deliberately does not do

- It does not classify any of the 17 claims. That is the recomputation's output,
  and doing it here would let the rule be tuned to the classification.
- It does not touch the discordance imputation, which is a separate item in the
  same review (imputation uncertainty, cluster dependence). Fold those in and
  this stops reading as a correction and starts reading as a re-analysis.
- It does not revisit R04. The metric-incompatibility ruling stands on its own
  grounds.

### Open item you must settle separately

The published artifact will disagree with the revised paper. Two options: cut a
v1.1 release with the recomputed CSV and cite the new version DOI, or keep
v1.0.0 as cited and add an explicit note in the artifacts section mapping which
figures come from which version. This is not part of the amendment, but it
becomes live the moment the amendment is signed.

### To put this in force

1. Review Part 1. Change any wording you disagree with — it is your text, not
   mine, and the four choices above are recommendations, not defaults.
2. Append the final Part 1 text under "Dated Amendments" in
   `docs/AUDIT_REGISTRATION_2026-07-15.md`. Append only; edit nothing above it.
3. Sign it (the convention elsewhere in this repo is a dated signature line in
   the commit message and the record).
4. Tell me, and I will run the recomputation once and carry every downstream
   number, table and sentence with it.

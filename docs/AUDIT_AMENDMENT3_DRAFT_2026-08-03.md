# Audit Registration, Amendment 3 (DRAFT, UNSIGNED)

Drafted by Claude Code, 2026-08-03, at Amogh's direction, following the
precedent of `docs/AUDIT_AMENDMENT2_DRAFT_2026-07-31.md`. Under `CLAUDE.md`,
amendments to frozen protocols are written by the human. **This file is a draft
for review only. Nothing in it takes effect until Amogh signs it and Part 1 is
appended to `docs/AUDIT_REGISTRATION_2026-07-15.md` under its "Dated Amendments"
heading.**

Direction chosen by Amogh, 2026-08-03: **R09 and R17 remain eligible.** The
alternative was quantified before the choice was made and is recorded in Part 1
so that a reader can see the road not taken.

**Results were inspected before this decision.** So was the locus classification
it rests on. The *Decision context* clause states this and must not be softened.

---

## Part 1: the amendment text, for appending verbatim

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
recovery percentage in prose at or above the registered threshold of 98. R09 and
R17 therefore occupy the same structural position that excluded R10.

*Determination.* **R09 and R17 remain in the eligible population.** They are
distinguished from R10 on a ground internal to §3.1 rather than by any new
criterion. R10 contains no comparative sentence at all: there is no prose
assertion to construe, permissively or otherwise, and the recorded quotation was
composed from tabular data. R09 and R17 each contain a comparative sentence in
prose which states both the compressed and the uncompressed score explicitly,
and the difference so stated is 0.35 pp and 0.15 pp respectively, each below one
percentage point. §3.1's trigger list admits "an explicit ≤1 pp delta framed as
parity", and in a document whose stated purpose is to offer the quantized model
in place of the unquantized one, a bare juxtaposition of two scores under a point
apart is an assertion of parity in substance. The judgement is that the framing
requirement is met by the document's function where it is not met by its
vocabulary. **This is an interpretation of the registered rule, not an extension
of it**, and it is recorded here because the same rule was applied strictly to
R10 and a reader is entitled to see why the two outcomes differ.

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

*Signed.* Amogh Singh, 2026-08-03.

---

## Part 2: notes for review, not for appending

**Why this needed an amendment at all, given nothing moves.** Amendment 2's
*Scope* clause reopens §§3.1 to 3.2 "only to correct eligibility and provenance,
that is, to apply the existing inclusion rule to R10". Applying the same rule to
two further claims, even to reach "no change", falls outside that authorisation.
Leaving it unrecorded would also leave the asymmetry with R10 discoverable but
unexplained, which is worse than either answer.

**The load-bearing sentence** is the R10 distinction: no comparative sentence
exists in R10, so there is nothing to construe. If a reviewer rejects that
distinction, the fallback is not to reverse this amendment but to report both
readings, since the strict reading changes no verdict and only the denominators.

**What to check before signing.**

1. Part 1 says "remain eligible" and never "are re-included". They were never
   removed; nothing is being restored.
2. The 9.1% and 11.1% figures are stated as the declined alternative, not as
   results.
3. The verification-status paragraph must survive editing intact. It is the
   clause that prevents the whole self-recheck being read as independent
   verification.

**On appending.** Part 1 only, byte-identically, under "Dated Amendments" in
`docs/AUDIT_REGISTRATION_2026-07-15.md`, with the append verified to have changed
no line above it, as was done for Amendment 2. `docs/PREPACE_FREEZE.json` does
not cover that file, so no freeze refresh applies; `paper/tools/
verify_registrations.py` **does** reproduce the registration into
`appendix_registrations.tex`, so that appendix must be regenerated in the same
commit or the gate will fail, exactly as it did silently after Amendment 2.

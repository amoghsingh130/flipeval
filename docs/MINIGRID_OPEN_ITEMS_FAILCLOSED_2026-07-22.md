# Open implementation items vs. the mini-grid validator

Discharges **ruling 6 of 2026-07-21**: enumerate the open implementation items
and confirm the mini-grid validator fails closed on every one, before any eval
job is submitted. Builds proceed meanwhile, per the same ruling.

The enumeration is taken from `configs/main_grid_manifest.yaml`
`implementation_status` (frozen data) rather than from prose, and the
"fails closed" column is backed by a test, not an assertion.

## The five open items

| item | manifest status | in mini-grid scope? | validator behaviour | test |
|---|---|---|---|---|
| `rtn_builder` | `not-implemented` | no — mini-grid is GPTQ/AWQ | rejects any method whose family is outside `{gptq, awq}`, naming rtn/wanda | `…rejects_an_unimplemented_method_family[rtn]` |
| `wanda_builder` | `not-implemented` | no | same check | `…rejects_an_unimplemented_method_family[wanda]` |
| `arc_challenge_loader` | `not-implemented` | no — mini-grid is MMLU/GSM8K | rejects any task outside `{mmlu, gsm8k}`, naming arc/hellaswag | `…rejects_an_unimplemented_task[arc_challenge]` |
| `hellaswag_loader` | `not-implemented` | no | same check | `…rejects_an_unimplemented_task[hellaswag]` |
| `real_wikitext2_artifact_preflight` | `blocked-zero-of-36718-rows-…` | no — mini-grid is C4-only | rejects any calibration set that is not `allenai/c4` | `…rejects_a_wikitext2_calibration_set` |

Two further scope boundaries are guarded the same way, because they are deferred
rather than unimplemented and would otherwise be reachable by a config edit:

| boundary | validator behaviour | test |
|---|---|---|
| 3-bit dose-response (deferred with the main grid) | rejects `calibration.bits != 4` | `…rejects_three_bit` |
| 5 calibration seeds (registered `{0,1,2,3,4}`) | rejects any other seed set | `…rejects_a_reduced_seed_set` |

`real_c4_artifact_preflight` was `requires-pace-storage-and-runtime` and is now
**satisfied**: all 10 artifacts exist and passed structural validation (job
`11339076`, 0 failures). It is not a gap.

`gptq_builder`, `awq_builder` and `hierarchical_bootstrap` are
`implemented-local-tests` and are exercised by this grid.

## Why these checks were added rather than assumed

Before this change the gaps were unreachable only *incidentally* — the config
happened not to name them. A config edit routing the grid into an unimplemented
builder or loader would have surfaced as a `KeyError` on a missing expected
count, or as an empty output file, rather than as a scope violation. Incidental
safety is not fail-closed. Each gap is now rejected **by name**, with the
message pointing at `configs/main_grid_manifest.yaml`.

## The staleness guard

`test_the_open_items_are_still_the_ones_these_tests_cover` reads
`implementation_status` and asserts the open set is exactly the five above. If
an item is implemented, or a new gap appears, that test fails and forces this
document and the validator's scope constants to be revisited. The guard exists
because a hand-maintained list of "things to check" silently rots, and a rotted
scope guard is the same failure class as a stale gate expectation.

The validator's `IMPLEMENTED_TASKS` / `IMPLEMENTED_METHOD_FAMILIES` constants
are likewise cross-checked against the manifest by
`test_validator_scope_matches_the_implemented_surface`, so the literals in code
cannot drift from the frozen data.

## Nothing here needs a ruling

Every open item is out of mini-grid scope by the frozen registration, and each
now fails closed by name. No item blocks eval submission; none required a
judgement call.

**Gate:** in-image suite **170 passed, 0 skipped, 0 failed** (job `11347835`).

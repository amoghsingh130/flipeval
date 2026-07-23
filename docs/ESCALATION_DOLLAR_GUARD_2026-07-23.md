# Escalation Stage — Dollar Guard (2026-07-23)

Condition 2 of Amogh's budget confirmation: translate the escalation-stage plan
into dollars against the charge account's actual balance, keep **≥ $75**
unspent as a post-campaign reserve, and stop-and-report rather than trim scope
if the projection breaks the reserve. This record is the pre-mass-submission
check; it is refreshed if the generation-speed probe (condition 1) moves the
A100-hour total.

## Balance (measured)

`pace-quota`, 2026-07-23, account `paceship-compressedlm`:

| | dollars |
|---|---|
| Balance | 966.81 |
| Reserved | 0.00 |
| **Available** | **966.81** |

## Rate (empirical, not quoted)

The A100 partition bills on the GPU alone: `TRESBillingWeights=gres/GPU=10261`
(`scontrol show partition gpu-a100`), CPU and memory carry zero weight there.
The realized rate is backed out from this campaign's own spend rather than a
rate card:

- Spent to date: $1000.00 − $966.81 = **$33.19**.
- Inferno GPU-hours behind that spend: **79.5 A100-h** across 97 inferno GPU
  jobs (`sacct` since 2026-07-15, GPU-allocated, inferno QOS).
- **Effective rate: $33.19 / 79.5 = $0.4175 / A100-h**, consistent with PACE's
  published ~$0.40. Used at $0.4175, which slightly overstates the GPU rate
  (some of the $33.19 was CPU-inferno calibration), so the projection is
  conservative.

CPU-inferno (calibration must use inferno — `embers` MaxWall is 8 h and
`prepare_calibration.sbatch` needs 48 h): an 8-CPU job on `cpu-small`
(`CPU=252`) costs `8×252/10261 × $0.4175 = $0.082/h`.

## Projection

| item | A100-h | $ |
|---|---|---|
| A100 work at plan estimate | 320 | 133.6 |
| A100 work at hard bound | 360 | 150.3 |
| Calibration (10 × ~20 h × 8 CPU, inferno) | — | 16.4 |

| scenario | total $ | balance after | reserve floor | headroom above floor |
|---|---|---|---|---|
| plan (320 A100-h) + calibration | **150.0** | 816.8 | 75 | **741.8** |
| hard bound (360 A100-h) + calibration | **166.7** | 800.1 | 75 | **725.1** |

## Verdict

**PASS with wide margin.** Even at the hard 360 A100-h bound plus all
calibration, projected spend is **~$167**, leaving **~$800** — about $725 above
the $75 reserve floor. The dollar guard does not bind this stage; the binding
constraint is the 360 A100-h ceiling itself, which condition 1's
generation-speed probe protects directly.

The reserve is preserved for exactly what the ruling names: validator reruns,
any Amendment-class correction, and the harness study's remainder. No scope
change is implied or taken — scope of the frozen 8-cell design is Amogh's.

## What could move this

Only an A100-hour total materially above 360 would threaten the reserve, and
that would breach the hour bound first — a stop-and-report condition in its own
right (condition 1). Concretely, the reserve floor of $75 is not reached until
roughly **(966.81 − 75) / 0.4175 ≈ 2,136 A100-h**, ~6× the hard bound. There is
no realistic path from this plan to the reserve.

## Provenance

Balance: `pace-quota` 2026-07-23. Rate: `sacct` inferno GPU-hours since
2026-07-15 against the $33.19 delta from $1000. Partition weights:
`scontrol show partition gpu-a100 / cpu-small`. Refreshed if condition 1 revises
the A100-hour total.

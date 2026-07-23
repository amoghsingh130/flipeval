# Escalation Stage — Llama-3.1-8B Access Status (2026-07-23)

Tracks the one external blocker on the Llama-8B half of the escalation. The
Qwen-7B half is unblocked and proceeding.

## Timeline

- **First contact (job `11378480`).** The generation-speed probe 403'd on
  `meta-llama/Llama-3.1-8B-Instruct`: "restricted and you are not in the
  authorized list." 3.2-3B (the whole mini-grid) works with the same token.
- **Amogh accepted the license** on his HF account, 2026-07-23.
- **Re-probe (job `11380267`), still 403.** Metadata resolves (`gated=manual`);
  the actual file download of `config.json` at the pinned revision fails with
  `GatedRepoError 403`.

## Diagnosis (job `11380xxx`, token-scope check)

The deployed token is **fine-grained** (`whoami` → `role: fineGrained`, user
`AmoghSingh123`), and **the same token downloads gated `meta-llama/Llama-3.2-3B-Instruct`
files successfully right now.** So the token's gated-repo read permission is
functional — it is not globally broken, and this is not a plain "token lacks
gated-repos scope" fault.

That leaves two candidates, and the deciding evidence is on Amogh's side (the
model page), per his own heuristic:

1. **Meta grant still pending.** Meta approves 3.1 access manually and it can lag
   the license click by minutes to hours. If the 3.1-8B model page shows
   **pending/under review**, this is the cause — wait and re-probe.
2. **Fine-grained token does not include 3.1-8B.** Fine-grained tokens grant
   gated access per an explicit repo allowlist (or a blanket "all gated repos
   you can access" scope). Since 3.2-3B works but 3.1-8B does not on the same
   token, if the model page shows **granted**, the token is the problem: 3.1-8B
   must be added to the token's permitted repositories, **or** the token's scope
   set to "Read access to contents of all repos you have access to" and the
   token value redeployed to `$HF_TOKEN`.

**The distinguishing check is Amogh's:** open
`https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct`.
- page = *pending* → Meta side; re-probe on his word.
- page = *granted* + still 403 → the **fine-grained token scope** is the cause
  (candidate 2), because the token demonstrably reads other gated Meta repos.

## Action

- Qwen-7B half proceeding (seed-0 calibration `11380274` running).
- Re-probe on Amogh's word (`llama_access_reprobe.sbatch`, which now downloads a
  real file at the pinned revision, not just metadata).
- On a pass: run the Llama generation-speed measurement to complete
  `docs/ESCALATION_GENSPEED_2026-07-23.md`, then bring the Llama half in behind
  its own canary.

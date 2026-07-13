# Running the pilot on PACE-ICE

## 0. One-time: get the code + env onto ICE

```bash
ssh <gtusername>@login-ice.pace.gatech.edu

# Put the repo on scratch (home quota is small; models/datasets are large).
cd ~/scratch
git clone <your-repo-url> Critiquing-Ranking-Quantized-LLMs   # or rsync it up
cd Critiquing-Ranking-Quantized-LLMs

module load anaconda3
conda create -y -n crql python=3.11
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate crql
pip install -r requirements.txt
pip install auto-gptq autoawq          # the quantization backends
```

If your repo lives somewhere other than `~/scratch/Critiquing-Ranking-Quantized-LLMs`,
set `PROJECT_DIR` at the top of `env.sh` (or export it before `sbatch`).

## 1. Build quantized checkpoints (GPU array job)

Builds all 6 checkpoints the pilot config expects (gptq/awq × seed 0,1,2), one GPU each:

```bash
cd ~/scratch/Critiquing-Ranking-Quantized-LLMs
sbatch scripts/slurm/build_quantized.sbatch
squeue --me
```

Outputs land in `outputs/quantized/`. Logs in `logs/build_<jobid>_<arrayidx>.{out,err}`.

## 2. Run the pilot + analysis (GPU job)

Blocks until the builds exist (the script checks and exits early if any are missing):

```bash
sbatch scripts/slurm/run_pilot.sbatch
```

Or chain it so it starts automatically after the builds finish:

```bash
BUILD=$(sbatch --parsable scripts/slurm/build_quantized.sbatch)
sbatch --dependency=afterok:$BUILD scripts/slurm/run_pilot.sbatch
```

Results: `results/qwen25_1p5b_pilot/*.jsonl`, `pair_summary.csv`, `rank_instability.csv`.

## Before you burn a full GPU allocation

Smoke-test the plumbing on a short interactive session first — cheaper than a bad batch job:

```bash
salloc --gres=gpu:1 --cpus-per-task=8 --mem=16G --time=00:30:00
source scripts/slurm/env.sh
python -m pilot_eval.run --config configs/smoke_tiny.yaml
python -m pilot_eval.analyze --run-dir results/smoke_tiny --baseline fp16 --bootstrap 100
```

## Knobs you may need to set

- **Account**: if ICE rejects the job for a missing account, add `#SBATCH -A gts-<PI>-ice`
  (or your class/PI account) to both sbatch files. Check with `pace-quota` / `sacctmgr`.
- **GPU type**: default is any available GPU. To pin one, add e.g.
  `#SBATCH --gres=gpu:V100:1` or a `--constraint=`. `sinfo -o "%N %G"` lists what's free.
- **Walltime/mem**: 1.5B fits comfortably in 48G RAM + one GPU. Bump `--time` if the
  GSM8K generation pass (256 new tokens × 200 items × 6 methods) runs long.
- **HF auth**: Qwen2.5-1.5B is open, so no token needed. If you swap in a gated model,
  `huggingface-cli login` once (token is cached under `HF_HOME` on scratch).

## Sanity checks

- `env.sh` prints the GPU name and `torch.cuda.is_available()` at the top of every job —
  confirm it says `True` and names a GPU, not `no-gpu`.
- Per PILOT.md, freeze prompts/decoding/extraction before the real run, and use the full
  item counts (MMLU 100/subject, GSM8K 200) so bootstrap rank flips aren't toy-sample noise.

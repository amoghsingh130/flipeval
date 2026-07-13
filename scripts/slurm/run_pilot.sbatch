#!/bin/bash
#SBATCH --job-name=crql-pilot
#SBATCH --output=logs/pilot_%j.out
#SBATCH --error=logs/pilot_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --gres=gpu:1
#SBATCH --time=04:00:00
# Add your instructional account if required, e.g.:  #SBATCH -A gts-<PI>-ice

source "$(dirname "$0")/env.sh"
mkdir -p logs

# Fail early if the quantized checkpoints the pilot config expects are missing.
for m in gptq awq; do for s in 0 1 2; do
  d="outputs/quantized/qwen25-1p5b-${m}4-seed${s}"
  if [ ! -d "$d" ]; then
    echo "MISSING checkpoint: $d -- run build_quantized.sbatch first" >&2
    exit 1
  fi
done; done

srun python -m pilot_eval.run --config configs/pilot_qwen_1p5b.yaml
python -m pilot_eval.analyze --run-dir results/qwen25_1p5b_pilot --baseline fp16 --bootstrap 2000

echo "Pilot complete. See results/qwen25_1p5b_pilot/"

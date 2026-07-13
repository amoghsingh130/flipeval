#!/bin/sh
set -eu

cd /workspace
python -m pytest -q
mkdir -p /kaggle/working/results
python -m pilot_eval.run --config configs/kaggle_smoke_tiny.yaml
python -m pilot_eval.analyze \
  --run-dir /kaggle/working/results/kaggle_smoke_tiny \
  --baseline fp16 \
  --bootstrap 100

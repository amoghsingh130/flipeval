# End to end with lm-evaluation-harness

This directory holds a runnable version of the workflow the paper proposes:
evaluate two models on the same items, then report the five lines instead of a
net accuracy delta.

It runs with **no GPU, no model download and no harness install**. The fixture in
`runs/` is laid out exactly the way `lm_eval --log_samples` lays out its output,
so the commands below are the ones you would run against real harness output,
unchanged.

## What is here

```
examples/
  make_fixture.py                      regenerates runs/ deterministically
  runs/fp16-baseline/synthetic__model/samples_mmlu_<ts>.jsonl
  runs/gptq-4bit/synthetic__model/samples_mmlu_<ts>.jsonl
```

The fixture is a **simulation**, drawn from a fixed seed to show the shape the
toolkit measures: a small net delta sitting on much larger per-item churn. It is
not a measurement of any model, and no number in the paper comes from it.

## 1. Produce the two per-item files

With a real model pair, this is the only step that needs a GPU. Run the harness
twice on the same task with `--log_samples`, changing nothing but the model:

```bash
lm_eval --model hf --model_args pretrained=$BASELINE \
        --tasks mmlu --log_samples --output_path runs/fp16-baseline

lm_eval --model hf --model_args pretrained=$COMPRESSED \
        --tasks mmlu --log_samples --output_path runs/gptq-4bit
```

Two things matter for the comparison to be paired at all: **the same task and
the same items on both sides**, and `--log_samples`, without which the harness
reports only the aggregate and the per-item evidence is gone.

FlipEval reads the v0.4.x sample schema, and accepts either a samples file or
the output directory. Loglikelihood tasks (MMLU-style) and generative tasks
(GSM8K-style) are both handled: for the first the prediction is the argmax over
the choice loglikelihoods, for the second it is the harness's own filtered
answer, so scoring stays the harness's decision rather than becoming ours.

## 2. Emit the five-line report

```bash
flipeval report runs/fp16-baseline runs/gptq-4bit \
    --format lm-eval --margin 0.02 --benchmark mmlu
```

Against the fixture in this directory, that prints:

```
FlipEval five-line report
  baseline : runs/fp16-baseline
  candidate: runs/gptq-4bit
  items    : 400 (paired on item_id)

1. Margin declared: equivalence is claimed within +/-2.00 pp of accuracy, tested at
   alpha = 0.05.
2. Paired equivalence test at that margin: TOST says NOT EQUIVALENT (p_low = 0.2198,
   p_high = 0.09899; equivalence requires both < 0.05). Exact McNemar p = 0.8974 on 31
   harmful and 29 beneficial discordant pairs; failure to detect a difference is not
   equivalence and is not reported as one.
3. Churn beside net delta: net accuracy delta -0.50 pp, accuracy-state churn 15.00 pp
   (7.75 pp correct->wrong, 7.25 pp wrong->correct), answer churn 26.50 pp.
4. Sample size: 400 items evaluated against 2164 required by mmlu at +/-2 pp, median of
   the churn observed across 1311 atlas cells (results/certification_tables_rev2.csv);
   SHORT by 1764 items. The requirement is a planning count at an assumed true
   difference of zero, so it is a lower bound.
5. Per-item outputs: NOT DECLARED. This line is the one the tool cannot verify for you;
   publish the two per-item files and pass --per-item-outputs <location> to record where
   they are.
```

Read line 3 against line 2. The two models differ by **half a point** in
aggregate, and disagree on **15% of individual items**. The net delta is what is
left after 7.75 points of correct-to-wrong and 7.25 points of wrong-to-correct
cancel, and it is not a summary of either.

Read line 4 against line 1. Four hundred items cannot certify a two-point margin
on MMLU, so no equivalence claim is available from this evaluation whatever the
delta looks like. That is a property of the evaluation, not of the model.

Line 5 stays unmet until you publish the per-item files and say where:

```bash
flipeval report runs/fp16-baseline runs/gptq-4bit --format lm-eval \
    --benchmark mmlu --per-item-outputs https://example.org/my-release
```

The tool cannot verify a release, so it never treats silence as compliance. Of
the eligible sources the paper audits, none releases task-matched per-item
outputs; this line is the one the field currently does not meet.

Add `--json` for the same content as a machine-readable object, and `--output
FILE` to write it alongside stdout.

## 3. Size the next evaluation

Before running anything, find out what the margin you intend to declare will
cost:

```bash
flipeval required-n --benchmark mmlu --margin 2.0
```

```
benchmark family     mmlu
margin               +/-2 pp
atlas cells          1311

Required n (paired TOST, one-sided alpha=0.05, 80% power, true difference zero)
  p25  churn 0.0926   n 1432
  med  churn 0.1400   n 2164
  p75  churn 0.2591   n 4005

selected (median)    2164 items
ignoring pairing     7727 items (3.57x more at the median)

source               <installed>/flipeval/data/certification_tables_rev2.csv
These are design tables: meeting the count makes the test informative, and
the test still has to be run and to pass.
```

`flipeval required-n --list` gives the families the table covers. The margin is
in **percentage points** here (`--margin 2.0`), while `flipeval report` and
`flipeval compare` take the same quantity as a **proportion** (`--margin 0.02`),
because they compare it against accuracies; both range-check the argument and
say which unit they wanted.

The cost is quadratic in the margin: certifying parity within 1 pp costs four
times what 2 pp costs. Picking the margin is therefore the decision that sets
the budget, and it has to be made before the evaluation rather than after it.

For a benchmark with no row in the table, measure churn on your own pair and
call the formula directly:

```python
from flipeval.certification import required_n_from_discordance
required_n_from_discordance(0.15, margin_pp=2.0)   # -> 2319
```

## As a library

```python
from flipeval import five_line_report
from flipeval.io import from_lm_eval_harness

report = five_line_report(
    from_lm_eval_harness("runs/fp16-baseline"),
    from_lm_eval_harness("runs/gptq-4bit"),
    margin=0.02,
    benchmark="mmlu",
)
print(report.to_text())
report.to_dict()            # every number behind the block
report.meets_required_n     # False here: 400 items against 2,164
```

## Regenerating the fixture

```bash
python3 examples/make_fixture.py
```

Deterministic: re-running it produces byte-identical files.

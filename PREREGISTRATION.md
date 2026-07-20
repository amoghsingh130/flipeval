# FlipEval Main-Grid Pre-Registration

Changelog: 2026-07-11 — resolved all TBDs and tightened the H3 decision rules prior to any main-grid execution; frozen by the commit containing this line.

Created: 2026-07-10. Status: locked before the first main-grid job.

After the first main-grid job starts, this file will not be edited. Any deviation or clarification will be appended under **Dated Amendments**, with its date, rationale, and whether results were inspected before the decision.

## Claims

- **H1 (net vs gross):** aggregate accuracy delta measures NET change and can be near zero because harmful and beneficial flips cancel, while GROSS behavioral churn on the same inputs stays large. Different quantities; report both.
- **H2 (underpowered, unstable ranking):** at common benchmark sizes, power to detect degradation and to order methods is low; rankings shift under resampling, seed, and calibration data.
- **H3 (calibration-seed instability, the "spike"):** the calibration set used to fit the quantizer may change the method ranking as much as or more than the choice of method. If true, current single-run compression comparisons are effectively not reproducible. THIS is the potential main-track-caliber finding and the thing to hunt hardest in the pilot.

## Experimental Grid

Models:

- Qwen2.5-1.5B-Instruct
- Qwen2.5-7B-Instruct
- Llama-3.2-3B-Instruct
- Llama-3.1-8B-Instruct

Llama-3.2-3B-Instruct is used rather than the 1B model because near-floor GSM8K accuracy at 1B would make flip analysis degenerate and leave insufficient performance headroom across the four benchmarks.

Compression cells:

- RTN at 4 and 3 bits; seed-free control
- GPTQ at 4 and 3 bits; calibration seeds `{0, 1, 2, 3, 4}` per model/bit cell
- AWQ at 4 and 3 bits; calibration seeds `{0, 1, 2, 3, 4}` per model/bit cell
- Wanda at 2:4 sparsity; calibration seeds `{0, 1, 2, 3, 4}`. Wanda is selected for its lower checkpoint-construction cost, documented implementation, and calibration dependence. SparseGPT is an explicitly out-of-scope pruning alternative.
- Calibration datasets: C4 for the full grid; C4 and WikiText-2 on Qwen2.5-1.5B-Instruct to separate sample-seed variance from calibration-distribution variance

For the full-grid C4 condition, each calibration set contains 128 samples of exactly 2,048 tokens from `allenai/c4`, configuration `en`, train split. For seed `s`, shuffle the complete C4 train-split document-index array using `numpy.random.default_rng(s).shuffle`; visit documents in that order, tokenize each document without adding special tokens, skip documents shorter than 2,048 tokens, and retain the first 2,048 tokens from each eligible document until 128 samples have been collected. Persist the selected document indices and token hashes. GPTQ seed `s` and AWQ seed `s` receive the identical ordered calibration samples. This pairing makes a seed-`s` ranking difference attributable to method-by-calibration interaction rather than the methods seeing different data. The Qwen2.5-1.5B-Instruct WikiText-2 distribution analysis will use the same seeds, sample count, token length, eligibility rule, and method pairing, with dataset-specific indices retained.

Benchmarks:

- MMLU
- ARC-Challenge
- HellaSwag, using the first 2,000 validation items in dataset index order (indices 0 through 1,999)
- GSM8K, at least 1,000 fixed test items

The model-family chat template is ON for every benchmark and method, including the FP16 baseline. GSM8K few-shot examples are inline within the user message. All paired methods receive identical item sets, prompt construction, and decoding/scoring settings.

## Outcomes and Analysis

Primary per-pair metrics are net accuracy delta `(c-b)/n`, harmful flip rate `b/n`, beneficial flip rate `c/n`, accuracy-state churn `(b+c)/n`, wrong-to-different-wrong churn, and total answer churn. The primary inferential outputs are bootstrap 95% confidence intervals, exact McNemar tests, TOST equivalence, minimum detectable difference at 80% power, required n at 80% power for the observed effect, and item-bootstrap rank-flip rates.

The TOST equivalence margin is fixed at **2 percentage points** (`0.02`) for accuracy delta. We will not interpret failure to reject a difference as equivalence. McNemar tests are two-sided and exact. Bootstrap seeds, item IDs, calibration sample indices, and environment fingerprints will be retained. Family-wise multiple comparisons will use Holm correction within each benchmark/model family of planned method contrasts.

### Hierarchical aggregation across calibration seeds

Calibration seeds are treated as a random effect. Item-level bootstrap intervals from a single seed do not represent between-seed uncertainty. For every model/benchmark/bit/method cell, we will report (1) item-bootstrap uncertainty separately within each seed, (2) the standard deviation of the five seed-level accuracy estimates, and (3) a two-level paired bootstrap interval. Each replicate of the two-level bootstrap samples the five seed labels with replacement and, within every selected seed, samples the common evaluation items with replacement; GPTQ and AWQ retain the same sampled seed labels and item indices. We will report seed-level SD and item-level SE as separate variance components rather than collapsing them into an item-only interval.

FlipEval's rank-instability metric will be reported both within each seed using item resampling, for comparison with the pilot, and across the paired seed-by-item joint bootstrap, which is the H3-relevant estimate. The joint procedure uses the same two-level resamples described above and reports exact-tie replicates separately.

## H3 Decision Rule

The primary confirmatory analysis is restricted to 4-bit GPTQ and AWQ over the fixed set

`S = {Qwen2.5-1.5B-Instruct, Qwen2.5-7B-Instruct, Llama-3.2-3B-Instruct, Llama-3.1-8B-Instruct} × {MMLU, GSM8K}`,

which contains eight model-by-benchmark cells. MMLU is the registered likelihood-based benchmark and GSM8K the registered generative benchmark in the confirmatory set. ARC-Challenge and HellaSwag are secondary. The identical H3 analyses at 3 bits are pre-declared secondary/exploratory analyses and will be reported regardless of outcome. Four-bit results are primary because 4-bit quantization is the deployment-relevant setting; 3-bit instability is expected to be larger and is interpreted only as a dose-response check, not as a second opportunity for confirmatory significance.

For seed `s`, GPTQ-`s` is compared with AWQ-`s` using the paired calibration set. Let

`d_s(model, benchmark, bit) = acc_GPTQ,s - acc_AWQ,s`.

A winner flip occurs in a cell if there are registered seeds `s` and `t` for which `sign(d_s) != sign(d_t)` and both differences are nonzero. An exact accuracy tie (`d_s = 0`), which can occur because item counts are discrete, is counted as neither a flip nor a non-flip and is reported separately. Thus a tie cannot create or erase a flip between two non-tied seeds.

Define the absolute mean method gap as

`gap(model, benchmark, bit) = |mean_s(acc_GPTQ,s) - mean_s(acc_AWQ,s)|`,

and, for method `m` in `{GPTQ, AWQ}`, define the seed-induced range as

`range_m(model, benchmark, bit) = max_s(acc_m,s) - min_s(acc_m,s)`.

The range/gap criterion holds in a cell exactly when

`max(range_GPTQ, range_AWQ) >= gap`.

**Supported:** H3 is supported if winner flips occur in at least 3 of the 8 confirmatory cells, or the range/gap criterion holds in at least 4 of the 8 confirmatory cells.

**Disconfirmed:** H3 is disconfirmed if winner flips occur in at most 1 of the 8 confirmatory cells and `max(range_GPTQ, range_AWQ) < 0.5 × gap` in at least 6 of the 8 confirmatory cells.

**Inconclusive:** Every outcome satisfying neither the support rule nor the disconfirmation rule is reported as inconclusive, without post-hoc promotion. Calibration-dataset effects, 3-bit results, ARC-Challenge, and HellaSwag are reported separately and cannot substitute for the eight-cell confirmatory rule.

H1 and H2 will be reported as estimated effects with confidence intervals rather than converted into new post-hoc binary thresholds. The preregistered pilot-motivated diagnostics are cancellation (`harmful` and `beneficial` both nonzero relative to net delta), required-n relative to benchmark size, and bootstrap method-rank flips.

## Exclusions and Missing Runs

An item is excluded only for a benchmark loader/scorer failure that affects all compared methods; exclusions and reasons are logged before analysis. Failed checkpoint builds or jobs are rerun with the same registered seed and calibration indices. Backend changes create a new environment cell and do not silently replace prior results.

## Dated Amendments

### 2026-07-20 — WikiText-2 document definition (Decision Point A)

**Decision owner:** Amogh Singh, alone.

**Results inspected before this decision:** No main-grid or mini-grid accuracy
result has been inspected, and none exists. The only evidence seen is
calibration-eligibility data, recorded below.

The 2026-07-13 calibration preflight failure recorded in
`docs/WIKITEXT2_PROTOCOL_BLOCKER.md`: on `Salesforce/wikitext`,
`wikitext-2-raw-v1`, train split, dataset revision
`b08601e04326c79dfdd32d625aee71d232d685c3`, tokenized with
`Qwen/Qwen2.5-1.5B-Instruct` revision
`989aa7980e4cf806f80c7fef2b1adb7bc71aa306` under the pinned runtime
(torch 2.13.0, transformers 5.13.0, datasets 5.0.0), seed 0, no added special
tokens: **0 of 36,718 rows contain at least 2,048 tokens**, against a
registered requirement of 128. No calibration artifact or checkpoint was
produced. This is a property of the corpus layout, not of the seed — WikiText-2
raw distributes each article across many short rows — so no reseeding can make
the registered row-level reading executable.

The 2026-07-20 eligibility probe, run **before** this decision was taken, on the
same pinned dataset revision, tokenizer revision, and runtime, applying the
reconstruction rule below verbatim (SLURM job `11303825`, embers CPU, in-image;
algorithm `wikitext2-level1-heading-articles-v1`): **629 articles reconstructed
from 36,718 rows, of which 425 contain at least 2,048 tokens** against the
registered requirement of 128 — verdict SUFFICIENT, a 3.3× pool. Token-length
distribution across the 629 reconstructed articles: min 10, p25 1,703, median
2,857, p75 5,320, p90 8,577, max 21,295, mean 4,002.0; 2,517,232 tokens total.
Eligibility is a property of the articles and not of the seed, so this single
count satisfies all five registered seeds. The probe script is persisted at
`scripts/wikitext2_article_probe.py` and is the **reference implementation** of
the reconstruction rule: the builder's reconstruction must match its
`reconstruct_articles` and `is_level1_heading` functions verbatim.

**Rationale:** The preregistration requires the WikiText-2 condition to sample
128 *documents* of 2,048 tokens. It did not operationalize "document" for a
corpus whose Hugging Face rows are line fragments rather than documents. This
amendment supplies that definition. It changes no other registered parameter.

**Amended rule.** For the Qwen2.5-1.5B-Instruct WikiText-2 calibration
condition, a *document* is one article, reconstructed deterministically from the
raw corpus as follows:

1. Read the train split in source row order at the pinned dataset revision.
2. An article begins at each row that is a level-1 heading — a row whose text,
   after stripping surrounding whitespace, matches a single `=`-delimited title
   (`= Title =`) and not a deeper heading (`= = Subtitle = =` or lower). All
   rows up to but excluding the next level-1 heading belong to that article.
   Rows preceding the first level-1 heading form no article and are discarded.
3. An article's text is its member rows concatenated in source order, joined
   exactly as stored, with no normalization beyond that already present in the
   raw corpus.
4. The reconstruction algorithm is versioned and persisted with the artifact,
   together with the ordered article index array and a hash of each
   reconstructed article, so the reconstruction is independently checkable.

The registered sampling rule then applies unchanged to that article array: for
seed `s`, shuffle the complete reconstructed-article index array using
`numpy.random.default_rng(s).shuffle`; visit articles in that order; tokenize
each without adding special tokens; skip articles shorter than 2,048 tokens;
retain the first 2,048 tokens from each eligible article until 128 samples are
collected. Persist the selected article indices and token hashes. GPTQ seed `s`
and AWQ seed `s` receive the identical ordered calibration samples, as for C4.

Seeds `{0,1,2,3,4}`, sample count 128, token length 2,048, the eligibility
threshold, method pairing, and index retention are **unchanged** from the
frozen protocol.

**Fail-closed condition.** The builder continues to fail closed on the WikiText-2
condition until this rule is implemented and tested. If the reconstruction
yields fewer than 128 eligible articles for any seed, the builder must raise
rather than relax any registered parameter, and the shortfall returns here as a
new dated amendment.

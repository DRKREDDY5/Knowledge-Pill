# Knowledge Pill — final submission guide

The fine-tuning experiment and first real English/Telugu generation are complete. The remaining required custom-submission item is your Loom recording and its link. The supplied handout asks for a GitHub repository containing project assets and a Loom video.

## Notebook verification

The two source notebooks were checked against GitHub `main` at commit `841063b271549fd59eb53edc6ed3b4754a287d5d`; both match the current local source by Git blob hash. The uploaded Colab copy has now been added separately, preserving its original bytes and saved outputs.

| Asset | Verified status |
|---|---|
| [Training notebook](../notebooks/Knowledge_Pill_Simple.ipynb) | Current source; 13 code cells; no saved outputs. Includes the LLaMA Factory import-path fix |
| [Daily writer notebook](../notebooks/Knowledge_Pill_Daily.ipynb) | Current source; 5 code cells; no saved outputs. Includes the response-length fix |
| [Dataset CSV](../data/knowledge_pill.csv) | Present; 500 rows with original split assignments |
| [Actual training evidence](../results/run_2026-09-12/) | Original predictions, metrics, training log, loss curve, confusion matrices and configuration are present |
| [Daily run evidence](../results/daily_2026-09-12/run.json) | Successful manual run and real provider usage for both languages |
| [Executed Colab notebook](../notebooks/Knowledge_Pill_Executed.ipynb) | Uploaded original: 13 code cells, 12 with execution counts and saved outputs, no saved error outputs; training, merge and evaluation completed |
| Loom recording | No recording URL supplied yet |

The executed notebook’s training time, base revision, 5/5 smoke tests and before/after metrics match the saved run exports. Its SHA-256 is `fc2559944e49421cb5fbd26916e82237d72a1d2506d7994d7e09928429a5a431`. The only unrun code cell downloads the already-created adapter ZIP; it does not train or evaluate the model. Run that final download cell if you still need the adapter backup. No new GPU training is needed.

## What to explain

Knowledge Pill helps AI learners choose relevant reading and learn through familiar stories. The Week 5 experiment trains one decision: English article description → RAG, Agents, Fine-tuning or Other. It uses Qwen3-1.7B-Base, LoRA, a grouped 400/100 split, merging and before/after evaluation.

Qwen improved from 25% to 100% validation accuracy and from 25% to 87.5% on sixteen paper examples. The simple classifier scored 15/16 on the paper set, compared with Qwen's 14/16. The product therefore uses the simple classifier. The small authored sets and checkpoint-selection reuse limit generalization claims. See [EVALUATION.md](EVALUATION.md).

A separate Fireworks writer creates the knowledge and news pills from selected sources. A real manual run generated both languages. Known wording issues were corrected and recorded in [CONTENT_REVIEW.md](CONTENT_REVIEW.md). Automatic scheduling is supported; scheduled delivery has not been verified.

## Finish in this order

1. Open the [three-minute script](DEMO_SCRIPT.md), prepare its four tabs and rehearse once. It includes exactly what to show and say.
2. Record your screen and voice. Show the app, CSV, actual results and successful generation run using the saved evidence.
3. Watch the recording once. Check audio, readable text and video sharing access for evaluators.
4. Add your real Loom URL near the top of README.md with the label **Watch the three-minute demo**.
5. Submit [the GitHub repository](https://github.com/DRKREDDY5/Knowledge-Pill) and your Loom URL through the [handout form](https://forms.gle/7Hpa2Pkd8ZaWUomm6).

**Deadline in the supplied handout: September 13, 2026, 11:59 PM Pacific.** Three minutes is your chosen recording format; the handout does not impose that length.

## Optional after submission

Set `DAILY_PILLS_ENABLED=true` in GitHub Actions variables for daily generation using your Fireworks credits. You do not need to wait for a scheduled run to submit. Independent language review and broader evaluation are useful improvements.

The hosted app is owner-private. Record from your signed-in browser. Reviewers can inspect the public repository and run `python -m http.server 8000 --directory dist` from the project root to open the app locally. The Loom provides the accessible walkthrough; public hosting is not specified in the handout.

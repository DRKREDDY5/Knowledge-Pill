# Week 5 handout mapping

Our custom problem is AI article-topic routing, using the same small-model fine-tuning workflow as the support-ticket example.

| Handout phase | Notebook steps | Evidence | Status |
|---|---|---|---|
| Install dependencies on T4 | 1–2 | environment.txt and factory_revision.txt in the run folder | Completed in user Colab |
| Prepare labelled dataset and stratified 80/20 split | 3 | CSV, data report, original train/validation snapshot | Completed, 400/100 with scenario grouping |
| ShareGPT and dataset_info.json | 3 | results/run_2026-09-12/snapshot/data/processed | Completed |
| Qwen3-1.7B-Base and LoRA | 4, 7 | training.log, base_model_revision.txt, exact YAML snapshot | Completed with LLaMA Factory CLI |
| Review loss curve | 8 | loss_curve.png | Completed |
| Merge, classify(), five examples | 9 | smoke_results.json: 5/5 | Completed; weights were in Colab, not uploaded here |
| Evaluate and compare | 5–6, 10 | comparison.json, per-example predictions, confusion_matrices.png | Metrics and dataset hashes independently recomputed from export |
| Custom GitHub and Loom | Documentation | This repository, source and executed notebooks, actual run exports and recording | Repository assets present; Loom recording/link pending |

LLaMA Board is the graphical interface demonstrated by the handout. We used its LLaMA Factory training engine through CLI commands. The custom submission must describe this accurately; no Board screenshot is included.

The CSV is a readable export of the exact examples used in the run. The self-contained notebook generates its JSON from authored seeds, then registers ShareGPT data. Do not split the CSV randomly: use its split column or the notebook's scenario-grouped split.

## Additional product work

The daily writer, bilingual stories, dated news, recall UI and scheduled generation are extensions. They do not change the fine-tuning task or its evaluation. Keep separate evidence for classifier accuracy and writer quality. A good classification score does not establish factual or linguistic quality of generated pills.

The handout allows custom projects to submit GitHub assets and a Loom rather than the standard Google Doc screenshot route. Source notebooks, the uploaded executed Colab notebook and actual results are present. Add the Loom link before submission. The supplied handout's deadline is September 13, 2026, 11:59 PM Pacific. See [FINAL_SUBMISSION.md](FINAL_SUBMISSION.md).

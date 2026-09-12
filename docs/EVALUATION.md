# Evaluation of the actual Colab run

## What was verified

The uploaded Knowledge_Pill_Results(1).zip contains 28 files. Its original bytes were preserved in the run directory (outputs are flattened; other files are kept under snapshot). [manifest.json](../results/run_2026-09-12/manifest.json) records the archive hash and every file hash.

Verification recomputed classification metrics from every base/merged prediction, checked row IDs and expected labels, reproduced dataset hashes, and regenerated the 400/100 split from the same source scenarios. The exported router.py, topic_seeds.json and source_cases.json matched the project sources at import. No GPU training was rerun locally.

| Model | Validation accuracy | Validation macro F1 | Paper accuracy | Paper macro F1 |
|---|---:|---:|---:|---:|
| Simple classifier | 100/100 | 1.0 | 15/16 | 0.9365079 |
| Base Qwen | 25/100 | 0.1 | 4/16 | 0.1 |
| Merged Qwen | 100/100 | 1.0 | 14/16 | 0.8666667 |

All four fine-tuned validation classes had precision, recall and F1 of 1.0, support 25 each. The confusion matrix is diagonal on this set. Five smoke examples passed.

The LoRA run completed three epochs and 150 optimizer updates. Training runtime was 520.63 seconds. Validation loss fell from 2.6460 to 2.5902; the best checkpoint was step 150. Lower loss alone would not establish better routing, so the before/after prediction comparison is essential.

## Why the comparison is fair within this experiment

- Base and merged Qwen use the same model revision, ChatML prompt and constrained A/B/C/D scoring at the next token.
- Both see the same English descriptions and exactly the same evaluation rows.
- LoRA adapters are trained only on the 400 training rows.
- The lexical model is trained only on training data and retained as a serious alternative.

This controls prompt/format differences; it does not make the small synthetic dataset representative of production traffic.

## Errors and limits

Merged Qwen predicts Fine-tuning for the CLIP and Whisper paper summaries, whose project labels are Other. The lexical baseline predicts Other for SWE-agent instead of Agents. Training mentioned in an article should not automatically determine its main-topic label.

The 500 authored examples have only 100 underlying scenarios. There are 80 training and 20 validation groups. Shared formatting patterns and simplified descriptions make the task easier. Validation also selects the best checkpoint, so it is a development comparison. The 16 historical paper summaries have project-authored labels, and familiar papers may have been in Qwen's original pretraining data. No claim of multilingual classification is made: input descriptions are English.

## Product decision

Use the simpler classifier in the browser and daily source selector. It matches validation performance and scores one more paper case correctly, while avoiding Qwen inference infrastructure in the reading app. This is a pragmatic prototype decision, not proof that it will always outperform Qwen. A fresh, independently labelled article set is the next meaningful evaluation; do not tune repeatedly on these 16 examples and call them an untouched test.

## Separate writer evaluation

Daily-pill generation needs its own checks: source support, correct dates, no invented news, clear fictional analogy, useful exercise and natural language. The scheduled writer has structural/date checks and failure-preservation tests. Its first real Fireworks run and human English/Telugu acceptance review remain pending. The dated demonstration editions were assistant-authored and must not be counted as Fireworks evaluation results.

# Data card

## Task and policy

Input: English AI article title plus a short description. Predict the main contribution:

- **RAG:** retrieving external text or improving text retrieval for knowledge-grounded answers.
- **Agents:** model-directed tools, planning, actions or orchestration.
- **Fine-tuning:** the main contribution is a model-adaptation method, learned adapters, supervised task training or preference optimization.
- **Other:** other AI topics, insufficient information or no dominant topic.

Training inside a retrieval or tool system does not automatically make its main topic Fine-tuning. A general model-adaptation recipe remains Fine-tuning even if demonstrated on a retriever. Ordinary deterministic automation is not automatically an AI agent. A broad newsletter covering all topics equally goes to Other. HyDE is included under RAG because the policy explicitly includes text retrieval methods.

## Authored dataset

`data/topic_seeds.json` has 100 author-labelled synthetic scenarios (25 per class). Each receives five shared title/description formatting patterns, producing 500 rows. These are not scraped articles or 500 independent scenarios. The same formats are used in every category.

We shuffle scenario IDs with seed 42 separately within each label, hold out five of the 25 scenarios, and keep every variation with its scenario. This yields 400 training rows (100 per class) and 100 validation rows (25 per class); no shared scenarios or exact texts. Real information diversity is closer to 80 training scenarios and 20 validation scenarios than to the row counts. These simple augmentations can make validation easier.

Labels were authored for this project and are not independently reviewed. Token length is checked in Colab against the exact pinned tokenizer with a 512-token cutoff. Overlong examples stop the run; they are not silently truncated. The validation loss selects the best checkpoint, so reported validation classification scores are development results.

## Paper diagnostic

`data/source_cases.json` contains 16 author-written short summaries based on official arXiv abstracts, four per label, with direct URLs. Full copyrighted abstracts are not redistributed. We assigned the labels using the above policy. These cases are separate from all authored training/validation scenario IDs; familiar concepts necessarily overlap. Only four cases per class are available, so estimates are unstable. Independent subject-matter review and a larger fresh article set remain future work. The papers may have appeared in Qwen's original pretraining data.

## Locally measured baseline

TF-IDF unigrams/bigrams and logistic regression are fit only on the 400 training rows. Validation: accuracy 1.000, macro F1 1.000 (100 rows). Paper cases: accuracy 0.9375, macro F1 0.9365079365 (16 cases). The SWE-agent summary was predicted Other instead of Agents. Browser inference matches the Python model on both evaluation sets. The browser adds a simple Other fallback when an input has zero known vocabulary features.

A perfect synthetic validation score highlights how easy this set is; it does not prove deployment quality. Do not manufacture a Qwen advantage by removing the strong baseline. Record negative results and explain whether a heavier model earns its cost.

## Product limits

Only English descriptions are classified. The bilingual experience comes from authored lessons and a separate source-grounded writer, not multilingual router training. Independent fluent-speaker review is pending. Topic assignment is not factual verification or full-paper understanding. The training notebook reads a 30-day Hugging Face feed window. The separate daily workflow reads four official feeds over seven days; neither is exhaustive research. Empty/unreachable feeds explicitly fall back to historical examples; imported packets identify their origin.

## CSV and original run evidence

`data/knowledge_pill.csv` exports the exact 500 rows used in the verified run, including their original split assignments. The source seeds remain canonical for notebook generation. Actual predictions and configurations are preserved in `results/run_2026-09-12/`; metrics were recomputed from them.

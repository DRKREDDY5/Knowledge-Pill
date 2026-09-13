# Knowledge Pill — three-minute demo script

Target: about 3 minutes at a comfortable pace, including brief screen changes. Rehearse once with a timer. Only the **Say** paragraphs are spoken; the **Show** lines are directions.

## Open these tabs before recording

1. [Knowledge Pill app](https://knowledge-pill.drkreddy.chatgpt.site) → Daily pills, RAG, English. Click **Check for new editions**.
2. [Dataset CSV](https://github.com/DRKREDDY5/Knowledge-Pill/blob/main/data/knowledge_pill.csv).
3. [Executed Colab notebook](https://github.com/DRKREDDY5/Knowledge-Pill/blob/main/notebooks/Knowledge_Pill_Executed.ipynb), or keep your original Colab tab open. Use steps 8–10; the [README results](https://github.com/DRKREDDY5/Knowledge-Pill#actual-results) are a compact alternative.
4. [Successful daily-generation run, attempt 3](https://github.com/DRKREDDY5/Knowledge-Pill/actions/runs/34724909759/attempts/3).

Keep text large enough to read. Close account settings and secret tabs. Record the app from your signed-in browser; its current hosted link is owner-private. The public repository can be reviewed separately.

Router example to paste:

```text
An assistant retrieves relevant pages from a company handbook and uses them to answer employees’ questions with citations.
```

The displayed topic should be **RAG**. The app uses the measured simple classifier; describe the Qwen experiment using the exported results.

## 0:00–0:25

**Show:** App → Daily pills. Show the two pill tabs.

**Say:**

> Hi, I’m Rushikeshava. My project is Knowledge Pill. AI learners have plenty to read, but choosing useful material takes time. My idea is two short sessions: one explains a concept through a familiar story; the other covers recent AI developments. Readers can choose English or Telugu.

## 0:25–0:55

**Show:** App → Article router. Paste the prepared example and show the RAG result.

**Say:**

> For Week Five, I scoped one measurable decision: classify an English article title and description as RAG, Agents, Fine-tuning, or Other. This adapts the handout’s support-ticket router to my product. The trained model chooses a topic. A separate Fireworks model writes the learning content. This keeps the training task focused and easy to evaluate.

## 0:55–1:25

**Show:** GitHub → data/knowledge_pill.csv; then executed notebook → step 8, loss curve.

**Say:**

> The dataset has one hundred authored scenarios, each in five formats, giving five hundred rows. I split by scenario: four hundred training rows and one hundred validation rows. Related variations stay together. I trained Qwen3-1.7B-Base with LoRA for three epochs using LLaMA Factory’s command line. LoRA trains a small adapter while the base weights stay frozen. Here is the loss curve.

## 1:25–2:00

**Show:** Executed notebook → step 9, Passed 5/5; step 10, comparison tables and confusion matrix.

**Say:**

> After merging the adapter, all five smoke tests passed. Qwen’s validation accuracy improved from twenty-five to one hundred percent. On sixteen separate paper examples, it reached eighty-seven point five percent. But the simple classifier got fifteen of sixteen right, compared with Qwen’s fourteen. So I kept the simple classifier in the product. These small, authored evaluation sets do not prove broad accuracy.

## 2:00–2:35

**Show:** App → Daily pills: show the story, exercise and recall answer; switch to Telugu; open AI News Pill and a source.

**Say:**

> Here is the product experience: a fictional story, a concept explanation, and a small exercise with a recall question. Each pill targets five to ten minutes including the activity. The news pill shows original sources and publication dates. Older updates are labelled recent. The English and Telugu versions teach the same concept, although their stories can differ. Generated text remains open to review.

## 2:35–3:00

**Show:** GitHub Actions → successful attempt 3; finish on README and the repository files.

**Say:**

> This run generated both languages and saved the editions. The workflow collects sources, checks dates, writes drafts, and validates them before saving. It supports an optional daily schedule. My main learning: measure model choices and use the simpler option when it works. The repository includes the evidence and documentation. Thank you.

## Recording notes

- Spoken script: **337 words**. Aim for approximately 125–135 words per minute and brief screen transitions; exact duration depends on your pace.
- The daily run shown is a successful **manual** run. Say the schedule is supported; do not claim scheduled delivery was verified.
- The executed Colab notebook is included with saved outputs. Its training and evaluation completed; only the final adapter-download cell is unrun. Show steps 8–10 without rerunning training.
- The original handout used LLaMA Board. Our custom project used the same LLaMA Factory training engine through the command line.
- Do not rerun GPU training just to record the demo. Use the completed run and saved evidence.

## After recording

Watch the recording once, check audio and screen readability, then add the Loom URL beside the project links at the top of README.md. Submit the GitHub and Loom links through the [handout form](https://forms.gle/7Hpa2Pkd8ZaWUomm6). See [FINAL_SUBMISSION.md](FINAL_SUBMISSION.md) for the remaining steps.

# Loom recording script — Knowledge Pill

Aim for about 5 minutes. This is a suggested length, not a handout rule. Read naturally; pause while showing each screen. Do not record API keys or secret settings.

## Before recording

Open these tabs in order:

1. The app, Daily pills, RAG, English.
2. Your executed Colab training notebook, at steps 3 and 7–10.
3. GitHub: data/knowledge_pill.csv and results/run_2026-09-12/comparison.json.
4. GitHub Actions: Generate daily pills, if a real run has succeeded.

Refresh the app once, check that the dated edition loads, and test the language switch. If Fireworks is not configured, use the labelled demonstration and say so. Do not recreate a successful workflow screenshot or describe a source-only check as generation.

## 0:00–0:35 — The problem

**Show:** Daily pills and the two tabs.

**Say:**

“Hi, I'm Rushikeshava. My Week 5 project is Knowledge Pill. As a developer learning AI, I find plenty of articles, but choosing what to read and understanding it takes time.

My idea is two small learning sessions. One teaches a concept using a familiar story, an explanation and a practice question. The other explains recent AI developments with their original sources and dates. Readers can choose English or Telugu. Each session targets five to ten minutes, including the activity.”

## 0:35–1:10 — The Week 5 scope

**Show:** Article router. Paste: An assistant retrieves relevant pages from a company handbook and uses them to answer employees' questions with citations. Click Find the topic.

**Say:**

“I kept the fine-tuning task small. The handout routes support tickets. My custom version routes an English article title and description into RAG, Agents, Fine-tuning or Other.

That is the only decision I trained Qwen to make. The model is not trained to write all the learning content. This gives me a clear problem and a result I can measure.”

## 1:10–1:55 — Data and training

**Show:** CSV, then Colab's data table, training settings and loss curve.

**Say:**

“My data has one hundred authored scenarios. Five shared formatting variations produce five hundred rows. These are not five hundred independently collected articles.

I split by scenario, giving four hundred training rows and one hundred validation rows. Variations of the same scenario never appear in both sets.

I used Qwen3-1.7B-Base and trained a LoRA adapter with LLaMA Factory. LoRA learns a small set of extra parameters while the base weights remain frozen. I used the command line for the same training engine demonstrated through LLaMA Board in the handout. The run used three epochs, and both training and validation loss decreased.”

## 1:55–2:50 — Actual results and judgment

**Show:** Five smoke results, comparison table, confusion matrix and the two paper errors.

**Say:**

“After training, I merged the adapter into the base model and tested the classifier. All five smoke tests passed.

On the same validation set, Qwen improved from twenty-five percent to one hundred percent accuracy. I also checked sixteen separate paper summaries, where it improved from twenty-five percent to eighty-seven point five percent.

I compared it with a simple TF-IDF and logistic regression classifier. That model also reached one hundred percent validation accuracy and got fifteen of the sixteen paper examples right, compared with fourteen for fine-tuned Qwen.

So I retained the simpler classifier in the browser. Fine-tuning clearly helped Qwen in this experiment, but that does not mean it is automatically the best product choice. The evaluation set is small and authored. Here are two mistakes: CLIP and Whisper were assigned to Fine-tuning instead of Other.”

## 2:50–3:45 — The learning experience

**Show:** Knowledge Pill story, connection, exercise and recall. Switch to Telugu. Then open AI News Pill and its source.

**Say:**

“Here is the reading experience. The story is explicitly fictional. The next section connects it to the real concept and explains where the analogy stops working. The reader tries a small exercise and explains the idea back before revealing the answer.

The news pill shows source links and publication dates. Older material is labelled recent, rather than being presented as today's announcement. If no eligible updates exist, the workflow says so.

Changing the language changes the explanation. This is bilingual content; I am not claiming that my topic classifier was trained to understand Telugu.”

**If demonstrating the included samples, add:**

“These are dated, assistant-authored demonstration editions. They show the reading flow, but they are not outputs from a Fireworks run.”

## 3:45–4:25 — Daily workflow

**Show:** README architecture and the daily workflow. If available, show a successful real generation run and its saved edition.

**Say:**

“The daily workflow collects a bounded set of official sources, checks dates, chooses relevant material and asks an existing Fireworks model to write both pills. Code checks the structure and source references before saving a dated JSON edition. The app loads saved editions from GitHub automatically.

I used a fixed workflow because the steps are known. I did not need several autonomous agents. By default, one topic in English and Telugu uses two writer requests per day.”

**Choose the truthful status sentence:**

- Before the first real run: “The generation and scheduling code is included. Fireworks configuration and the first live run are still pending.”
- After a verified real manual run: “This workflow run generated the edition shown here. I reviewed its sources and language. The daily schedule is enabled only after setting the activation variable.”

Do not say the schedule has run successfully unless an actual scheduled run exists. A manual generation run proves the generation path, not the scheduler's delivery history.

## 4:25–5:00 — Close with what you learned

**Show:** GitHub evidence folder and README limitations.

**Say:**

“My main learning is that model choice is a product decision. I should measure the improvement, inspect the mistakes and keep the simpler option when it is sufficient.

The repository includes the data, notebook, training configuration, actual predictions, loss plot and evaluation report. The next quality step is a fresh, independently labelled article set and human review of real generated English and Telugu editions.

Knowledge Pill connects the Week 5 fine-tuning experiment to a small learning product, while keeping its results and limitations visible. Thank you.”

## After recording

Watch the recording once. Check sound, legible text, dates and the status sentence. Add the Loom URL to README.md and submit it with https://github.com/DRKREDDY5/Knowledge-Pill through the handout form. The executed Colab notebook must be added separately; the source notebook here does not contain invented execution outputs.

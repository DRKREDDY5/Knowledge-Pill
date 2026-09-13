# Knowledge Pill

AI topic routing and short concept/news lessons in English and Telugu. Built by Rushikeshava for Week 5.

[App](https://knowledge-pill.drkreddy.chatgpt.site) — currently owner-private. The static app can also run locally.

## Files

- [Executed Colab notebook](notebooks/Knowledge_Pill_Executed.ipynb): original training and evaluation outputs.
- [Training source notebook](notebooks/Knowledge_Pill_Simple.ipynb) and [daily writer notebook](notebooks/Knowledge_Pill_Daily.ipynb).
- [Labelled CSV](data/knowledge_pill.csv): 500 rows, 400 training / 100 validation; split by scenario.
- [Actual training results](results/run_2026-09-12/) and [daily generation evidence](results/daily_2026-09-12/run.json).
- `configs/`, `scripts/`, `tests/` and `.github/workflows/`: configuration and reproducible execution.

## Results

| Model | Validation accuracy | Paper cases |
|---|---:|---:|
| Simple classifier | 100% | 15/16 |
| Qwen before training | 25% | 4/16 |
| Qwen + LoRA | 100% | 14/16 |

The product uses the simple classifier. A separate Fireworks model writes the daily pills. These small authored evaluation sets do not establish broad accuracy. Full metrics and limitations are in the saved results and [evaluation notes](docs/EVALUATION.md).

## Run

```bash
python -m http.server 8000 --directory dist
```

Open `http://localhost:8000`. Source notebooks run in Colab; completed training does not need repeating. To generate new pills, use the daily notebook or the existing GitHub Actions workflow with the Fireworks secret and model variable configured. See [provider setup](docs/DAILY_SETUP.md).

```bash
python -m pip install -r requirements-data.txt
python -m unittest discover -s tests -v
```

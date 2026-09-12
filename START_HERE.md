# Finish Knowledge Pill in this order

Your GPU training is complete. The actual results ZIP has been received and verified. You do not need to retrain.

1. **Save the remaining training files.** In Colab run the last adapter-download cell. Choose File → Download → Download .ipynb to save the executed notebook. Upload the executed notebook to this project conversation; the adapter can stay in your own storage. Do not claim an adapter upload until it is confirmed.
2. **Open the app.** Daily pills automatically load the dated RAG demonstrations in English and Telugu. They are labelled demonstrations, not Fireworks output. The Experiment page summarizes actual training results. Source files and raw reports are available in the GitHub repository.
3. **Activate the real writer.** Follow [DAILY_SETUP.md](docs/DAILY_SETUP.md). Add FIREWORKS_API_KEY as a GitHub Actions secret and FIREWORKS_MODEL as a repository variable. Run the Generate daily pills workflow manually with collect_only unchecked. Inspect its output and sources. Then set DAILY_PILLS_ENABLED=true to activate the existing schedule.
4. **Review the first generated edition.** Read the English and Telugu versions. Check facts against sources, publication dates, analogy boundaries and natural language. The app records review only on your device. Independent fluent-speaker review remains your step; the demo's assistant review is not a substitute.
5. **Record your Loom.** Use [DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md). Speak in your own words and show the actual report, loss curve, five smoke tests and product. Only say the scheduled writer is running after its real workflow succeeds.
6. **Submit.** GitHub: https://github.com/DRKREDDY5/Knowledge-Pill. Add your Loom URL to the README. Use the handout's submission form: https://forms.gle/7Hpa2Pkd8ZaWUomm6. Deadline: September 13, 2026, 11:59 PM Pacific.

The daily setup uses an existing inference-ready Fireworks model. It does not deploy your fine-tuned Qwen to Fireworks and does not create paid dedicated infrastructure.

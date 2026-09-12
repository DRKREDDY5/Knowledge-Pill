# Sources and provenance

The dataset summaries are author-written from official paper abstracts. Labels follow our project policy and are not independently reviewed.

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) — RAG.
- [REALM: Retrieval-Augmented Language Model Pre-Training](https://arxiv.org/abs/2002.08909) — RAG.
- [Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection](https://arxiv.org/abs/2310.11511) — RAG.
- [Precise Zero-Shot Dense Retrieval without Relevance Labels](https://arxiv.org/abs/2212.10496) — RAG.
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) — Agents.
- [Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/abs/2302.04761) — Agents.
- [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291) — Agents.
- [SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering](https://arxiv.org/abs/2405.15793) — Agents.
- [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685) — Fine-tuning.
- [QLoRA: Efficient Finetuning of Quantized LLMs](https://arxiv.org/abs/2305.14314) — Fine-tuning.
- [Direct Preference Optimization: Your Language Model is Secretly a Reward Model](https://arxiv.org/abs/2305.18290) — Fine-tuning.
- [DoRA: Weight-Decomposed Low-Rank Adaptation](https://arxiv.org/abs/2402.09353) — Fine-tuning.
- [An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale](https://arxiv.org/abs/2010.11929) — Other.
- [Learning Transferable Visual Models From Natural Language Supervision](https://arxiv.org/abs/2103.00020) — Other.
- [Robust Speech Recognition via Large-Scale Weak Supervision](https://arxiv.org/abs/2212.04356) — Other.
- [High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/abs/2112.10752) — Other.

## Training and assignment

- [Supplied support router](https://github.com/The-Gen-Academy/5A-Fine-Tune-a-Support-Ticket-Router): official CSV has 585 rows; the notebook uses an 80/20 split (468/117).
- [Qwen3-1.7B-Base](https://huggingface.co/Qwen/Qwen3-1.7B-Base): required base model. Its exact revision is resolved once and recorded in the notebook before training.
- [Pinned LLaMA Factory source](https://github.com/hiyouga/LLaMA-Factory/tree/100e9a42c6c09f8f7849b70d60f3da445fb2024b): Factory engine and qwen3_nothink template.
- [Colab FAQ](https://research.google.com/colaboratory/faq.html): GPU availability and limits vary.
- [Hugging Face editorial feed](https://huggingface.co/blog/feed.xml): optional recent article descriptions.
- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents): foundation lesson on workflows and model-directed agents.

The handout was read from the supplied Week 5 Project Handout (Aug 2026).docx. Deadline and custom GitHub + Loom requirements come from that attachment. Research pages/abstracts were checked on September 12, 2026; this does not mean every full paper was read.

# Content review record

## First real Fireworks edition: September 12, 2026

[Successful run, attempt 3](https://github.com/DRKREDDY5/Knowledge-Pill/actions/runs/34724909759/attempts/3) saved both languages. The [original generated collection](https://github.com/DRKREDDY5/Knowledge-Pill/blob/88fa31b72e3df66fbdf8aca64280483b2b70d88e/editions/latest.json) is preserved in Git history. The current collection includes the wording corrections below, recorded in each packet's editorial metadata and disclosed in the app. Provider usage and original run evidence remain unchanged.

| Check | Result |
|---|---|
| English knowledge / news length | 805 / 515 whitespace-counted words; valid under the existing content limits |
| Telugu knowledge / news length | 632 / 418 whitespace-counted words; Telugu-script check passed |
| Source references and dates | Two paper sources and two September 10 news sources; correctly labelled recent |
| Python and browser validation | Both packets passed |
| Editorial review | Assistant compared source claims, read both languages and applied the corrections below |
| Human review | Independent fluent Telugu review is recommended; no human approval is claimed |

The [RAG](https://arxiv.org/abs/2005.11401) and [REALM](https://arxiv.org/abs/2002.08909) abstracts support the descriptions of external retrieval alongside model parameters. The [Google Research post](https://research.google/blog/toolgrad-efficient-tool-use-dataset-generation-with-textual-gradients/) supports ToolGrad's reported method and the quoted benchmark numbers; the experiment has not been reproduced here. The [OpenAI article](https://openai.com/index/using-codex-chatgpt-to-search-for-new-antimicrobials/) supports the research-assistance example. The generator used only that item's feed excerpt and disclosed this limitation.

**Corrections applied to the saved edition:**

- Changed the Telugu summary to say that RAG combines parameter knowledge with retrieved information.
- Changed the Telugu story to say that the retrieved material did not supply the answer, without claiming the whole library lacks it.
- Labelled similarity thresholds and evidence checks as proposed engineering choices. Clarified that missing evidence can reflect retrieval failure as well as absent documents.
- Reworded the Telugu recall question and news answer. Clarified that successful tool execution does not prove every factual claim.

The table's word counts describe the original API output; the edited editions were rechecked against the same content limits. Reader review remains available in the app, and future generated content is still labelled as an AI draft. This review is not an additional Week 5 handout requirement.

The two versions were written independently from the same source pack and concept; their fictional stories differ. They are not sentence-by-sentence translations. Successful API execution is distinct from final editorial approval.

## Dated demonstrations included in the repository

- Edition: September 12, 2026, RAG, English and Telugu.
- Generation method: assistant-authored demonstration, not a Fireworks API response.
- Knowledge concept: retrieving supporting material before answering, taught through an explicitly fictional library notice.
- News: one selected Google Research update from September 10, correctly labelled recent.
- Automated checks: required fields, source IDs, lengths, Telugu character presence and browser packet/date validation.
- Editorial review performed by the assistant: source-to-claim comparison, English/Telugu meaning, date wording and analogy boundary.
- Independent fluent-speaker review: **pending**. This record is not a human sign-off or a quality score.

## Source-to-claim review

| Claim | Support and boundary |
|---|---|
| RAG combines a language model with retrieved passages; its research system uses a Wikipedia index | [RAG abstract](https://arxiv.org/abs/2005.11401). No promise of guaranteed factual correctness |
| REALM studies retrieval alongside language-model learning | [REALM abstract](https://arxiv.org/abs/2002.08909). The two systems are not described as identical |
| ToolGrad produces tool-use sequences before matching requests and uses feedback | [Google Research, September 10](https://research.google/blog/toolgrad-efficient-tool-use-dataset-generation-with-textual-gradients/). Reported findings are attributed; no experiment was reproduced here |
| Library visit and room-booking practice | Original fictional teaching examples. Not attributed as real events or paper experiments |

The example retains technical names such as RAG, retrieval and generation in English where useful, while explaining the idea in Telugu. The knowledge versions preserve the same story and limitation. News translations retain the publication date, attribution and distinction between reporting and interpretation.

## Review each real writer output

1. Read both the pill and the linked sources. For each factual statement, find the supporting passage. Remove or qualify unsupported claims.
2. Confirm that the story is fictional and its mapping does not imply guaranteed model correctness.
3. Confirm actual publication dates and the selected timezone. Older news must remain recent, not today.
4. Check translation meaning, naturalness and preserved technical terms with a fluent Telugu reader.
5. Try the exercise and recall question. Does the answer follow from the explanation?
6. Record any corrections and keep the unedited output/evidence for comparison. Never change an evaluation result to make it look better.

The app's reviewed button records a reader's local acknowledgement. It does not publish a review to GitHub, gate public visibility or certify automatically generated editions. All newly generated editions remain visibly drafts.

# Daily generation: exact setup

The app already reads saved editions automatically. GitHub Actions will generate new drafts on a schedule once you add the provider configuration. The first real Fireworks request has not been verified yet.

## 1. Add the key privately

Open [repository Actions secrets](https://github.com/DRKREDDY5/Knowledge-Pill/settings/secrets/actions). Choose **New repository secret**.

- Name: `FIREWORKS_API_KEY`
- Secret: your Fireworks API key

Never paste the key into chat, a notebook code cell, a workflow file, an issue or the README. Keys are used only by the runner; the app does not receive them. See [GitHub's secret guide](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets).

## 2. Select the writer

In the same settings area choose **Variables → New repository variable**.

- Name: `FIREWORKS_MODEL`
- Value: the exact inference-ready model or deployment path from your Fireworks account, beginning with `accounts/`.

Use a model already available for inference in your account. There is intentionally no guessed model default: availability depends on the account. The request uses the [Fireworks chat-completions API](https://docs.fireworks.ai/api-reference/post-chatcompletions) with JSON output. Do not create a dedicated paid deployment just to bypass an unavailable-model error.

## 3. Run once manually

Open **Actions → Generate daily pills → Run workflow**. Select `main`. Leave **collect_only** unchecked for a real generation run.

For a source-only check, check collect_only; that mode does not call Fireworks and does not publish a generated edition.

A successful real run updates `editions/latest.json` and commits it. Open the app's Daily pills page or click **Check for new editions**. The provider model and original date appear with the content. Browser/GitHub caching may introduce a short delay.

Default configuration: RAG, English and Telugu, America/New_York, at most 30 saved editions. That means two writer requests per generation day; each request creates both kinds of pill. Provider usage is billed to your Fireworks account and usage tokens are saved with each packet. Prices depend on your selected model. There are no automatic provider retries.

## 4. Review the first output

Check the fictional story label, factual explanation, source IDs, original news dates, English/Telugu meaning and recall answer. See [CONTENT_REVIEW.md](CONTENT_REVIEW.md). Mark it reviewed in the app only after you have checked it. This device-local review does not change the public draft's status or certify future outputs.

The writer returns drafts, not certified facts. Automated validation checks structure, source IDs, dates and rough length/language signals. It cannot prove that every sentence is true or the Telugu is natural.

## 5. Enable the schedule

After the manual run succeeds, add repository variable:

- Name: `DAILY_PILLS_ENABLED`
- Value: `true`

The workflow schedule is **11:17 UTC every day**: 7:17 AM in Ohio during daylight saving time and 6:17 AM during standard time. It uses the latest default-branch code. GitHub schedules can be delayed; it is not an exact-time delivery guarantee. See [workflow schedule documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onschedule).

To pause paid generation, set DAILY_PILLS_ENABLED to `false`. Manual Run workflow still works when scheduling is disabled.

## Behavior when things go wrong

| Situation | Behavior / next action |
|---|---|
| Key/model missing | Generation stops before a provider request; last edition stays available |
| HTTP 401/403 | Check key/account access; do not put credentials in logs |
| Model unavailable or insufficient credit | Choose an existing supported model or check your account; no automatic deployment |
| Invalid or truncated response | Reject the draft; inspect the error before another paid attempt |
| One language succeeds and the other fails | Keep public collection unchanged; partial checkpoint is a workflow artifact |
| Same day rerun after success | Reuse existing Fireworks editions; no repeated provider requests |
| News feed unavailable | Record the unavailable publisher; use other eligible sources; never invent updates |
| No eligible recent news | Publish a clear no-updates explanation with no news items |
| Older saved edition | App displays its date and warns it is not today's news |
| Git push conflict | Workflow fails visibly; generated output remains in the artifact for recovery |

Source excerpts and partial checkpoints are kept in a seven-day workflow artifact for review; only generated drafts and source metadata enter the public edition JSON. Public repository artifacts may be downloadable by signed-in readers. Sources are public and no personal profile or key is included. The public app is not a private research vault.

Generation runs off-device on GitHub Actions. Reading and recall progress remain local to each browser. There is no on-demand writing server or personal per-user scheduler in this version.

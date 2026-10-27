# Daily LeetCode Automation

A cloud-scheduled study assistant that prepares five C++17 solution drafts each day using the Gemini API: **2 Easy, 2 Medium, and 1 Hard**. Scheduled for **06:00 Asia/Kolkata**.

## Progress dashboard

The repository includes a GitHub Pages dashboard that lists unique problems from `state/history.json`, shows the latest draft/compile/local-test statuses, and lets you track your own progress and submission outcomes.

- Track: Not started, Solved locally, Submitted, Accepted, Wrong Answer, Time Limit Exceeded, Runtime Error, Compile Error, and Needs review.
- Search and filter by title, status, and difficulty.
- Export/import your status data as JSON.
- **Your edited statuses are stored in this browser only.** Export/import to move them between browsers/devices. The dashboard does not access your LeetCode account or detect submissions automatically.
- To publish it, open **Settings → Pages** in this repository and set **Build and deployment → Source** to **GitHub Actions**. The deployment workflow then publishes `docs/`. After the first successful deployment, the site URL will be shown in the workflow run and Pages settings.

## Current scope and limitations

- Generates five AI-assisted study drafts and a report.
- Avoids reusing previously generated problems while the curated pool permits.
- **Does not log in to LeetCode or submit solutions.** The generated queue initially marks every problem `NOT_SUBMITTED`; use the dashboard to record your actual submission result.
- Every generated C++17 code block receives a compiler syntax check. Problems without a dedicated harness are marked compile-only.
- A compile or smoke-test pass is not proof of correctness. Read the official problem statement and validate each solution yourself.
- No LeetCode password, session cookie, or account token is required.

## Setup

1. Open **Settings → Secrets and variables → Actions** in this repository.
2. Add a repository secret named `GEMINI_API_KEY` with your Google AI Studio API key. Never commit the key or paste it into source files.
3. Open **Actions → Daily LeetCode Drafts** and run the workflow manually once.
4. Open the run and download the `daily-leetcode-drafts` artifact. It contains five Markdown drafts, a report, and a JSON submission queue.

The schedule is `00:30 UTC` (06:00 IST). GitHub may delay scheduled workflows, and scheduled runs require the workflow to exist on the default branch.

## Local run

Requires Python 3.11+.

```bash
python -m venv .venv
# Activate the virtual environment, then:
pip install -r requirements.txt
export GEMINI_API_KEY='your-key-here'  # Windows PowerShell: $env:GEMINI_API_KEY='your-key-here'
python -m src.daily
```

Generated files are written under `output/YYYY-MM-DD/`; the history is stored in `state/history.json`.

## Model and costs

The default model is `gemini-3.5-flash-lite`, configurable with `GEMINI_MODEL`. Free-tier access and limits depend on Google's current availability and your account. Check [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing). This project does not guarantee zero cost or unlimited usage.

## Tests

```bash
python -m unittest discover -s tests -v
```

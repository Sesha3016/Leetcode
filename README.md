# Daily LeetCode Automation

A cloud-scheduled study assistant that prepares five C++17 solution drafts each day using the Gemini API: **2 Easy, 2 Medium, and 1 Hard**. Scheduled for **06:00 Asia/Kolkata**.

## Current scope and limitations

- Generates five AI-assisted study drafts and a report.
- Avoids reusing previously generated problems while the curated pool permits.
- **Does not log in to LeetCode or submit solutions.** Submission status is always `NOT_SUBMITTED`.
- Drafts are unverified and are not compiled or tested by this workflow. Read the official problem statement and validate each solution yourself.
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

The default model is `gemini-2.5-flash-lite`, configurable with `GEMINI_MODEL`. Free-tier access and limits depend on Google's current availability and your account. Check [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing). This project does not guarantee zero cost or unlimited usage.

## Tests

```bash
python -m unittest discover -s tests -v
```

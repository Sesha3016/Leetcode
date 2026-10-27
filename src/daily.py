from __future__ import annotations
import json, os, random, re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
PROBLEMS_FILE = ROOT / "src" / "problems.json"
STATE_DIR = ROOT / "state"
HISTORY_FILE = STATE_DIR / "history.json"
OUTPUT_DIR = ROOT / "output"
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
MIX = {"Easy": 2, "Medium": 2, "Hard": 1}

def load_json(path, fallback):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else fallback

def choose_daily_problems(problems, history):
    used = set(history.get("used_slugs", []))
    selected = []
    for difficulty, count in MIX.items():
        pool = [p for p in problems if p["difficulty"] == difficulty and p["slug"] not in used]
        if len(pool) < count:
            pool = [p for p in problems if p["difficulty"] == difficulty]
        if len(pool) < count:
            raise RuntimeError(f"Problem pool has fewer than {count} {difficulty} problems.")
        random.SystemRandom().shuffle(pool)
        selected.extend(pool[:count])
    random.SystemRandom().shuffle(selected)
    return selected

def safe_error(exc):
    return re.sub(r"sk-[A-Za-z0-9_-]{10,}", "[REDACTED_API_KEY]", f"{type(exc).__name__}: {exc}")[:500]

def generate_draft(client, problem):
    prompt = f"""Create a careful C++17 LeetCode study draft.
Title: {problem['title']}
Difficulty: {problem['difficulty']}
URL: {problem['url']}

You do not have the official statement. Tell the reader to verify the linked statement, constraints, and signature. Include approach, correctness argument, complexity, C++17 class Solution code, and edge cases. State assumptions. Never claim tests, submission, or acceptance occurred. This is an unverified draft."""
    response = client.models.generate_content(model=MODEL, contents=prompt)
    content = (response.text or "").strip()
    if len(content) < 80:
        raise RuntimeError("Model returned an empty or unexpectedly short draft.")
    return content

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("Missing GEMINI_API_KEY. Add it as a GitHub Actions secret.")
    from google import genai
    client = genai.Client(api_key=api_key)
    problems = load_json(PROBLEMS_FILE, [])
    history = load_json(HISTORY_FILE, {"used_slugs": [], "runs": []})
    selected = choose_daily_problems(problems, history)
    now = datetime.now(ZoneInfo(TIMEZONE))
    stamp = now.strftime("%Y-%m-%d")
    run_dir = OUTPUT_DIR / stamp
    run_dir.mkdir(parents=True, exist_ok=True)
    report = [f"# Daily LeetCode Draft Report — {stamp}", "", "**Submission status: NOT_SUBMITTED.** No LeetCode account was accessed.", "**Correctness status: UNVERIFIED.** Local tests were not run.", "", "| # | Problem | Difficulty | Draft status | Submission status |", "|---:|---|---|---|---|"]
    run_record = {"date": stamp, "timezone": TIMEZONE, "model": MODEL, "mix": MIX, "problems": []}
    used = list(history.get("used_slugs", []))
    queue = []
    for i, problem in enumerate(selected, 1):
        status = "DRAFT_GENERATED_UNVERIFIED"
        try:
            draft = generate_draft(client, problem)
        except Exception as exc:
            status, draft = "GENERATION_FAILED", f"Generation failed: {safe_error(exc)}"
        text = f"# {problem['title']}\n\n- Difficulty: {problem['difficulty']}\n- Official problem: {problem['url']}\n- Draft status: {status}\n- Local test status: NOT_RUN\n- LeetCode submission status: NOT_SUBMITTED\n\n> Verify the official statement and constraints. This is not proof of correctness.\n\n{draft}\n"
        (run_dir / f"{i:02d}-{problem['slug']}.md").write_text(text, encoding="utf-8")
        report.append(f"| {i} | [{problem['title']}]({problem['url']}) | {problem['difficulty']} | {status} | NOT_SUBMITTED |")
        run_record["problems"].append({"slug": problem["slug"], "difficulty": problem["difficulty"], "draft_status": status, "local_test_status": "NOT_RUN", "submission_status": "NOT_SUBMITTED"})
        queue.append({"slug": problem["slug"], "title": problem["title"], "url": problem["url"], "status": "NOT_SUBMITTED"})
        if status == "DRAFT_GENERATED_UNVERIFIED":
            used.append(problem["slug"])
    report += ["", "## Limitations", "- AI drafts have not been compiled or tested.", "- This workflow does not log into LeetCode or submit code.", "- Review the official statement and use a permitted submission method."]
    history.setdefault("runs", []).append(run_record)
    history["used_slugs"] = list(dict.fromkeys(used))
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")
    (run_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (run_dir / "submission_queue.json").write_text(json.dumps({"date": stamp, "items": queue}, indent=2), encoding="utf-8")
    print(f"Report written to {run_dir / 'REPORT.md'}")

if __name__ == "__main__":
    main()

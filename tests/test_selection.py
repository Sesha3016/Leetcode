import json, unittest
from pathlib import Path
from src.daily import MIX, choose_daily_problems

ROOT = Path(__file__).resolve().parents[1]

class SelectionTests(unittest.TestCase):
    def test_exact_mix_and_unique(self):
        problems = json.loads((ROOT / "src" / "problems.json").read_text())
        selected = choose_daily_problems(problems, {"used_slugs": []})
        self.assertEqual(len(selected), 5)
        self.assertEqual({d: sum(p["difficulty"] == d for p in selected) for d in MIX}, MIX)
        self.assertEqual(len({p["slug"] for p in selected}), 5)

    def test_avoids_used_when_possible(self):
        problems = json.loads((ROOT / "src" / "problems.json").read_text())
        selected = choose_daily_problems(problems, {"used_slugs": ["two-sum", "maximum-subarray", "trapping-rain-water"]})
        self.assertNotIn("two-sum", {p["slug"] for p in selected})
        self.assertNotIn("maximum-subarray", {p["slug"] for p in selected})
        self.assertNotIn("trapping-rain-water", {p["slug"] for p in selected})

if __name__ == "__main__":
    unittest.main()

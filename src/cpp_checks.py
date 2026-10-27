from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

# Deterministic smoke tests for curated LeetCode problems.
# Unconfigured problems receive a C++17 syntax check only.
PREAMBLE = {
    "merge-two-sorted-lists": r"""
struct ListNode {
    int val;
    ListNode* next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode* next) : val(x), next(next) {}
};
""",
}

HARNESS = {
    "maximum-subarray": r"""
int main() {
    Solution s;
    if (s.maxSubArray(std::vector<int>{-2,1,-3,4,-1,2,1,-5,4}) != 6) return 1;
    if (s.maxSubArray(std::vector<int>{-8,-3,-6,-2,-5,-4}) != -2) return 2;
    if (s.maxSubArray(std::vector<int>{5}) != 5) return 3;
    if (s.maxSubArray(std::vector<int>{1,2,3,4}) != 10) return 4;
    return 0;
}
""",
    "median-of-two-sorted-arrays": r"""
int main() {
    Solution s;
    if (std::abs(s.findMedianSortedArrays(std::vector<int>{1,3}, std::vector<int>{2}) - 2.0) > 1e-9) return 1;
    if (std::abs(s.findMedianSortedArrays(std::vector<int>{1,2}, std::vector<int>{3,4}) - 2.5) > 1e-9) return 2;
    if (std::abs(s.findMedianSortedArrays(std::vector<int>{}, std::vector<int>{1}) - 1.0) > 1e-9) return 3;
    if (std::abs(s.findMedianSortedArrays(std::vector<int>{0,0}, std::vector<int>{0,0}) - 0.0) > 1e-9) return 4;
    if (std::abs(s.findMedianSortedArrays(std::vector<int>{1,2,3,4,5,6}, std::vector<int>{7}) - 4.0) > 1e-9) return 5;
    return 0;
}
""",
    "merge-two-sorted-lists": r"""
static std::vector<int> values(ListNode* node) {
    std::vector<int> out;
    while (node) { out.push_back(node->val); node = node->next; }
    return out;
}
static ListNode* makeList(const std::vector<int>& vals) {
    ListNode dummy;
    ListNode* tail = &dummy;
    for (int v : vals) { tail->next = new ListNode(v); tail = tail->next; }
    return dummy.next;
}
static void freeList(ListNode* node) {
    while (node) { ListNode* next = node->next; delete node; node = next; }
}
int main() {
    Solution s;
    ListNode* a = makeList({1,2,4});
    ListNode* b = makeList({1,3,4});
    ListNode* merged = s.mergeTwoLists(a,b);
    if (values(merged) != std::vector<int>{1,1,2,3,4,4}) return 1;
    freeList(merged);
    ListNode* empty = s.mergeTwoLists(nullptr, makeList({0,2}));
    if (values(empty) != std::vector<int>{0,2}) return 2;
    freeList(empty);
    if (s.mergeTwoLists(nullptr, nullptr) != nullptr) return 3;
    return 0;
}
""",
    "contains-duplicate": r"""
int main() {
    Solution s;
    if (!s.containsDuplicate(std::vector<int>{1,2,3,1})) return 1;
    if (s.containsDuplicate(std::vector<int>{1,2,3,4})) return 2;
    if (!s.containsDuplicate(std::vector<int>{-1,0,-1})) return 3;
    if (s.containsDuplicate(std::vector<int>{7})) return 4;
    return 0;
}
""",
    "number-of-islands": r"""
int main() {
    Solution s;
    std::vector<std::vector<char>> a{{'1','1','1','1','0'},{'1','1','0','1','0'},{'1','1','0','0','0'},{'0','0','0','0','0'}};
    if (s.numIslands(a) != 1) return 1;
    std::vector<std::vector<char>> b{{'1','1','0','0','0'},{'1','1','0','0','0'},{'0','0','1','0','0'},{'0','0','0','1','1'}};
    if (s.numIslands(b) != 3) return 2;
    std::vector<std::vector<char>> water{{'0','0'},{'0','0'}};
    if (s.numIslands(water) != 0) return 3;
    std::vector<std::vector<char>> empty;
    if (s.numIslands(empty) != 0) return 4;
    return 0;
}
""",
    "3sum": r"""
int main() {
    Solution s;
    std::vector<int> a{-1,0,1,2,-1,-4};
    auto got = s.threeSum(a);
    for (auto& v : got) std::sort(v.begin(), v.end());
    std::sort(got.begin(), got.end());
    std::vector<std::vector<int>> expected{{-1,-1,2},{-1,0,1}};
    std::sort(expected.begin(), expected.end());
    if (got != expected) return 1;
    std::vector<int> zeros{0,0,0,0};
    if (s.threeSum(zeros) != std::vector<std::vector<int>>{{0,0,0}}) return 2;
    return 0;
}
""",
    "binary-search": r"""
int main() {
    Solution s;
    std::vector<int> a{-1,0,3,5,9,12};
    if (s.search(a, 9) != 4) return 1;
    if (s.search(a, 2) != -1) return 2;
    std::vector<int> one{5};
    if (s.search(one, 5) != 0 || s.search(one, 2) != -1) return 3;
    return 0;
}
""",
    "top-k-frequent-elements": r"""
int main() {
    Solution s;
    std::vector<int> a{1,1,1,2,2,3};
    auto got = s.topKFrequent(a, 2);
    std::sort(got.begin(), got.end());
    if (got != std::vector<int>{1,2}) return 1;
    std::vector<int> b{1};
    if (s.topKFrequent(b, 1) != std::vector<int>{1}) return 2;
    return 0;
}
""",
    "best-time-to-buy-and-sell-stock": r"""
int main() {
    Solution s;
    if (s.maxProfit(std::vector<int>{7,1,5,3,6,4}) != 5) return 1;
    if (s.maxProfit(std::vector<int>{7,6,4,3,1}) != 0) return 2;
    if (s.maxProfit(std::vector<int>{2,4,1}) != 2) return 3;
    return 0;
}
""",
    "trapping-rain-water": r"""
int main() {
    Solution s;
    if (s.trap(std::vector<int>{0,1,0,2,1,0,1,3,2,1,2,1}) != 6) return 1;
    if (s.trap(std::vector<int>{4,2,0,3,2,5}) != 9) return 2;
    if (s.trap(std::vector<int>{1,2,3}) != 0) return 3;
    return 0;
}
""",
}

def extract_cpp(markdown: str) -> str:
    matches = re.findall(r"```(?:cpp|c\+\+|c)\s*\n(.*?)```", markdown, re.DOTALL | re.IGNORECASE)
    if not matches:
        raise ValueError("No C++ code block found in generated Markdown.")
    return matches[0].strip() + "\n"

def check_cpp(markdown_path: Path, slug: str) -> dict[str, str]:
    source = markdown_path.read_text(encoding="utf-8")
    try:
        cpp = extract_cpp(source)
    except Exception as exc:
        return {"compile_status": "COMPILE_FAIL", "test_status": "NOT_RUN", "details": str(exc)}

    with tempfile.TemporaryDirectory(prefix="leetcode-cpp-") as temp:
        temp_path = Path(temp)
        source_path = temp_path / "solution.cpp"
        source_path.write_text(cpp, encoding="utf-8")
        compile_result = subprocess.run(
            ["g++", "-std=c++17", "-Wall", "-Wextra", "-pedantic", "-fsyntax-only", str(source_path)],
            capture_output=True, text=True, timeout=20
        )
        if compile_result.returncode != 0:
            details = (compile_result.stderr or compile_result.stdout or "Compiler failed")[-3000:]
            return {"compile_status": "COMPILE_FAIL", "test_status": "NOT_RUN", "details": details}

        harness = HARNESS.get(slug)
        if harness is None:
            return {
                "compile_status": "COMPILE_PASS",
                "test_status": "COMPILE_ONLY_NO_HARNESS",
                "details": "C++17 syntax check passed; no problem-specific smoke-test harness is configured."
            }

        full_source = temp_path / "smoke_test.cpp"
        preamble = PREAMBLE.get(slug, "")
        full_source.write_text("#include <algorithm>\n#include <cmath>\n#include <vector>\n" + preamble + "\n" + cpp + "\n" + harness + "\n", encoding="utf-8")
        binary = temp_path / "smoke_test"
        build = subprocess.run(
            ["g++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-pedantic", str(full_source), "-o", str(binary)],
            capture_output=True, text=True, timeout=30
        )
        if build.returncode != 0:
            details = (build.stderr or build.stdout or "Smoke-test harness compilation failed")[-3000:]
            return {"compile_status": "COMPILE_PASS", "test_status": "HARNESS_COMPILE_FAIL", "details": details}
        try:
            run = subprocess.run([str(binary)], capture_output=True, text=True, timeout=5)
        except subprocess.TimeoutExpired:
            return {"compile_status": "COMPILE_PASS", "test_status": "TEST_TIMEOUT", "details": "Smoke-test binary exceeded 5 seconds."}
        if run.returncode != 0:
            details = f"Smoke-test binary exited with code {run.returncode}. {run.stderr[-2000:]}"
            return {"compile_status": "COMPILE_PASS", "test_status": "TEST_FAIL", "details": details}
        return {"compile_status": "COMPILE_PASS", "test_status": "SMOKE_TEST_PASS", "details": "Configured example/edge-case smoke tests passed."}

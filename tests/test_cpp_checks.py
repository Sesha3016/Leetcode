import tempfile
import unittest
from pathlib import Path

from src.cpp_checks import check_cpp

SNIPPETS = {
    "3sum": """```cpp
#include <vector>
#include <algorithm>
class Solution {
public:
 std::vector<std::vector<int>> threeSum(std::vector<int>& nums) {
  std::vector<std::vector<int>> out;
  std::sort(nums.begin(), nums.end());
  for (int i=0;i<(int)nums.size()-2;++i) {
   if (i && nums[i]==nums[i-1]) continue;
   int l=i+1,r=(int)nums.size()-1;
   while(l<r) {
    long long s=(long long)nums[i]+nums[l]+nums[r];
    if(s==0) {
     out.push_back({nums[i],nums[l],nums[r]});
     int a=nums[l],b=nums[r];
     while(l<r && nums[l]==a) ++l;
     while(l<r && nums[r]==b) --r;
    } else if(s<0) ++l; else --r;
   }
  }
  return out;
 }
};
```""",
    "binary-search": """```cpp
#include <vector>
class Solution {
public:
 int search(std::vector<int>& nums, int target) {
  int l=0,r=(int)nums.size()-1;
  while(l<=r) { int m=l+(r-l)/2; if(nums[m]==target)return m; if(nums[m]<target)l=m+1;else r=m-1; }
  return -1;
 }
};
```""",
    "top-k-frequent-elements": """```cpp
#include <vector>
#include <unordered_map>
class Solution {
public:
 std::vector<int> topKFrequent(std::vector<int>& nums, int k) {
  std::unordered_map<int,int> f;
  for(int x:nums) ++f[x];
  std::vector<std::vector<int>> b(nums.size()+1);
  for(auto [x,n]:f)b[n].push_back(x);
  std::vector<int> out;
  for(int i=(int)nums.size();i>=1;--i) for(int x:b[i]) { out.push_back(x); if((int)out.size()==k)return out; }
  return out;
 }
};
```""",
    "best-time-to-buy-and-sell-stock": """```cpp
#include <vector>
#include <algorithm>
class Solution {
public:
 int maxProfit(const std::vector<int>& prices) {
  int mn=prices.empty()?0:prices[0], ans=0;
  for(int x:prices) { ans=std::max(ans,x-mn); mn=std::min(mn,x); }
  return ans;
 }
};
```""",
    "trapping-rain-water": """```cpp
#include <vector>
#include <algorithm>
class Solution {
public:
 int trap(const std::vector<int>& h) {
  int l=0,r=(int)h.size()-1,lm=0,rm=0,ans=0;
  while(l<=r) { if(h[l]<=h[r]) { lm=std::max(lm,h[l]); ans+=lm-h[l]; ++l; } else { rm=std::max(rm,h[r]); ans+=rm-h[r]; --r; } }
  return ans;
 }
};
```""",
}

class CppSmokeTestHarnessTests(unittest.TestCase):
    def test_supported_harnesses(self):
        with tempfile.TemporaryDirectory() as temp:
            for slug, markdown in SNIPPETS.items():
                with self.subTest(problem=slug):
                    path = Path(temp) / f"{slug}.md"
                    path.write_text(markdown, encoding="utf-8")
                    result = check_cpp(path, slug)
                    self.assertEqual(result["compile_status"], "COMPILE_PASS", result["details"])
                    self.assertEqual(result["test_status"], "SMOKE_TEST_PASS", result["details"])

if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path

from src.cpp_checks import check_cpp

SNIPPETS = {
    "valid-palindrome": """```cpp
#include <string>
#include <cctype>
class Solution { public: bool isPalindrome(std::string s) { int l=0,r=(int)s.size()-1; while(l<r){while(l<r&&!std::isalnum((unsigned char)s[l]))++l;while(l<r&&!std::isalnum((unsigned char)s[r]))--r;if(std::tolower((unsigned char)s[l])!=std::tolower((unsigned char)s[r]))return false;++l;--r;}return true;} };
```""",
    "longest-substring-without-repeating-characters": """```cpp
#include <string>
#include <vector>
#include <algorithm>
class Solution { public: int lengthOfLongestSubstring(std::string s) { std::vector<int> last(256,-1); int start=0,best=0; for(int i=0;i<(int)s.size();++i){unsigned char c=s[i];start=std::max(start,last[c]+1);last[c]=i;best=std::max(best,i-start+1);}return best;} };
```""",
    "daily-temperatures": """```cpp
#include <vector>
class Solution { public: std::vector<int> dailyTemperatures(std::vector<int>& t) { std::vector<int> ans(t.size()), st; for(int i=0;i<(int)t.size();++i){while(!st.empty()&&t[i]>t[st.back()]){int j=st.back();st.pop_back();ans[j]=i-j;}st.push_back(i);}return ans;} };
```""",
    "invert-binary-tree": """```cpp
class Solution { public: TreeNode* invertTree(TreeNode* root) { if(!root)return nullptr; auto left=invertTree(root->left); auto right=invertTree(root->right); root->left=right;root->right=left;return root;} };
```""",
    "two-sum": """```cpp
#include <vector>
class Solution { public: std::vector<int> twoSum(std::vector<int>& a, int target) { for (int i=0;i<(int)a.size();++i) for (int j=i+1;j<(int)a.size();++j) if (a[i]+a[j]==target) return {i,j}; return {}; } };
```""",
    "valid-parentheses": """```cpp
#include <string>
#include <stack>
class Solution { public: bool isValid(std::string s) { std::stack<char> st; for(char c:s){if(c=='('||c=='['||c=='{')st.push(c);else{if(st.empty())return false;char t=st.top();st.pop();if((c==')'&&t!='(')||(c==']'&&t!='[')||(c=='}'&&t!='{'))return false;}} return st.empty(); } };
```""",
    "maximum-subarray": """```cpp
#include <vector>
#include <algorithm>
class Solution { public: int maxSubArray(const std::vector<int>& nums) {
 int current=nums[0], best=nums[0];
 for (std::size_t i=1;i<nums.size();++i) { current=std::max(nums[i],current+nums[i]); best=std::max(best,current); }
 return best;
} };
```""",
    "median-of-two-sorted-arrays": """```cpp
#include <vector>
#include <algorithm>
#include <climits>
class Solution { public: double findMedianSortedArrays(std::vector<int>& a,std::vector<int>& b) {
 if(a.size()>b.size()) return findMedianSortedArrays(b,a);
 int m=a.size(),n=b.size(),lo=0,hi=m,half=(m+n+1)/2;
 while(lo<=hi) { int i=lo+(hi-lo)/2,j=half-i;
 int al=i? a[i-1]:INT_MIN, ar=i<m?a[i]:INT_MAX, bl=j?b[j-1]:INT_MIN, br=j<n?b[j]:INT_MAX;
 if(al<=br&&bl<=ar) return (m+n)%2?std::max(al,bl):(std::max(al,bl)+std::min(ar,br))/2.0;
 if(al>br) hi=i-1; else lo=i+1;
 } return 0.0;
} };
```""",
    "merge-two-sorted-lists": """```cpp
class Solution { public: ListNode* mergeTwoLists(ListNode* a,ListNode* b) {
 ListNode dummy(0); ListNode* cur=&dummy;
 while(a&&b) { if(a->val<=b->val) {cur->next=a;a=a->next;} else {cur->next=b;b=b->next;} cur=cur->next; }
 cur->next=a?a:b; return dummy.next;
} };
```""",
    "contains-duplicate": """```cpp
#include <vector>
#include <unordered_set>
class Solution { public: bool containsDuplicate(const std::vector<int>& nums) {
 std::unordered_set<int> seen;
 for(int x:nums) if(!seen.insert(x).second) return true;
 return false;
} };
```""",
    "number-of-islands": """```cpp
#include <vector>
class Solution { void dfs(std::vector<std::vector<char>>& g,int r,int c) {
 if(r<0||c<0||r>=(int)g.size()||c>=(int)g[0].size()||g[r][c]=='0') return;
 g[r][c]='0'; dfs(g,r-1,c);dfs(g,r+1,c);dfs(g,r,c-1);dfs(g,r,c+1);
} public: int numIslands(std::vector<std::vector<char>>& g) {
 if(g.empty()||g[0].empty()) return 0; int n=0;
 for(int r=0;r<(int)g.size();++r)for(int c=0;c<(int)g[0].size();++c)if(g[r][c]=='1'){++n;dfs(g,r,c);}
 return n;
} };
```""",
    "3sum": """```cpp
#include <vector>
#include <algorithm>
class Solution { public: std::vector<std::vector<int>> threeSum(std::vector<int>& n) {
 std::vector<std::vector<int>> o; std::sort(n.begin(),n.end());
 for(int i=0;i<(int)n.size()-2;++i){if(i&&n[i]==n[i-1])continue;int l=i+1,r=n.size()-1;
 while(l<r){long long s=(long long)n[i]+n[l]+n[r];if(!s){o.push_back({n[i],n[l],n[r]});int a=n[l],b=n[r];while(l<r&&n[l]==a)++l;while(l<r&&n[r]==b)--r;}else if(s<0)++l;else --r;}}
 return o;
} };
```""",
    "binary-search": """```cpp
#include <vector>
class Solution { public: int search(std::vector<int>& a,int t){int l=0,r=(int)a.size()-1;while(l<=r){int m=l+(r-l)/2;if(a[m]==t)return m;if(a[m]<t)l=m+1;else r=m-1;}return -1;} };
```""",
    "top-k-frequent-elements": """```cpp
#include <vector>
#include <unordered_map>
class Solution { public: std::vector<int> topKFrequent(std::vector<int>& a,int k){std::unordered_map<int,int> f;for(int x:a)++f[x];std::vector<std::vector<int>> b(a.size()+1);for(auto [x,n]:f)b[n].push_back(x);std::vector<int> o;for(int i=(int)a.size();i>=1;--i)for(int x:b[i]){o.push_back(x);if((int)o.size()==k)return o;}return o;} };
```""",
    "best-time-to-buy-and-sell-stock": """```cpp
#include <vector>
#include <algorithm>
class Solution { public: int maxProfit(const std::vector<int>& p){int m=p.empty()?0:p[0],a=0;for(int x:p){a=std::max(a,x-m);m=std::min(m,x);}return a;} };
```""",
    "trapping-rain-water": """```cpp
#include <vector>
#include <algorithm>
class Solution { public: int trap(const std::vector<int>& h){int l=0,r=(int)h.size()-1,lm=0,rm=0,a=0;while(l<=r){if(h[l]<=h[r]){lm=std::max(lm,h[l]);a+=lm-h[l++];}else{rm=std::max(rm,h[r]);a+=rm-h[r--];}}return a;} };
```""",
    "coin-change": """```cpp
#include <vector>
#include <algorithm>
class Solution { public: int coinChange(std::vector<int>& coins, int amount) {
 std::vector<int> dp(amount + 1, amount + 1); dp[0] = 0;
 for (int a = 1; a <= amount; ++a) for (int c : coins) if (c <= a) dp[a] = std::min(dp[a], dp[a-c] + 1);
 return dp[amount] > amount ? -1 : dp[amount];
} };
```""",
    "climbing-stairs": """```cpp
class Solution { public: int climbStairs(int n) { if (n <= 2) return n; int a=1,b=2; for(int i=3;i<=n;++i){int c=a+b;a=b;b=c;} return b; } };
```""",
    "product-of-array-except-self": """```cpp
#include <vector>
class Solution { public: std::vector<int> productExceptSelf(std::vector<int>& a) { int n=a.size(); std::vector<int> o(n,1); int p=1; for(int i=0;i<n;++i){o[i]=p;p*=a[i];} p=1; for(int i=n-1;i>=0;--i){o[i]*=p;p*=a[i];} return o; } };
```""",
    "course-schedule": """```cpp
#include <vector>
class Solution { public: bool canFinish(int n, std::vector<std::vector<int>>& p) { std::vector<std::vector<int>> g(n); for(auto& e:p) g[e[1]].push_back(e[0]); std::vector<int> state(n); for(int i=0;i<n;++i){ if(state[i]==2)continue; std::vector<std::pair<int,int>> st{{i,0}}; while(!st.empty()){int u=st.back().first; int& j=st.back().second; if(state[u]==0)state[u]=1; if(j==(int)g[u].size()){state[u]=2;st.pop_back();continue;}int v=g[u][j++];if(state[v]==1)return false;if(state[v]==0)st.push_back({v,0});}} return true; } };
```"""
}

class CppSmokeTestHarnessTests(unittest.TestCase):
    def test_all_configured_harnesses(self):
        with tempfile.TemporaryDirectory() as temp:
            for slug, markdown in SNIPPETS.items():
                with self.subTest(problem=slug):
                    path = Path(temp) / f"{slug}.md"
                    markdown = markdown.replace("\\n", "\n")
                    path.write_text(markdown, encoding="utf-8")
                    result = check_cpp(path, slug)
                    self.assertEqual(result["compile_status"], "COMPILE_PASS", result["details"])
                    self.assertEqual(result["test_status"], "SMOKE_TEST_PASS", result["details"])

if __name__ == "__main__":
    unittest.main()

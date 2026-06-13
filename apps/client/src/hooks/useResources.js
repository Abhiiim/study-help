import { useCallback, useMemo, useState } from "react";

export const SEED_RESOURCES = [
  {
    id: 1,
    t: "lc",
    url: "https://leetcode.com/problems/two-sum/",
    title: "Two Sum",
    num: 1,
    diff: "Easy",
    tags: ["Array", "Hash Table"],
    status: "solved",
    platform: "LeetCode",
    date: "Jan 15",
    notes: "Classic hash map approach. O(n) time, O(n) space.",
    desc: "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
  },
  {
    id: 2,
    t: "lc",
    url: "https://leetcode.com/problems/merge-intervals/",
    title: "Merge Intervals",
    num: 56,
    diff: "Medium",
    tags: ["Array", "Sorting"],
    status: "attempted",
    platform: "LeetCode",
    date: "Jan 16",
    notes: "",
    desc: "Given an array of intervals, merge all overlapping intervals and return a non-overlapping array.",
  },
  {
    id: 3,
    t: "cf",
    url: "https://codeforces.com/problemset/problem/1234/A",
    title: "Equalize Prices Again",
    num: "1234A",
    diff: "800",
    tags: ["math", "greedy"],
    status: "unsolved",
    platform: "Codeforces",
    date: "Jan 17",
    notes: "",
    desc: "You are given n numbers. Find the minimum operations to make all numbers equal.",
  },
  {
    id: 4,
    t: "yt",
    url: "https://youtube.com/watch?v=abc",
    title: "Dynamic Programming - Full Course for Beginners",
    channel: "freeCodeCamp.org",
    dur: "5:10:22",
    status: "watching",
    date: "Jan 18",
    notes: "Great DP resource. Start from 1:20:00 for tree DP.",
    desc: "Learn dynamic programming covering memoization, tabulation, and space optimization with 20+ problems.",
  },
  {
    id: 5,
    t: "yt",
    url: "https://youtube.com/watch?v=xyz",
    title: "System Design Interview Primer",
    channel: "Gaurav Sen",
    dur: "22:15",
    status: "saved",
    date: "Jan 19",
    notes: "",
    desc: "Load balancing, caching, database sharding, and microservices architecture.",
  },
  {
    id: 6,
    t: "bl",
    url: "https://overreacted.io/a-complete-guide-to-useeffect/",
    title: "A Complete Guide to useEffect",
    author: "Dan Abramov",
    domain: "overreacted.io",
    readTime: "26 min",
    status: "unread",
    date: "Jan 20",
    notes: "",
    desc: "A deep dive into React's useEffect hook with the correct mental model.",
  },
  {
    id: 7,
    t: "bl",
    url: "https://bytebytego.com/system-design-101",
    title: "System Design 101: Scale to Millions",
    author: "ByteByteGo",
    domain: "bytebytego.com",
    readTime: "15 min",
    status: "read",
    date: "Jan 21",
    notes: "Excellent overview.",
    desc: "Horizontal scaling, CDN, caching, message queues, and sharding explained with diagrams.",
  },
  {
    id: 8,
    t: "lc",
    url: "https://leetcode.com/problems/lru-cache/",
    title: "LRU Cache",
    num: 146,
    diff: "Medium",
    tags: ["Hash Table", "Linked List", "Design"],
    status: "unsolved",
    platform: "LeetCode",
    date: "Jan 22",
    notes: "",
    desc: "Design a data structure that follows LRU cache constraints with O(1) get and put.",
  },
];

function matchesFilter(resource, filter) {
  return (
    filter === "all" ||
    (filter === "problem" && (resource.t === "lc" || resource.t === "cf")) ||
    resource.t === filter
  );
}

function matchesSearch(resource, query) {
  if (!query) {
    return true;
  }

  const q = query.toLowerCase();
  return (
    resource.title.toLowerCase().includes(q) ||
    resource.desc.toLowerCase().includes(q) ||
    ("channel" in resource && resource.channel.toLowerCase().includes(q)) ||
    ("author" in resource && resource.author.toLowerCase().includes(q)) ||
    ("domain" in resource && resource.domain.toLowerCase().includes(q)) ||
    ("tags" in resource && resource.tags.some((tag) => tag.toLowerCase().includes(q)))
  );
}

export function useResources() {
  const [resources, setResources] = useState(SEED_RESOURCES);
  const [filter, setFilter] = useState("all");
  const [view, setView] = useState("grid");
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);

  const filtered = useMemo(
    () => resources.filter((resource) => matchesFilter(resource, filter) && matchesSearch(resource, search)),
    [resources, filter, search],
  );

  const counts = useMemo(
    () => ({
      all: resources.length,
      problem: resources.filter((resource) => resource.t === "lc" || resource.t === "cf").length,
      yt: resources.filter((resource) => resource.t === "yt").length,
      bl: resources.filter((resource) => resource.t === "bl").length,
    }),
    [resources],
  );

  const addResource = useCallback((resource) => {
    setResources((previous) => [{ ...resource, id: Date.now() }, ...previous]);
  }, []);

  const updateStatus = useCallback((id, status) => {
    setResources((previous) => previous.map((resource) => (resource.id === id ? { ...resource, status } : resource)));
  }, []);

  const updateNotes = useCallback((id, notes) => {
    setResources((previous) => previous.map((resource) => (resource.id === id ? { ...resource, notes } : resource)));
  }, []);

  return {
    resources,
    filtered,
    counts,
    filter,
    setFilter,
    view,
    setView,
    search,
    setSearch,
    modalOpen,
    setModalOpen,
    addResource,
    updateStatus,
    updateNotes,
  };
}

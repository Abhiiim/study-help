function getDomain(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch (error) {
    return "saved article";
  }
}

function apiMetadataToPreview(payload, url, detectedType) {
  const responseType = payload?.type || detectedType;
  const type = ["lc", "cf", "yt", "bl"].includes(responseType) ? responseType : detectedType;

  if (!type) {
    throw new Error("Could not detect URL type.");
  }

  const common = {
    t: type,
    url,
    title: payload?.title || "Untitled resource",
    desc: payload?.description || payload?.desc || "No description returned for this resource.",
    date: "Just now",
    notes: "",
  };

  if (type === "lc") {
    return {
      ...common,
      num: payload?.num || 0,
      diff: payload?.diff || "Medium",
      tags: payload?.tags?.length ? payload.tags : ["Array", "DP"],
      status: "unsolved",
      platform: payload?.platform || "LeetCode",
    };
  }

  if (type === "cf") {
    return {
      ...common,
      num: payload?.num || "1547C",
      diff: payload?.diff || "1600",
      tags: payload?.tags?.length ? payload.tags : ["greedy", "math"],
      status: "unsolved",
      platform: payload?.platform || "Codeforces",
    };
  }

  if (type === "yt") {
    return {
      ...common,
      channel: payload?.channel || "YouTube",
      dur: payload?.dur || payload?.duration || "18:45",
      status: "saved",
    };
  }

  return {
    ...common,
    author: payload?.author || "Unknown author",
    domain: payload?.domain || getDomain(url),
    readTime: payload?.readTime || payload?.read_time || "12 min",
    status: "unread",
  };
}

function fallbackPreview(url, detectedType) {
  const fallbackByType = {
    lc: {
      title: "Maximum Subarray",
      description: "Find the contiguous subarray with the largest sum and return its sum.",
      num: 53,
      diff: "Medium",
      tags: ["Array", "DP", "Divide and Conquer"],
      platform: "LeetCode",
    },
    cf: {
      title: "Beautiful Array",
      description: "Practice constructive thinking and greedy transitions on Codeforces.",
      num: "1547C",
      diff: "1600",
      tags: ["greedy", "implementation"],
      platform: "Codeforces",
    },
    yt: {
      title: "Binary Search - Complete Tutorial",
      description: "Binary search templates, boundary patterns, and common interview variants.",
      channel: "NeetCode",
      dur: "18:45",
    },
    bl: {
      title: "Developer Learning Notes",
      description: "A technical article saved for focused reading and later review.",
      author: "Unknown author",
      domain: getDomain(url),
      readTime: "12 min",
    },
  };

  return apiMetadataToPreview(fallbackByType[detectedType] || {}, url, detectedType);
}

export async function fetchMetadataPreview(url, detectedType) {
  try {
    const response = await fetch("/api/fetch-metadata", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
      throw new Error("Metadata fetch failed.");
    }

    const payload = await response.json();
    return apiMetadataToPreview(payload, url, detectedType);
  } catch (error) {
    return fallbackPreview(url, detectedType);
  }
}

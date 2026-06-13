export function detectType(url) {
  if (url.includes("leetcode.com")) {
    return "lc";
  }
  if (url.includes("codeforces.com")) {
    return "cf";
  }
  if (url.includes("youtube.com") || url.includes("youtu.be")) {
    return "yt";
  }
  if (url.trim().length > 10) {
    return "bl";
  }
  return null;
}

export function getPlatformLabel(type) {
  return {
    lc: "LC",
    cf: "CF",
    yt: "YT",
    bl: "Blog",
  }[type] || type;
}

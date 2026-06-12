import { DASHBOARD_URL } from "../shared/api.js";

chrome.runtime.onInstalled.addListener(() => {
  chrome.action.setBadgeBackgroundColor({ color: "#2563eb" });
});

chrome.runtime.onMessage.addListener((message) => {
  if (message?.type === "open-dashboard") {
    chrome.tabs.create({ url: DASHBOARD_URL });
  }
});

import {
  DASHBOARD_URL,
  ApiError,
  getSession,
  loginWithPassword,
  logoutSession,
  requestWithAuth,
} from "../shared/api.js";

const state = {
  session: null,
  activeTab: null,
  unsupportedReason: "",
};

const elements = {
  signedOutView: document.querySelector("#signedOutView"),
  signedInView: document.querySelector("#signedInView"),
  statusMessage: document.querySelector("#statusMessage"),
  loginForm: document.querySelector("#loginForm"),
  emailInput: document.querySelector("#emailInput"),
  passwordInput: document.querySelector("#passwordInput"),
  loginButton: document.querySelector("#loginButton"),
  accountEmail: document.querySelector("#accountEmail"),
  logoutButton: document.querySelector("#logoutButton"),
  tabTitle: document.querySelector("#tabTitle"),
  tabUrl: document.querySelector("#tabUrl"),
  saveForm: document.querySelector("#saveForm"),
  favoriteInput: document.querySelector("#favoriteInput"),
  noteInput: document.querySelector("#noteInput"),
  saveButton: document.querySelector("#saveButton"),
  dashboardButtons: document.querySelectorAll("[data-open-dashboard]"),
};

function setStatus(message, type = "info") {
  elements.statusMessage.textContent = message;
  elements.statusMessage.className = `status ${type}`;
  elements.statusMessage.classList.toggle("hidden", !message);
}

function toErrorMessage(error) {
  if (error instanceof ApiError && error.code === "gmail_only") {
    return "Only Gmail accounts can sign in.";
  }
  return error?.message || "Request failed. Check that the API is running.";
}

function setHidden(element, hidden) {
  element.classList.toggle("hidden", hidden);
}

function isSignedIn() {
  return Boolean(state.session?.accessToken || state.session?.refreshToken);
}

function isSupportedPage(url) {
  if (!url) {
    return false;
  }

  try {
    const parsed = new URL(url);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

function queryActiveTab() {
  return new Promise((resolve, reject) => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const error = chrome.runtime.lastError;
      if (error) {
        reject(new Error(error.message));
        return;
      }
      resolve(tabs[0] || null);
    });
  });
}

async function loadActiveTab() {
  const tab = await queryActiveTab();

  if (!tab?.url) {
    state.activeTab = null;
    state.unsupportedReason = "No active page found.";
    return;
  }

  if (!isSupportedPage(tab.url)) {
    state.activeTab = null;
    state.unsupportedReason = "Open an http or https page to save it.";
    return;
  }

  state.activeTab = {
    title: tab.title || tab.url,
    url: tab.url,
  };
  state.unsupportedReason = "";
}

async function loadSession() {
  state.session = await getSession();

  if (!isSignedIn()) {
    return;
  }

  try {
    const user = await requestWithAuth("/auth/me");
    state.session = await getSession();
    state.session.email = user.email;
  } catch (error) {
    state.session = await getSession();
    if (!isSignedIn()) {
      setStatus("Session expired. Sign in again.", "error");
      return;
    }
    setStatus("Signed in, but the API is not reachable.", "error");
  }
}

function render() {
  const signedIn = isSignedIn();
  setHidden(elements.signedOutView, signedIn);
  setHidden(elements.signedInView, !signedIn);

  if (!signedIn) {
    return;
  }

  elements.accountEmail.textContent = state.session.email || "Gmail account";

  if (state.activeTab) {
    elements.tabTitle.textContent = state.activeTab.title;
    elements.tabUrl.textContent = state.activeTab.url;
    elements.saveButton.disabled = false;
    return;
  }

  elements.tabTitle.textContent = state.unsupportedReason;
  elements.tabUrl.textContent = "";
  elements.saveButton.disabled = true;
}

function setLoginBusy(isBusy) {
  elements.loginButton.disabled = isBusy;
  elements.loginButton.textContent = isBusy ? "Signing in..." : "Sign in";
}

function setSaveBusy(isBusy) {
  elements.saveButton.disabled = isBusy || !state.activeTab;
  elements.saveButton.textContent = isBusy ? "Saving..." : "Save current page";
}

async function handleLogin(event) {
  event.preventDefault();

  const email = elements.emailInput.value.trim();
  const password = elements.passwordInput.value;

  setLoginBusy(true);
  setStatus("Signing in...", "info");

  try {
    state.session = await loginWithPassword(email, password);
    elements.passwordInput.value = "";
    setStatus("Signed in.", "success");
    render();
  } catch (error) {
    setStatus(toErrorMessage(error), "error");
  } finally {
    setLoginBusy(false);
  }
}

async function handleSave(event) {
  event.preventDefault();

  if (!state.activeTab) {
    setStatus(state.unsupportedReason || "This page cannot be saved.", "error");
    return;
  }

  setSaveBusy(true);
  setStatus("Saving page...", "info");

  const note = elements.noteInput.value.trim();

  try {
    await requestWithAuth("/items", {
      method: "POST",
      body: {
        url: state.activeTab.url,
        is_favorite: elements.favoriteInput.checked,
        note: note || null,
        tags: [],
      },
    });

    state.session = await getSession();
    setStatus("Saved. Existing matching URLs are updated automatically.", "success");
  } catch (error) {
    state.session = await getSession();
    render();
    setStatus(toErrorMessage(error), "error");
  } finally {
    setSaveBusy(false);
  }
}

async function handleLogout() {
  elements.logoutButton.disabled = true;
  setStatus("Signing out...", "info");

  try {
    await logoutSession();
    state.session = await getSession();
    render();
    setStatus("Signed out.", "success");
  } catch (error) {
    state.session = await getSession();
    render();
    setStatus("Signed out locally.", "info");
  } finally {
    elements.logoutButton.disabled = false;
  }
}

function openDashboard() {
  chrome.tabs.create({ url: DASHBOARD_URL });
}

async function init() {
  elements.loginForm.addEventListener("submit", handleLogin);
  elements.saveForm.addEventListener("submit", handleSave);
  elements.logoutButton.addEventListener("click", handleLogout);
  elements.dashboardButtons.forEach((button) => {
    button.addEventListener("click", openDashboard);
  });

  try {
    await Promise.all([loadActiveTab(), loadSession()]);
  } catch (error) {
    setStatus(toErrorMessage(error), "error");
  }

  render();
}

init();

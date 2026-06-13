export const API_BASE_URL = "http://localhost:8000/api/v1";
export const DASHBOARD_URL = "http://localhost:5173";

const API_BASE = API_BASE_URL.endsWith("/") ? API_BASE_URL : `${API_BASE_URL}/`;

const STORAGE_KEYS = {
  accessToken: "study_saver_extension_access_token",
  refreshToken: "study_saver_extension_refresh_token",
  email: "study_saver_extension_user_email",
};

let refreshPromise = null;

export class ApiError extends Error {
  constructor(message, status, code = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

function storageGet(keys) {
  return new Promise((resolve, reject) => {
    chrome.storage.local.get(keys, (values) => {
      const error = chrome.runtime.lastError;
      if (error) {
        reject(new Error(error.message));
        return;
      }
      resolve(values);
    });
  });
}

function storageSet(values) {
  return new Promise((resolve, reject) => {
    chrome.storage.local.set(values, () => {
      const error = chrome.runtime.lastError;
      if (error) {
        reject(new Error(error.message));
        return;
      }
      resolve();
    });
  });
}

function storageRemove(keys) {
  return new Promise((resolve, reject) => {
    chrome.storage.local.remove(keys, () => {
      const error = chrome.runtime.lastError;
      if (error) {
        reject(new Error(error.message));
        return;
      }
      resolve();
    });
  });
}

function buildApiUrl(path, query) {
  const cleanPath = path.startsWith("/") ? path.slice(1) : path;
  const url = new URL(cleanPath, API_BASE);

  if (query && typeof query === "object") {
    Object.entries(query).forEach(([key, value]) => {
      if (value === undefined || value === null || value === "") {
        return;
      }
      url.searchParams.set(key, String(value));
    });
  }

  return url;
}

function parseApiError(payload, status) {
  if (payload && typeof payload === "object" && payload.error) {
    return new ApiError(
      payload.error.message || "Request failed",
      status,
      payload.error.code || null,
    );
  }
  return new ApiError("Request failed", status);
}

async function apiRequest(path, options = {}) {
  const { method = "GET", token, body, query } = options;
  const headers = {
    Accept: "application/json",
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  let requestBody;
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    requestBody = JSON.stringify(body);
  }

  const response = await fetch(buildApiUrl(path, query), {
    method,
    headers,
    body: requestBody,
  });

  if (response.status === 204) {
    return null;
  }

  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    throw parseApiError(payload, response.status);
  }

  return payload;
}

export async function getSession() {
  const values = await storageGet(Object.values(STORAGE_KEYS));
  return {
    accessToken: values[STORAGE_KEYS.accessToken] || null,
    refreshToken: values[STORAGE_KEYS.refreshToken] || null,
    email: values[STORAGE_KEYS.email] || null,
  };
}

export async function clearSession() {
  await storageRemove(Object.values(STORAGE_KEYS));
}

async function storeAuthResponse(payload) {
  await storageSet({
    [STORAGE_KEYS.accessToken]: payload.access_token,
    [STORAGE_KEYS.refreshToken]: payload.refresh_token,
    [STORAGE_KEYS.email]: payload.user?.email || "",
  });
  return getSession();
}

export async function loginWithPassword(email, password) {
  const payload = await apiRequest("/auth/login", {
    method: "POST",
    query: {
      client: "extension",
    },
    body: { email, password },
  });
  return storeAuthResponse(payload);
}

export async function refreshSession(refreshToken) {
  if (refreshPromise) {
    return refreshPromise;
  }

  refreshPromise = (async () => {
    const payload = await apiRequest("/auth/refresh", {
      method: "POST",
      body: {
        refresh_token: refreshToken,
        device_info: "Chrome extension popup",
      },
    });
    return storeAuthResponse(payload);
  })();

  try {
    return await refreshPromise;
  } catch (error) {
    await clearSession();
    throw error;
  } finally {
    refreshPromise = null;
  }
}

export function startGoogleOAuth(extensionRedirectUri) {
  return apiRequest("/auth/google/start", {
    query: {
      client: "extension",
      extension_redirect_uri: extensionRedirectUri,
    },
  });
}

export async function completeGoogleOAuth(token) {
  const payload = await apiRequest("/auth/extension/google/session", {
    method: "POST",
    body: {
      token,
    },
  });
  return storeAuthResponse(payload);
}

export async function requestWithAuth(path, options = {}) {
  let session = await getSession();

  if (!session.accessToken && session.refreshToken) {
    session = await refreshSession(session.refreshToken);
  }

  if (!session.accessToken) {
    throw new ApiError("Sign in to Study Saver first.", 401, "not_authenticated");
  }

  try {
    return await apiRequest(path, {
      ...options,
      token: session.accessToken,
    });
  } catch (error) {
    const canRefresh = error instanceof ApiError && error.status === 401 && session.refreshToken;
    if (!canRefresh) {
      throw error;
    }

    const refreshed = await refreshSession(session.refreshToken);
    return apiRequest(path, {
      ...options,
      token: refreshed.accessToken,
    });
  }
}

export async function logoutSession() {
  const session = await getSession();

  try {
    if (session.accessToken && session.refreshToken) {
      try {
        await apiRequest("/auth/logout", {
          method: "POST",
          token: session.accessToken,
          body: {
            refresh_token: session.refreshToken,
            logout_all: false,
          },
        });
      } catch (error) {
        if (error instanceof ApiError && error.status === 401) {
          const refreshed = await refreshSession(session.refreshToken);
          await apiRequest("/auth/logout", {
            method: "POST",
            token: refreshed.accessToken,
            body: {
              refresh_token: refreshed.refreshToken,
              logout_all: false,
            },
          });
        }
      }
    }
  } finally {
    await clearSession();
  }
}

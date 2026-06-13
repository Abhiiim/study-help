const RAW_API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";
const API_BASE_URL = RAW_API_BASE_URL.endsWith("/") ? RAW_API_BASE_URL : `${RAW_API_BASE_URL}/`;

export class ApiError extends Error {
  constructor(message, status, code = null, details = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

function buildApiUrl(path, query) {
  const cleanPath = path.startsWith("/") ? path.slice(1) : path;
  const url = new URL(cleanPath, API_BASE_URL);

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
    const { message, code, details } = payload.error;
    return new ApiError(message || "Request failed", status, code || null, details || {});
  }
  return new ApiError("Request failed", status);
}

export async function apiRequest(path, options = {}) {
  const {
    method = "GET",
    token,
    body,
    query,
    headers = {},
  } = options;

  const requestHeaders = {
    Accept: "application/json",
    ...headers,
  };

  if (token) {
    requestHeaders.Authorization = `Bearer ${token}`;
  }

  let requestBody;
  if (body !== undefined) {
    requestHeaders["Content-Type"] = "application/json";
    requestBody = JSON.stringify(body);
  }

  const response = await fetch(buildApiUrl(path, query), {
    method,
    headers: requestHeaders,
    body: requestBody,
    credentials: "include",
  });

  if (response.status === 204) {
    return null;
  }

  const contentType = response.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");
  const payload = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    throw parseApiError(payload, response.status);
  }

  return payload;
}

export function getApiBaseUrl() {
  return API_BASE_URL.replace(/\/$/, "");
}

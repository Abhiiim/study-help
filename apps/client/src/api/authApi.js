import { apiRequest } from "./http";

export function signup(payload) {
  return apiRequest("/auth/signup", {
    method: "POST",
    body: payload,
  });
}

export function login(payload) {
  return apiRequest("/auth/login", {
    method: "POST",
    body: payload,
  });
}

export function fetchMe(accessToken) {
  return apiRequest("/auth/me", {
    token: accessToken,
  });
}

export function refreshAuthToken(payload) {
  return apiRequest("/auth/refresh", {
    method: "POST",
    body: payload,
  });
}

export function logout(accessToken, payload) {
  return apiRequest("/auth/logout", {
    method: "POST",
    token: accessToken,
    body: payload,
  });
}

export function startGoogleOAuth() {
  return apiRequest("/auth/google/start");
}

export function completeGoogleOAuth(code, state) {
  return apiRequest("/auth/google/callback", {
    query: {
      code,
      state,
    },
  });
}

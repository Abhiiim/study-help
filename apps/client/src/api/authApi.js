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
  return apiRequest("/auth/google/start", {
    query: {
      client: "web",
    },
  });
}

export function completeGoogleOAuth(token) {
  return apiRequest("/auth/google/session", {
    method: "POST",
    body: {
      token,
    },
  });
}

export function forgotPassword(email) {
  return apiRequest("/auth/forgot-password", {
    method: "POST",
    query: { email },
  });
}

export function resetPassword({ token, password }) {
  return apiRequest("/auth/reset-password", {
    method: "POST",
    body: { token, password },
  });
}

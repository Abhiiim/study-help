import { apiRequest } from "./http";

export function listItems(accessToken, filters = {}) {
  return apiRequest("/items", {
    token: accessToken,
    query: filters,
  });
}

export function fetchItemStats(accessToken) {
  return apiRequest("/items/stats", {
    token: accessToken,
  });
}

export function createItem(accessToken, payload) {
  return apiRequest("/items", {
    method: "POST",
    token: accessToken,
    body: payload,
  });
}

export function getItem(accessToken, itemId) {
  return apiRequest(`/items/${itemId}`, {
    token: accessToken,
  });
}

export function updateItem(accessToken, itemId, payload) {
  return apiRequest(`/items/${itemId}`, {
    method: "PATCH",
    token: accessToken,
    body: payload,
  });
}

export function deleteItem(accessToken, itemId) {
  return apiRequest(`/items/${itemId}`, {
    method: "DELETE",
    token: accessToken,
  });
}

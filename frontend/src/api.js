const API_BASE_URL = "/api/v1";

export function getToken() {
  return localStorage.getItem("token");
}

export function setAuth(token, user) {
  if (token) localStorage.setItem("token", token);
  if (user) localStorage.setItem("user", JSON.stringify(user));
}

export function clearAuth() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
}

export function getUser() {
  const data = localStorage.getItem("user");
  if (!data || data === "undefined" || data === "null") return null;
  try {
    return JSON.parse(data);
  } catch (_) {
    return null;
  }
}

export async function apiRequest(endpoint, method = "GET", body = null, requireAuth = false, customHeaders = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...customHeaders,
  };

  if (requireAuth) {
    const token = getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  const options = {
    method,
    headers,
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

  // Parse Rate Limit Headers
  const limit = response.headers.get("X-RateLimit-Limit");
  const remaining = response.headers.get("X-RateLimit-Remaining");
  const retryAfter = response.headers.get("Retry-After") || "14";

  if (remaining !== null) {
    window.dispatchEvent(new CustomEvent("ratelimit-update", { detail: { limit, remaining } }));
  }

  if (response.status === 429) {
    window.dispatchEvent(new CustomEvent("ratelimit-exceeded", { detail: { retryAfter: parseInt(retryAfter, 10) } }));
    throw new Error(`Rate limit exceeded. Please retry in ${retryAfter} seconds.`);
  }

  const totalCountHeader = response.headers.get("X-Total-Count");
  const totalCount = totalCountHeader ? parseInt(totalCountHeader, 10) : null;

  if (!response.ok) {
    let errMessage = "An error occurred";
    try {
      const errData = await response.json();
      errMessage = errData.detail || (errData.error && errData.error.message) || response.statusText;
    } catch (_) {
      errMessage = `HTTP Error ${response.status}: ${response.statusText}`;
    }
    throw new Error(errMessage);
  }

  if (response.status === 204) return { data: null, totalCount };
  
  const text = await response.text();
  const data = text ? JSON.parse(text) : null;
  return { data, totalCount };
}

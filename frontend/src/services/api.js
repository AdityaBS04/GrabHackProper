import axios from "axios";

const API_BASE_URL =
  process.env.REACT_APP_API_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const stored = localStorage.getItem("user");
  if (stored) {
    try {
      config.headers.Authorization = `Bearer ${JSON.parse(stored).username}`;
    } catch {
      localStorage.removeItem("user");
    }
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !isSignInRequest(error.config)) {
      localStorage.removeItem("user");
      window.location.assign("/signin");
    }
    return Promise.reject(error);
  }
);

/** A rejected sign-in is a form error, not an expired session. */
function isSignInRequest(config) {
  return Boolean(config?.url && config.url.includes("/login"));
}

export function currentUser() {
  try {
    return JSON.parse(localStorage.getItem("user") || "null");
  } catch {
    return null;
  }
}

export function signOut() {
  localStorage.removeItem("user");
}

export default api;

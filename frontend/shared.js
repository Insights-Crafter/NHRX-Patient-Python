const API_BASE = (window.NHRX_API_BASE || "http://127.0.0.1:8000").replace(/\/$/, "");

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => `${item.loc?.at(-1) || "Field"}: ${item.msg}`).join(". ")
      : detail || "Request failed. Please try again.";
    throw new Error(message);
  }
  return data;
}

function showMessage(element, message, kind = "error") {
  element.textContent = message;
  element.className = `notice ${kind}`;
  element.hidden = false;
}

function setBusy(button, busy, label) {
  button.disabled = busy;
  button.textContent = busy ? "Please wait…" : label;
}

function requireToken() {
  const token = localStorage.getItem("nhrx_access_token");
  if (!token) window.location.replace("login.html");
  return token;
}

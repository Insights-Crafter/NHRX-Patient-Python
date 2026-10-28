const API_BASE = (window.NHRX_API_BASE || "/api").replace(/\/$/, "");
const busyButtonMarkup = new WeakMap();

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => `${humanizeField(item.loc?.at(-1))}: ${item.msg}`).join(". ")
      : detail || "We couldn't complete that request. Please try again.";
    throw new Error(message);
  }
  return data;
}

function humanizeField(field) {
  if (!field) return "Field";
  return String(field).replaceAll("_", " ").replace(/([a-z])([A-Z])/g, "$1 $2");
}

function showFeedback(message, kind = "error", duration = 4200) {
  let widget = document.querySelector("#feedback-widget");
  if (!widget) {
    widget = document.createElement("div");
    widget.id = "feedback-widget";
    widget.className = "feedback-widget";
    widget.setAttribute("role", "status");
    widget.setAttribute("aria-live", "polite");
    widget.innerHTML = '<span class="feedback-icon" aria-hidden="true"></span><p></p><button type="button" aria-label="Dismiss message">×</button>';
    document.body.append(widget);
  }

  clearTimeout(widget.dismissTimer);
  widget.className = `feedback-widget ${kind}`;
  widget.setAttribute("role", kind === "error" ? "alert" : "status");
  widget.querySelector("p").textContent = message;
  widget.querySelector(".feedback-icon").textContent = kind === "success" ? "✓" : "!";
  widget.hidden = false;

  return new Promise((resolve) => {
    const dismiss = () => {
      clearTimeout(widget.dismissTimer);
      widget.classList.add("feedback-leaving");
      window.setTimeout(() => {
        widget.hidden = true;
        widget.classList.remove("feedback-leaving");
        resolve();
      }, 220);
    };
    widget.querySelector("button").onclick = dismiss;
    widget.dismissTimer = window.setTimeout(dismiss, duration);
  });
}

function setBusy(button, busy, label) {
  if (busy) {
    if (!busyButtonMarkup.has(button)) busyButtonMarkup.set(button, button.innerHTML);
    button.disabled = true;
    button.innerHTML = `<span class="button-spinner" aria-hidden="true"></span>${label}`;
  } else {
    button.disabled = false;
    button.innerHTML = busyButtonMarkup.get(button) || label;
  }
}

function validateForm(form) {
  for (const field of form.querySelectorAll("input, select, textarea")) {
    field.setCustomValidity("");
    if (field.type !== "password" && field.type !== "date") {
      field.value = field.value.trim();
    }
    if (field.required && !field.value.trim()) {
      field.setCustomValidity(`${field.labels?.[0]?.textContent.trim() || "This field"} is required.`);
    }
  }
  if (!form.checkValidity()) {
    form.reportValidity();
    return false;
  }
  return true;
}

function requireToken() {
  const token = localStorage.getItem("nhrx_access_token");
  if (!token) window.location.replace("login.html");
  return token;
}

function signOut() {
  localStorage.removeItem("nhrx_access_token");
  sessionStorage.removeItem("nhrx_login_succeeded");
  window.location.replace("login.html");
}

function setActiveNavigation() {
  const currentPage = window.location.pathname.split("/").pop();
  document.querySelectorAll("[data-page]").forEach((link) => {
    if (link.dataset.page === currentPage) {
      link.classList.add("active");
      link.setAttribute("aria-current", "page");
    }
  });
}

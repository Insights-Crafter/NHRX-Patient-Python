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

function setPatientAvatarFallback(name) {
  const avatar = document.querySelector("#header-avatar");
  if (!avatar) return;
  avatar.dataset.fallback = String(name || "P").charAt(0).toUpperCase();
  if (!avatar.querySelector("img")) avatar.textContent = avatar.dataset.fallback;
}

function setupPatientAvatar(token) {
  const avatar = document.querySelector("#header-avatar");
  if (!avatar || !token) return;
  const input = document.createElement("input");
  input.type = "file";
  input.accept = "image/jpeg,image/png,image/webp";
  input.setAttribute("aria-label", "Choose a profile image");
  input.className = "visually-hidden-file-input";
  document.body.append(input);

  const previewDialog = document.createElement("div");
  previewDialog.className = "profile-image-backdrop";
  previewDialog.hidden = true;
  previewDialog.innerHTML = `
    <section class="profile-image-dialog" role="dialog" aria-modal="true" aria-labelledby="profile-image-title" tabindex="-1">
      <button class="profile-image-close" type="button" aria-label="Close profile image preview">×</button>
      <div class="profile-image-large" id="profile-image-large" aria-hidden="true"></div>
      <h2 id="profile-image-title">Profile photo</h2>
      <p>Use a clear photo so your profile is easy to recognize.</p>
      <button class="profile-image-change" type="button">📷 &nbsp; Change photo</button>
    </section>`;
  document.body.append(previewDialog);
  const dialog = previewDialog.querySelector(".profile-image-dialog");
  const largePreview = previewDialog.querySelector("#profile-image-large");
  const changeButton = previewDialog.querySelector(".profile-image-change");
  const closeButton = previewDialog.querySelector(".profile-image-close");

  const renderLargePreview = () => {
    const currentImage = avatar.querySelector("img");
    largePreview.replaceChildren();
    if (currentImage) {
      const image = document.createElement("img");
      image.src = currentImage.src;
      image.alt = "";
      largePreview.append(image);
    } else {
      largePreview.textContent = avatar.dataset.fallback || avatar.textContent || "P";
    }
  };
  const closePreview = () => {
    previewDialog.hidden = true;
    avatar.focus({ preventScroll: true });
  };
  const openPreview = () => {
    renderLargePreview();
    previewDialog.hidden = false;
    changeButton.focus({ preventScroll: true });
  };
  closeButton.addEventListener("click", closePreview);
  changeButton.addEventListener("click", () => input.click());
  previewDialog.addEventListener("click", (event) => {
    if (event.target === previewDialog) closePreview();
  });
  dialog.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closePreview();
    if (event.key === "Tab") {
      const first = closeButton;
      const last = changeButton;
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }
  });

  const showPreview = (event) => {
    event.preventDefault();
    event.stopPropagation();
    openPreview();
  };
  avatar.addEventListener("click", showPreview);
  avatar.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") showPreview(event);
  });

  let refreshed = false;
  const refreshAvatar = async () => {
    try {
      const response = await fetch(`${API_BASE}/patients/me/images`, {
        headers: { Authorization: `Bearer ${token}` },
        cache: "no-store",
      });
      if (!response.ok) return;
      const images = await response.json();
      const latest = Array.isArray(images) ? images[0] : null;
      if (!latest?.imageUrl) {
        if (avatar.querySelector("img")) avatar.textContent = avatar.dataset.fallback || "P";
        if (!previewDialog.hidden) renderLargePreview();
        return;
      }
      const image = document.createElement("img");
      image.src = latest.imageUrl;
      image.alt = "";
      image.addEventListener("error", () => {
        if (refreshed) return;
        refreshed = true;
        refreshAvatar();
      }, { once: true });
      avatar.replaceChildren(image);
      avatar.setAttribute("aria-label", "Change profile image");
      avatar.title = "View profile image";
      if (!previewDialog.hidden) renderLargePreview();
    } catch (_) {
      // Keep the patient's initials visible if image loading is unavailable.
    }
  };

  input.addEventListener("change", async () => {
    const file = input.files?.[0];
    if (!file) return;
    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      await showFeedback("Choose a JPEG, PNG, or WebP image.", "error");
      input.value = "";
      return;
    }
    if (file.size > 8 * 1024 * 1024) {
      await showFeedback("Images must be 8 MB or smaller.", "error");
      input.value = "";
      return;
    }
    avatar.setAttribute("aria-busy", "true");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(`${API_BASE}/patients/me/images`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(result.detail || "Image upload failed.");
      refreshed = false;
      await refreshAvatar();
      window.dispatchEvent(new Event("patient-images-updated"));
      await showFeedback("Profile image updated.", "success");
    } catch (error) {
      await showFeedback(error.message || "Image upload failed.", "error");
    } finally {
      avatar.removeAttribute("aria-busy");
      input.value = "";
    }
  });

  window.addEventListener("patient-images-updated", refreshAvatar);
  refreshAvatar();
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

(() => {
  const token = requireToken();
  if (!token) return;

  setActiveNavigation();
  document.querySelector("#signout").addEventListener("click", signOut);
  setupPatientAvatar(token);

  const menu = document.querySelector("#dashboard-sidebar");
  const toggle = document.querySelector("#mobile-nav-toggle");
  const scrim = document.querySelector("#sidebar-scrim");
  const setMenuOpen = (open) => {
    menu.classList.toggle("sidebar-open", open);
    scrim.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
  };
  toggle.addEventListener("click", () => setMenuOpen(!menu.classList.contains("sidebar-open")));
  scrim.addEventListener("click", () => setMenuOpen(false));

  const featureCopy = {
    "medical-records": ["Medical records", "This section is still being built. Your personal health information will appear here when it is connected securely."],
    "lab-results": ["Lab results", "This page isn’t here yet. Your test results will appear here when this section is added to the portal."],
    "visit-summaries": ["Visit summaries", "This page isn’t here yet. Visit summaries will appear here when this section is added to the portal."],
    prescriptions: ["Prescriptions", "This page isn’t here yet. Prescription details will appear here when this section is added to the portal."],
    "health-summary": ["Health summary", "This section is still being built. It will show your conditions, allergies, medications and blood group when connected securely."],
    allergies: ["Allergies", "This page isn’t here yet. Allergy details will appear here when this section is added to the portal."],
    medications: ["Medications", "This page isn’t here yet. Medication details will appear here when this section is added to the portal."],
    conditions: ["Conditions", "This page isn’t here yet. Condition details will appear here when this section is added to the portal."],
    "blood-group": ["Blood group", "This page isn’t here yet. Blood group details will appear here when this section is added to the portal."],
    "appointment-summary": ["Visit summary", "This page isn’t here yet. Consultation summaries will appear here when this section is added to the portal."],
    notifications: ["Notifications", "This page isn’t here yet. Portal updates will appear here when notifications are added."],
  };
  const dashboardColumns = document.querySelector(".dashboard-columns");
  const quickActions = document.querySelector(".quick-actions");
  const intro = document.querySelector(".dashboard-intro");
  const featureView = document.querySelector("#feature-view");
  const imagesPanel = document.querySelector("#patient-images");
  function showView(view) {
    if (!featureCopy[view]) return;
    document.querySelector("#feature-title").textContent = featureCopy[view][0];
    document.querySelector("#feature-description").textContent = featureCopy[view][1];
    dashboardColumns.hidden = true;
    quickActions.hidden = true;
    intro.hidden = true;
    imagesPanel.hidden = true;
    featureView.hidden = false;
    document.querySelector(".modern-dashboard-main").classList.add("feature-mode");
    history.replaceState(null, "", `#${view}`);
    featureView.focus({ preventScroll: true });
    window.scrollTo({ top: 0, behavior: "smooth" });
    setMenuOpen(false);
  }
  function showDashboard() {
    dashboardColumns.hidden = false;
    quickActions.hidden = false;
    intro.hidden = false;
    imagesPanel.hidden = false;
    featureView.hidden = true;
    document.querySelector(".modern-dashboard-main").classList.remove("feature-mode");
    history.replaceState(null, "", "#dashboard");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
  document.querySelectorAll("[data-view]").forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      showView(link.dataset.view);
    });
  });
  document.querySelectorAll(".feature-home-button, #feature-back").forEach((link) => {
    link.addEventListener("click", (event) => { event.preventDefault(); showDashboard(); });
  });
  if (featureCopy[window.location.hash.slice(1)]) showView(window.location.hash.slice(1));

  const createElement = (tag, className, content) => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (content !== undefined) element.textContent = content;
    return element;
  };
  const toDate = (value) => {
    const parsed = new Date(`${value}T00:00:00`);
    return Number.isNaN(parsed.getTime()) ? null : parsed;
  };
  const formatDate = (value, options = { month: "short", day: "numeric", year: "numeric" }) => {
    const date = toDate(value);
    return date ? new Intl.DateTimeFormat(undefined, options).format(date) : "Date not provided";
  };
  const formatTime = (value) => {
    if (!value) return "Time not provided";
    const [hour, minute] = String(value).split(":").map(Number);
    if (!Number.isFinite(hour) || !Number.isFinite(minute)) return String(value);
    return new Intl.DateTimeFormat(undefined, { hour: "numeric", minute: "2-digit" }).format(new Date(2000, 0, 1, hour, minute));
  };
  const setState = (id, message, kind = "info") => {
    const state = document.getElementById(id);
    state.textContent = message;
    state.className = `dashboard-state ${kind}`;
    state.hidden = false;
  };
  const addRetry = (stateId, loader) => {
    const state = document.getElementById(stateId);
    const button = createElement("button", "retry-button", "Try again");
    button.type = "button";
    button.addEventListener("click", loader);
    state.append(document.createElement("br"), button);
  };
  const authHeaders = { Authorization: `Bearer ${token}` };

  async function loadPatient() {
    try {
      const patient = await apiRequest("/patients/me", { headers: authHeaders });
      const firstName = patient.firstName || "Patient";
      const fullName = [patient.firstName, patient.lastName].filter(Boolean).join(" ") || firstName;
      document.querySelector("#patient-first-name").textContent = firstName;
      document.querySelector("#header-name").textContent = fullName;
      setPatientAvatarFallback(firstName);
      document.querySelector("#patient-id").textContent = `#${patient.patientID}`;
    } catch (error) {
      if (/unauthorized|credentials|token|auth/i.test(error.message)) {
        localStorage.removeItem("nhrx_access_token");
        await showFeedback("Your sign-in may have expired. Please sign in again.", "error", 1500);
        window.location.replace("login.html");
        return;
      }
      document.querySelector("#patient-first-name").textContent = "there";
      document.querySelector("#patient-id").textContent = "—";
      const profileError = document.querySelector("#profile-load-error");
      profileError.textContent = "We couldn’t load your profile details. You can still review your appointments.";
      profileError.hidden = false;
    }
  }

  function appointmentDateTime(item) {
    return `${item.AppointmentDate || ""}T${item.AppointmentTime || "00:00"}`;
  }
  function renderUpcoming(items) {
    const state = document.querySelector("#upcoming-state");
    const list = document.querySelector("#upcoming-list");
    list.replaceChildren();
    const today = new Date(); today.setHours(0, 0, 0, 0);
    const upcoming = items.filter((item) => {
      const date = toDate(item.AppointmentDate);
      return String(item.Status || "").toLowerCase() === "pending" && date && date >= today;
    }).sort((a, b) => appointmentDateTime(a).localeCompare(appointmentDateTime(b))).slice(0, 3);
    if (!upcoming.length) { setState("upcoming-state", "No upcoming appointments yet. When you book a visit, it will appear here."); return; }
    state.hidden = true;
    list.hidden = false;
    for (const item of upcoming) {
      const article = createElement("article", "upcoming-appointment");
      const date = toDate(item.AppointmentDate);
      const dateBox = createElement("div", "appointment-date-box");
      dateBox.append(createElement("span", "appointment-month", date ? new Intl.DateTimeFormat(undefined, { month: "short" }).format(date) : "—"));
      dateBox.append(createElement("strong", "appointment-day", date ? String(date.getDate()) : "—"));
      dateBox.append(createElement("span", "appointment-weekday", date ? new Intl.DateTimeFormat(undefined, { weekday: "short" }).format(date) : ""));
      const details = createElement("div", "upcoming-details");
      details.append(createElement("p", "appointment-time", formatTime(item.AppointmentTime)));
      details.append(createElement("h3", "", item.doctorName ? `Dr. ${item.doctorName.replace(/^Dr\.\s*/i, "")}` : "Doctor details not provided"));
      details.append(createElement("p", "appointment-specialty", item.specialityName || "Specialty not provided"));
      details.append(createElement("p", "appointment-location", item.hospitalName || "Clinic details not provided"));
      const actions = createElement("div", "appointment-actions");
      const view = createElement("a", "appointment-primary-action", "View details");
      view.href = "appointments.html";
      const reschedule = createElement("a", "appointment-secondary-action", "Reschedule");
      reschedule.href = "appointments.html";
      actions.append(view, reschedule);
      article.append(dateBox, details, actions);
      list.append(article);
    }
  }
  function renderPast(items) {
    const state = document.querySelector("#past-state");
    const list = document.querySelector("#past-list");
    list.replaceChildren();
    const now = new Date();
    const past = items.filter((item) => {
      const status = String(item.Status || "").toLowerCase();
      const date = toDate(item.AppointmentDate);
      return ["completed", "rejected", "cancelled", "canceled"].includes(status) || (date && date < new Date(now.getFullYear(), now.getMonth(), now.getDate()));
    }).sort((a, b) => appointmentDateTime(b).localeCompare(appointmentDateTime(a))).slice(0, 4);
    if (!past.length) { setState("past-state", "Your past appointments will appear here after your first visit."); return; }
    state.hidden = true;
    list.hidden = false;
    for (const item of past) {
      const row = createElement("article", "past-appointment-row");
      const date = toDate(item.AppointmentDate);
      const dateBox = createElement("div", "past-date-box");
      dateBox.append(createElement("span", "", date ? new Intl.DateTimeFormat(undefined, { month: "short" }).format(date) : "—"));
      dateBox.append(createElement("strong", "", date ? String(date.getDate()) : "—"));
      const info = createElement("div", "past-doctor");
      info.append(createElement("strong", "", item.doctorName ? `Dr. ${item.doctorName.replace(/^Dr\.\s*/i, "")}` : "Doctor details not provided"));
      info.append(createElement("small", "", item.specialityName || "Specialty not provided"));
      const place = createElement("div", "past-place");
      place.append(createElement("strong", "", formatTime(item.AppointmentTime)));
      place.append(createElement("small", "", item.hospitalName || "Clinic details not provided"));
      const summary = createElement("a", "past-summary-button", "View summary");
      summary.href = "#appointment-summary";
      summary.dataset.view = "appointment-summary";
      summary.addEventListener("click", (event) => { event.preventDefault(); showView("appointment-summary"); });
      row.append(dateBox, info, place, summary);
      list.append(row);
    }
  }
  async function loadAppointments() {
    setState("upcoming-state", "Loading your appointments…");
    setState("past-state", "Loading appointment history…");
    document.querySelector("#upcoming-list").hidden = true;
    document.querySelector("#past-list").hidden = true;
    try {
      const items = await apiRequest("/appointments", { headers: authHeaders });
      renderUpcoming(Array.isArray(items) ? items : []);
      renderPast(Array.isArray(items) ? items : []);
    } catch (error) {
      setState("upcoming-state", "We couldn’t load your appointments. Please try again.", "error");
      setState("past-state", "We couldn’t load your appointment history. Please try again.", "error");
      addRetry("upcoming-state", loadAppointments);
      addRetry("past-state", loadAppointments);
    }
  }

  const imageState = document.querySelector("#patient-images-state");
  const imageGrid = document.querySelector("#patient-images-grid");
  const renewedImageUrls = new Set();
  const formatBytes = (bytes) => bytes < 1024 * 1024
    ? `${Math.max(1, Math.round(bytes / 1024))} KB`
    : `${(bytes / (1024 * 1024)).toFixed(1)} MB`;

  async function loadPatientImages() {
    setState("patient-images-state", "Loading your images…");
    imageGrid.hidden = true;
    imageGrid.replaceChildren();
    try {
      const response = await fetch(`${API_BASE}/patients/me/images`, { headers: authHeaders });
      const images = await response.json().catch(() => []);
      if (!response.ok) throw new Error("Images could not be loaded.");
      if (!Array.isArray(images) || images.length === 0) {
        setState("patient-images-state", "No images yet. Upload an image and it will appear here.");
        return;
      }
      imageState.hidden = true;
      imageGrid.hidden = false;
      for (const image of images) {
        const card = createElement("article", "patient-image-card");
        const preview = createElement("img", "patient-image-preview");
        preview.src = image.imageUrl;
        preview.alt = "Image uploaded to your patient portal";
        preview.loading = "lazy";
        preview.addEventListener("error", () => {
          if (renewedImageUrls.has(image.imageID)) return;
          renewedImageUrls.add(image.imageID);
          loadPatientImages();
        }, { once: true });
        const info = createElement("div", "patient-image-info");
        const date = image.uploadedAt ? new Date(image.uploadedAt) : null;
        info.append(createElement("strong", "", date && !Number.isNaN(date.getTime())
          ? new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(date)
          : "Uploaded image"));
        info.append(createElement("small", "", formatBytes(Number(image.fileSize) || 0)));
        const remove = createElement("button", "patient-image-delete", "Delete");
        remove.type = "button";
        remove.setAttribute("aria-label", "Delete uploaded image");
        remove.addEventListener("click", () => deletePatientImage(image.imageID, remove));
        card.append(preview, info, remove);
        imageGrid.append(card);
      }
    } catch (error) {
      setState("patient-images-state", "We couldn’t load your images. Please try again.", "error");
      addRetry("patient-images-state", loadPatientImages);
    }
  }

  async function deletePatientImage(imageId, button) {
    if (!window.confirm("Delete this image from your patient portal?")) return;
    setBusy(button, true, "Deleting…");
    try {
      await apiRequest(`/patients/me/images/${encodeURIComponent(imageId)}`, {
        method: "DELETE",
        headers: authHeaders,
      });
      window.dispatchEvent(new Event("patient-images-updated"));
      await loadPatientImages();
      await showFeedback("Image deleted from your portal.", "success");
    } catch (error) {
      await showFeedback(error.message || "Image could not be deleted.", "error");
      setBusy(button, false, "Delete");
    }
  }

  loadPatient();
  loadAppointments();
  loadPatientImages();
  window.addEventListener("patient-images-updated", loadPatientImages);
})();

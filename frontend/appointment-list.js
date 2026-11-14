(() => {
  const token = requireToken();
  if (!token) return;
  setActiveNavigation();
  const statusText = document.querySelector("#appointments-status");
  const list = document.querySelector("#appointments-list");
  const refreshButton = document.querySelector("#refresh-appointments");
  const isPendingView = window.location.pathname.endsWith("appointments.html")
    && !window.location.pathname.endsWith("past-appointments.html");

  function request(path, options = {}) {
    return apiRequest(path, {
      ...options,
      headers: { ...(options.headers || {}), Authorization: `Bearer ${token}` },
    });
  }

  function localDateString(date = new Date()) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  }

  function isInPast(item) {
    const value = `${item.AppointmentDate || ""}T${String(item.AppointmentTime || "00:00").slice(0, 8)}`;
    const appointmentAt = new Date(value);
    return !Number.isNaN(appointmentAt.getTime()) && appointmentAt < new Date();
  }

  function statusBadge(value) {
    const badge = document.createElement("span");
    const normalized = String(value || "Unknown");
    badge.className = `appointment-status status-${normalized.toLowerCase()}`;
    badge.textContent = normalized;
    return badge;
  }

  async function loadAppointments() {
    refreshButton.disabled = true;
    statusText.textContent = "Loading appointments…";
    list.replaceChildren();
    try {
      const allAppointments = await request("/appointments");
      const appointments = allAppointments.filter((item) => {
        const value = String(item.Status || "").toLowerCase();
        const terminal = ["completed", "rejected", "cancelled", "canceled"].includes(value);
        return isPendingView
          ? value === "pending" && !isInPast(item)
          : terminal || isInPast(item);
      }).sort((a, b) => `${a.AppointmentDate}T${a.AppointmentTime}`.localeCompare(`${b.AppointmentDate}T${b.AppointmentTime}`) * (isPendingView ? 1 : -1));
      statusText.textContent = appointments.length
        ? `${appointments.length} ${isPendingView ? "pending" : "past"} appointment${appointments.length === 1 ? "" : "s"}`
        : isPendingView ? "You have no upcoming appointments." : "You have no past appointments yet.";

      for (const item of appointments) {
        const card = document.createElement("article");
        card.className = "appointment-card appointment-list-card";
        const details = document.createElement("div");
        details.className = "appointment-card-details";
        const titleRow = document.createElement("div");
        titleRow.className = "appointment-title-row";
        const title = document.createElement("h3");
        title.textContent = item.doctorName || "Doctor";
        titleRow.append(title, statusBadge(item.Status));
        const meta = document.createElement("p");
        meta.className = "appointment-when";
        const apptDate = new Date(`${item.AppointmentDate}T00:00:00`);
        meta.textContent = `${apptDate.toLocaleDateString(undefined, { weekday: "long", year: "numeric", month: "long", day: "numeric" })} at ${(item.AppointmentTime || "").slice(0, 5)}`;
        const venue = document.createElement("p");
        venue.className = "appointment-venue";
        venue.textContent = [item.specialityName, item.hospitalName?.toLocaleUpperCase(), item.City].filter(Boolean).join(" · ") || "Appointment details";
        details.append(titleRow, meta, venue);
        if (item.Complaint) {
          const complaint = document.createElement("p");
          complaint.className = "appointment-complaint";
          complaint.textContent = item.Complaint;
          details.append(complaint);
        }
        card.append(details);

        if (isPendingView) {
          const actions = document.createElement("div");
          actions.className = "pending-appointment-actions";
          const dateInput = document.createElement("input");
          dateInput.type = "date";
          dateInput.min = localDateString();
          dateInput.setAttribute("aria-label", "New appointment date");
          const timeSelect = document.createElement("select");
          timeSelect.disabled = true;
          timeSelect.add(new Option("Choose date first", ""));
          timeSelect.setAttribute("aria-label", "New appointment time");
          dateInput.addEventListener("change", async () => {
            timeSelect.replaceChildren(new Option("Loading times…", ""));
            if (!dateInput.value) { timeSelect.disabled = true; return; }
            try {
              const slots = await apiRequest(`/doctors/${item.DoctorID}/availability?date=${encodeURIComponent(dateInput.value)}`);
              timeSelect.replaceChildren(new Option(slots.length ? "Choose a time" : "No times available", ""));
              for (const slot of slots) timeSelect.add(new Option(slot.slice(0, 5), slot));
              timeSelect.disabled = slots.length === 0;
            } catch (error) {
              timeSelect.replaceChildren(new Option("Could not load times", ""));
              timeSelect.disabled = true;
              await showFeedback(error.message, "error");
            }
          });
          const reschedule = document.createElement("button");
          reschedule.type = "button";
          reschedule.className = "button secondary";
          reschedule.textContent = "Reschedule";
          reschedule.addEventListener("click", async () => {
            if (!dateInput.value || !timeSelect.value) { await showFeedback("Choose a new date and time first.", "error"); return; }
            reschedule.disabled = true;
            try {
              await request(`/appointments/${item.AppointmentID}`, { method: "PATCH", body: JSON.stringify({ AppointmentDate: dateInput.value, AppointmentTime: timeSelect.value }) });
              await loadAppointments();
              await showFeedback("Appointment rescheduled.", "success");
            } catch (error) { reschedule.disabled = false; await showFeedback(error.message, "error"); }
          });
          const cancel = document.createElement("button");
          cancel.type = "button";
          cancel.className = "button secondary";
          cancel.textContent = "Cancel appointment";
          cancel.addEventListener("click", async () => {
            if (!window.confirm("Cancel this appointment?")) return;
            cancel.disabled = true;
            try {
              await request(`/appointments/${item.AppointmentID}`, { method: "DELETE" });
              await loadAppointments();
              await showFeedback("Appointment cancelled.", "success");
            } catch (error) { cancel.disabled = false; await showFeedback(error.message, "error"); }
          });
          actions.append(dateInput, timeSelect, reschedule, cancel);
          card.append(actions);
        }
        list.append(card);
      }
    } catch (error) {
      statusText.textContent = `Could not load appointments: ${error.message}`;
    } finally {
      refreshButton.disabled = false;
    }
  }

  refreshButton.addEventListener("click", loadAppointments);
  loadAppointments();
})();

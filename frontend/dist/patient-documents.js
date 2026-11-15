(() => {
  const token = requireToken();
  if (!token) return;

  const panel = document.querySelector("#patient-documents");
  const title = document.querySelector("#feature-title");
  const description = document.querySelector("#feature-description");
  const featureView = panel?.closest(".feature-view");
  if (!panel || !title || !description) return;

  const messages = {
    "medical-records": ["Medical records", "Reports and prescriptions your doctor has uploaded.", ""],
    "lab-results": ["Reports", "View reports and results uploaded by your doctor.", "report"],
    prescriptions: ["Prescriptions", "View prescriptions uploaded by your doctor.", "prescription"],
  };
  const element = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  };

  async function load(view) {
    const copy = messages[view];
    if (!copy) {
      panel.hidden = true;
      featureView?.classList.remove("documents-mode");
      return;
    }
    panel.hidden = false;
    featureView?.classList.add("documents-mode");
    title.textContent = copy[0];
    description.textContent = copy[1];
    panel.replaceChildren(element("p", "dashboard-state", "Loading your documents…"));
    try {
      const query = copy[2] ? `?type=${encodeURIComponent(copy[2])}` : "";
      const records = await apiRequest(`/patients/me/documents${query}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!records.length) {
        const label = copy[2] === "prescription" ? "prescriptions" : "reports";
        panel.replaceChildren(element("p", "dashboard-state", `Your doctor hasn’t uploaded any ${label} yet.`));
        return;
      }
      const list = element("div", "patient-document-list");
      for (const record of records) {
        const card = element("article", "patient-document-card");
        const details = element("div", "patient-document-details");
        details.append(element("strong", "", record.fileName || (record.documentType === "prescription" ? "Prescription" : "Report")));
        const meta = [record.documentType === "prescription" ? "Prescription" : "Report"];
        if (record.uploadedAt) {
          const uploaded = new Date(record.uploadedAt);
          if (!Number.isNaN(uploaded.getTime())) meta.push(new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(uploaded));
        }
        details.append(element("small", "", meta.join(" · ")));
        if (record.description) details.append(element("p", "", record.description));
        const open = element("a", "patient-document-open", record.available === false ? "File unavailable" : "View file");
        try {
          if (record.available === false || !record.documentUrl) throw new Error("File unavailable");
          const url = new URL(record.documentUrl);
          if (url.protocol !== "https:") throw new Error("Invalid document URL");
          open.href = url.href;
          open.target = "_blank";
          open.rel = "noopener noreferrer";
        } catch {
          open.setAttribute("aria-disabled", "true");
        }
        if (record.available === false) details.append(element("small", "patient-document-missing", "This file is missing from storage. Please contact your care team."));
        card.append(details, open);
        list.append(card);
      }
      panel.replaceChildren(list);
    } catch {
      const state = element("p", "dashboard-state error", "We couldn’t load your documents. Please try again.");
      const retry = element("button", "retry-button", "Try again");
      retry.type = "button";
      retry.addEventListener("click", () => load(view));
      state.append(document.createElement("br"), retry);
      panel.replaceChildren(state);
    }
  }

  document.querySelectorAll("[data-view]").forEach((link) => {
    link.addEventListener("click", () => setTimeout(() => load(link.dataset.view), 0));
  });
  const current = window.location.hash.slice(1);
  if (messages[current]) load(current);
})();

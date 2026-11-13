(() => {
  const token = requireToken();
  if (!token) return;

  const page = window.location.pathname.split("/").pop() || "home.html";
  const oldHeader = document.querySelector("header.topbar");
  const main = document.querySelector("main");
  if (!main) return;

  document.body.classList.add("nhrx-dashboard", "portal-inner-page");
  const shell = document.createElement("div");
  shell.className = "dashboard-shell";
  const sidebar = document.createElement("aside");
  sidebar.className = "dashboard-sidebar";
  sidebar.id = "dashboard-sidebar";
  sidebar.setAttribute("aria-label", "Patient portal navigation");
  sidebar.innerHTML = `
    <a class="dashboard-brand" href="home.html"><img src="nhrx-mark.svg?v=20261113-blue" alt=""><span><strong>NHRX</strong><small>Patient Portal</small></span></a>
    <nav class="sidebar-nav" aria-label="Main navigation">
      <a data-page="home.html" href="home.html"><span aria-hidden="true">🏠</span>Dashboard</a>
      <a data-page="appointments.html" href="appointments.html"><span aria-hidden="true">📅</span>Appointments</a>
      <a data-page="past-appointments.html" href="past-appointments.html"><span aria-hidden="true">🕘</span>Past appointments</a>
      <a data-page="booking.html" href="booking.html"><span aria-hidden="true">🩺</span>Book Appointment</a>
      <a href="home.html#medical-records"><span aria-hidden="true">📋</span>Medical Records</a>
      <a href="home.html#prescriptions"><span aria-hidden="true">💊</span>Prescriptions</a>
      <a href="home.html#lab-results"><span aria-hidden="true">🧪</span>Lab Results</a>
      <a href="home.html#health-summary"><span aria-hidden="true">💙</span>Health Summary</a>
      <a href="home.html#patient-images"><span aria-hidden="true">🖼️</span>My Images</a>
      <a data-page="contact.html" href="contact.html"><span aria-hidden="true">📞</span>Contact details</a>
      <a data-page="address.html" href="address.html"><span aria-hidden="true">🏡</span>Home address</a>
    </nav>
    <div class="sidebar-help"><span class="sidebar-help-icon" aria-hidden="true">ⓘ</span><strong>Need help?</strong><p>For account assistance, contact your care provider.</p></div>`;

  const content = document.createElement("div");
  content.className = "dashboard-content";
  const header = document.createElement("header");
  header.className = "dashboard-header";
  header.innerHTML = `
    <button class="mobile-nav-toggle" id="mobile-nav-toggle" type="button" aria-expanded="false" aria-controls="dashboard-sidebar" aria-label="Open navigation"><span></span><span></span><span></span></button>
    <div class="header-spacer"></div>
    <a class="notification-button" href="home.html#notifications" aria-label="Notifications"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4"/></svg></a>
    <details class="profile-menu"><summary><span class="profile-avatar profile-avatar-uploadable" id="header-avatar" role="button" tabindex="0" aria-label="Set profile image" title="Set profile image">P</span><span class="profile-menu-name" id="header-name">My account</span><span class="profile-chevron" aria-hidden="true">⌄</span></summary>
      <div class="profile-dropdown"><a href="contact.html">Contact details</a><a href="address.html">Home address</a><button id="signout" type="button">Sign out</button></div>
    </details>`;
  const scrim = document.createElement("div");
  scrim.className = "sidebar-scrim";
  scrim.id = "sidebar-scrim";
  scrim.hidden = true;

  oldHeader?.remove();
  document.body.insertBefore(shell, document.body.firstChild);
  shell.append(sidebar, content);
  content.append(header, main);
  document.body.append(scrim);

  setActiveNavigation();
  document.querySelector("#signout").addEventListener("click", signOut);
  setupPatientAvatar(token);
  const toggle = document.querySelector("#mobile-nav-toggle");
  const setMenuOpen = (open) => {
    sidebar.classList.toggle("sidebar-open", open);
    scrim.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
  };
  toggle.addEventListener("click", () => setMenuOpen(!sidebar.classList.contains("sidebar-open")));
  scrim.addEventListener("click", () => setMenuOpen(false));
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") setMenuOpen(false); });
  sidebar.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => setMenuOpen(false)));

  apiRequest("/patients/me", { headers: { Authorization: `Bearer ${token}` } }).then((patient) => {
    const firstName = patient.firstName || "Patient";
    const fullName = [patient.firstName, patient.lastName].filter(Boolean).join(" ") || "My account";
    document.querySelector("#header-name").textContent = fullName;
    setPatientAvatarFallback(firstName);
  }).catch(() => {});

  if (page === "appointments.html" || page === "past-appointments.html") {
    const title = document.querySelector(".directory-hero h1");
    if (title) title.textContent = page === "appointments.html" ? "Your upcoming care." : "Your appointment history.";
  }
})();

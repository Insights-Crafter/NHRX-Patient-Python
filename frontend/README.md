# NHRX Patient Portal

The frontend is a responsive patient portal with registration, sign-in, a patient overview, and separate account pages for home address and contact details.

## Patient flows

- Registration validates patient details in the browser and submits to `POST /patients/register`.
- Sign-in validates the national ID and password, then calls `POST /auth/login`.
- The overview loads the authenticated profile from `GET /patients/me` and links to the account update pages.
- The address page loads and saves with `GET` and `PATCH /patients/me/address`.
- The contact page loads and saves with `GET` and `PATCH /patients/me/contact`.
- The booking page filters doctors, shows 30-minute availability from `GET /doctors/{doctor_id}/availability`, and books through authenticated `POST /appointments`.
- The patient dashboard links to separate pending and past appointment pages. Pending appointments show status and support rescheduling/cancellation; past appointments show completed and rejected records. These pages use `GET /appointments`, `PATCH /appointments/{appointment_id}`, and `DELETE /appointments/{appointment_id}`. The API scopes appointment changes to the signed-in patient.

Availability is generated from the doctor's recurring weekday schedule in `DoctorTimings_Dummy`; each appointment occupies a 30-minute slot. Booking checks availability again before saving, so a slot selected earlier can still be rejected if another patient booked it.

Successful registration and sign-in show a timed confirmation widget before navigating to the next page. Account update pages show timed success or error feedback without moving the user away from the form.

The UI uses native browser constraints plus shared JavaScript validation before API requests. The API remains the source of truth and validates every submitted request independently.

## Local API connection

`config.js` points to `http://localhost:8000` for local development with VS Code Live Server and a directly running FastAPI server. Start Uvicorn on port 8000. For Docker Compose or deployment through Nginx, set `window.NHRX_API_BASE` to `/api`; Nginx forwards those requests to the backend container. The frontend Dockerfile copies all top-level HTML, CSS, JavaScript, and SVG files into Nginx's document root, so `booking.html` and `past-appointments.html` are served as static pages automatically.

For Cloudflare Pages, build with `python build_frontend.py` and publish `dist`. Set the Pages build variable `API_BASE_URL` to the Render API's HTTPS origin (no `/api` suffix). Set `CORS_ORIGINS` on Render to the exact Cloudflare Pages origin. The frontend calls API routes such as `/doctors` and `/appointments` directly. Use HTTPS before sending real patient data.

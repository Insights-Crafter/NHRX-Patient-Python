# NHRX Patient Portal

The frontend is a responsive patient portal with registration, sign-in, a patient overview, and separate account pages for home address and contact details.

## Patient flows

- Registration validates patient details in the browser and submits to `POST /patients/register`.
- Sign-in validates the national ID and password, then calls `POST /auth/login`.
- The overview loads the authenticated profile from `GET /patients/me` and links to the account update pages.
- The address page loads and saves with `GET` and `PATCH /patients/me/address`.
- The contact page loads and saves with `GET` and `PATCH /patients/me/contact`.
- The appointments page loads and filters doctors, shows 30-minute availability from `GET /doctors/{doctor_id}/availability`, and books through authenticated `POST /appointments`.
- Patients can view their bookings with `GET /appointments`, reschedule with `PATCH /appointments/{appointment_id}`, and cancel with `DELETE /appointments/{appointment_id}`. The API scopes appointment changes to the signed-in patient.

Availability is generated from the doctor's recurring weekday schedule in `DoctorTimings_Dummy`; each appointment occupies a 30-minute slot. Booking checks availability again before saving, so a slot selected earlier can still be rejected if another patient booked it.

Successful registration and sign-in show a timed confirmation widget before navigating to the next page. Account update pages show timed success or error feedback without moving the user away from the form.

The UI uses native browser constraints plus shared JavaScript validation before API requests. The API remains the source of truth and validates every submitted request independently.

## Local API connection

`config.js` uses the same-origin `/api` proxy configured in `nginx.conf`, which forwards requests to the backend container. For local development with VS Code Live Server and a directly running FastAPI server, temporarily set `window.NHRX_API_BASE` to `http://localhost:8000` in `config.js`.

For a teammate running a frontend on their own computer, set that frontend's API base to `http://<EC2_PUBLIC_IP>/api` (for this EC2 instance: `http://13.127.82.104/api`). Nginx removes `/api` when forwarding to FastAPI, so routes remain `/doctors`, `/doctors/filters`, `/patients/...`, and `/appointments/...`. FastAPI currently allows browser origins on `localhost` and `127.0.0.1`; a deployed frontend on another hostname must be added to the CORS allowlist. Use HTTPS before sending real patient data.

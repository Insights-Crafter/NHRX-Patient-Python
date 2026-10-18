# NHRX Patient Portal

The frontend is a responsive patient portal with registration, sign-in, a patient overview, and separate account pages for home address and contact details.

## Patient flows

- Registration validates patient details in the browser and submits to `POST /patients/register`.
- Sign-in validates the national ID and password, then calls `POST /auth/login`.
- The overview loads the authenticated profile from `GET /patients/me` and links to the account update pages.
- The address page loads and saves with `GET` and `PATCH /patients/me/address`.
- The contact page loads and saves with `GET` and `PATCH /patients/me/contact`.
- The appointments page loads doctors from `GET /doctors`, loads speciality and city options from `GET /doctors/filters`, and supports name, speciality, and city filtering. Search filters, pagination, and the selected doctor are represented in the URL query string.

Doctor discovery is connected to the backend. Availability lookup and appointment creation are not implemented in the backend yet, so selecting a doctor does not create or confirm an appointment.

Successful registration and sign-in show a timed confirmation widget before navigating to the next page. Account update pages show timed success or error feedback without moving the user away from the form.

The UI uses native browser constraints plus shared JavaScript validation before API requests. The API remains the source of truth and validates every submitted request independently.

## Local API connection

`config.js` points directly to `http://localhost:8000`. Start FastAPI on that address and open the frontend from a localhost web server so the browser can make API requests. FastAPI allows localhost origins on any port for local development. If your backend uses another port, update `window.NHRX_API_BASE` in `config.js`.

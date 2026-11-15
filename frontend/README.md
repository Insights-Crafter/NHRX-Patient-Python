# NHRX Patient Portal

The frontend is a responsive patient portal built with plain HTML, CSS, and JavaScript. It includes registration, sign-in, a patient dashboard, appointment booking and history, and account pages for home address and contact details.

## Patient flows

- Registration validates patient details in the browser and submits to `POST /patients/register`.
- Sign-in validates the national ID and password, then calls `POST /auth/login`.
- The dashboard loads the authenticated profile from `GET /patients/me` and patient-scoped appointments from `GET /appointments`. It displays upcoming and past visits and links to the account pages.
- The address page loads and saves with `GET` and `PATCH /patients/me/address`.
- The contact page loads and saves with `GET` and `PATCH /patients/me/contact`.
- The booking page filters doctors, shows 30-minute availability from `GET /doctors/{doctor_id}/availability`, and books through authenticated `POST /appointments`.
- The patient dashboard links to separate pending and past appointment pages. Pending appointments show status and support rescheduling/cancellation; past appointments show completed and rejected records. These pages use `GET /appointments`, `PATCH /appointments/{appointment_id}`, and `DELETE /appointments/{appointment_id}`. The API scopes appointment changes to the signed-in patient.

Availability is generated from the doctor's recurring weekday schedule in `DoctorTimings_Dummy`; each appointment occupies a 30-minute slot. Booking checks availability again before saving, so a slot selected earlier can still be rejected if another patient booked it.

Successful registration and sign-in show a timed confirmation widget before navigating to the next page. Account update pages show timed success or error feedback without moving the user away from the form.

The UI uses native browser constraints plus shared JavaScript validation before API requests. The API remains the source of truth and validates every submitted request independently.

The dashboard's `dashboard.js` contains its UI rendering and view-state helpers. `portal-shell.js` supplies the shared sidebar, responsive mobile navigation, profile menu, and sign-out control on authenticated pages. Reports and prescriptions uploaded by a doctor appear in the patient's Medical Records, Reports, and Prescriptions views.

## Local API connection

`config.js` currently points to the Render API at `https://nhrx-patient-python.onrender.com`. For local development with VS Code Live Server and a directly running FastAPI server, change it to `http://localhost:8000`. For Docker Compose or deployment through Nginx, set `window.NHRX_API_BASE` to `/api`; Nginx forwards those requests to the backend container. The frontend Dockerfile copies top-level HTML, CSS, JavaScript, and SVG files into Nginx's document root, so `dashboard.js`, `booking.html`, and `past-appointments.html` are served automatically.

For Cloudflare Pages, set the project root directory to `frontend`, build with `python build_frontend.py`, and publish `dist`. `API_BASE_URL` is optional: the build uses the Render API URL in `config.js` by default, or an `API_BASE_URL` build variable can override it. Set `CORS_ORIGINS` on Render to the exact Cloudflare Pages origin. The frontend calls API routes such as `/doctors` and `/appointments` directly. Use HTTPS before sending real patient data.

## Patient image uploads (Cloudflare R2)

Click the circular profile image in the header to choose or change a JPEG, PNG, or WebP profile image (up to 8 MB). The **My images** dashboard section displays uploaded images and supports deleting them. Uploads go through the authenticated backend, which checks the file signature, creates a patient-scoped random object key, uploads the file to a private R2 bucket, and stores that key plus content type, size, patient ID, and upload time in `PatientImages`. It does not store image bytes or expiring URLs in PostgreSQL. `GET /patients/me/images` returns a five-minute signed URL only for the logged-in patient's rows; `DELETE /patients/me/images/{image_id}` removes the patient's metadata and object.

For local development, set `R2_ENDPOINT`, `R2_ACCESS_KEY`, `R2_SECRET_KEY`, and `R2_PATIENT_BUCKET` in `.env` for profile images. Set `R2_REPORTS_ENDPOINT`, `R2_REPORTS_ACCESS_KEY_ID`, `R2_REPORTS_SECRET_ACCESS_KEY`, and `R2_REPORTS_BUCKET` for medical documents (or use the patient bucket settings if the files share a bucket). In Render, set these on the API service using an R2 API token with read access for patient views and write access if doctors upload through this API. Keep buckets private and never add R2 credentials to frontend configuration.

## Doctor-uploaded reports and prescriptions (Cloudflare R2)

An authenticated doctor can upload a PDF, JPEG, PNG, or WebP file (up to 20 MB) for an appointment they own with `POST /doctors/me/appointments/{appointment_id}/documents`. Send multipart form fields `documentType` (`report` or `prescription`), optional `description`, and `file`. Medical files are stored privately in the reports bucket. `GET /patients/me/documents` returns the signed-in patient's existing `LabReport` rows, prescription object keys on `MedicalRecords`, and new `PatientDocuments` entries with five-minute signed URLs; use `?type=report` or `?type=prescription` to filter. The portal requests fresh URLs as the patient opens these sections.

After deploying the code, apply the database migration once against the production database: `alembic upgrade head`. `python-multipart` is listed in `requirements.txt` for FastAPI multipart form uploads. Then deploy the frontend so the **My images** gallery and patient document views can use the new endpoints.

# NHRX patient frontend

Three page patient portal: registration, sign in, and a post-login dashboard. Registration submits patient details and address together to `POST /patients/register`. The API inserts the patient first, uses the generated `patientID` for the address row, and commits both in one transaction. The dashboard loads the authenticated profile and address with `GET /patients/me` and `GET /patients/me/address`; address edits use the existing authenticated `PATCH /patients/me/updateAdress` endpoint.

## Run with Docker Compose

See the repository's [`DEPLOYMENT.md`](../DEPLOYMENT.md) for local Docker testing and EC2 deployment. Nginx serves these static pages and proxies same-origin `/api/` requests to FastAPI. The bearer token remains in browser local storage and is removed at sign out or when the profile request is rejected. Records and appointments are placeholders because there are no corresponding patient-facing API endpoints yet.

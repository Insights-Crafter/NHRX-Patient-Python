# NHRX patient frontend

Three page patient portal: registration, sign in, and a post-login dashboard. It uses the FastAPI endpoints `POST /patients/register`, `POST /auth/login`, and authenticated `GET /patients/me`.

## Run locally

1. Start the API from the repository root: `uvicorn app.main:app --reload` (configure the database, `JWT_SECRET_KEY`, and `AES_SIV_KEY` in `.env` first).
2. If the API is not at `http://127.0.0.1:8000`, edit `NHRX_API_BASE` in `config.js`.
3. In a second terminal, run `python -m http.server 5500 --directory frontend` from the repository root.
4. Open `http://127.0.0.1:5500/`.

The API enables CORS for localhost and 127.0.0.1 origins so the separate development server can call it. The bearer token is kept in browser local storage and removed at sign out or when the profile request is rejected. The dashboard shows a profile summary; records and appointments are placeholders because there are no corresponding patient-facing API endpoints yet.

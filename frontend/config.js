// Use the local FastAPI process during frontend development. When the portal
// is served by the Nginx container, route API calls through its /api proxy so
// the browser never tries to contact localhost on the visitor's machine.
const isLocalFrontend = ["localhost", "127.0.0.1"].includes(window.location.hostname)
  && window.location.port !== "80";
window.NHRX_API_BASE = isLocalFrontend ? "http://localhost:8000" : "/api";

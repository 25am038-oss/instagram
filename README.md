# InstaStyle Demo API (FastAPI + MongoDB)

A hosting-ready backend for a clearly labelled Instagram-inspired **demo UI**.

## Safety design
- The API has **no username or password fields** and never accepts passwords.
- Password reconfirmation remains in the demo frontend and should use invented demo text only.
- MongoDB stores only a random demo session ID, demo status, and timestamps.
- Demo sessions expire automatically after 24 hours (MongoDB TTL index).
- This does not authenticate users with Instagram. Redirect to `https://www.instagram.com/` only after the demo flow is complete.

## Run locally (Windows PowerShell)

1. Install Python 3.11+.
2. Create a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. Create a MongoDB Atlas cluster and database user. Add your current public IP to Atlas Network Access for local testing.
4. Copy `.env.example` to `.env` and replace the placeholder URI. Never commit `.env`.
5. Load the variables into your shell (PowerShell example):

   ```powershell
   $env:MONGODB_URI="your-real-atlas-connection-string"
   $env:MONGODB_DB="instastyle_demo"
   $env:FRONTEND_ORIGINS="http://127.0.0.1:5500,http://localhost:5500"
   uvicorn main:app --reload --port 8000
   ```

6. Open `http://127.0.0.1:8000/docs` to test the API.

## Endpoints
- `GET /` — API info
- `GET /health` — health check
- `POST /api/demo-sessions` — create a demo session (body: `{"demo_only": true}`)
- `POST /api/demo-sessions/{session_id}/complete` — mark a session complete

## Connect your frontend
Call `POST /api/demo-sessions` when a visitor starts the demo. Keep the returned `session_id` in memory. After the local demo password entries match, call the completion endpoint. Do not send either password to the backend.

Example browser JavaScript:

```js
const API_BASE = "http://127.0.0.1:8000";

// Start demo (do not send username or password)
const response = await fetch(`${API_BASE}/api/demo-sessions`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ demo_only: true })
});
const session = await response.json();

// After the two invented demo password entries match:
await fetch(`${API_BASE}/api/demo-sessions/${session.session_id}/complete`, {
  method: "POST"
});

// Then, if desired, redirect to the official site:
window.location.href = "https://www.instagram.com/";
```

For deployment, change `API_BASE` to your deployed API URL and set `FRONTEND_ORIGINS` to the exact origin hosting your frontend.

## Deploy to Render
1. Push this folder to a GitHub repository.
2. In Render, create a Web Service from the repository (or use the included `render.yaml`).
3. Add `MONGODB_URI` as a secret environment variable in Render. Set `MONGODB_DB=instastyle_demo`.
4. Set `FRONTEND_ORIGINS` to the exact deployed frontend origin (for example, `https://your-demo-site.example`); do not leave broad wildcards.
5. Deploy, then test `/health` and `/docs`.

Keep MongoDB Atlas Network Access restricted where practical. Use a dedicated least-privilege database user. Never expose the MongoDB URI in frontend JavaScript or commit it to GitHub.

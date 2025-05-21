# Exercise A: Telephony‑Job Scheduler Service

### Description:
- Build a small Python microservice that exposes:
- A REST API endpoint POST /jobs to schedule an outbound “call job.”
- A background worker that picks up queued jobs and simulates sending them to Twilio by logging a message.
- A WebSocket endpoint /ws/jobs that streams job status updates to connected clients.

### Requirements:
- Use FastAPI (or Flask + Celery) for the HTTP/WebSocket server.
- Persist jobs in an in‑memory queue or lightweight database (e.g., SQLite).
- Containerize with Docker; expose ports 8000 (HTTP) and 8001 (WebSocket).
- Demonstrate job scheduling, processing, and streaming in your README.

### Evaluation Criteria:
- Code clarity and organization
- Correct use of async I/O for WebSocket streaming
- Robustness of job processing (e.g., error handling, retries)
- Quality of Dockerfile (layering, caching, image size)

---

# Exercise B: Secure AI‑Inference API

### Description:
- Create a Python/Node.js service that:
- Accepts POST /infer with a JSON payload, e.g. { "text": "Hello world" }.
- Applies a stub “model” (e.g., returns input text reversed) to simulate inference.
- Protects the endpoint with JWT-based authentication (you can mock a secret).
- Logs each request to stdout with a timestamp.

### Requirements:
- Use Express or Koa and the jsonwebtoken library.
- Provide a sample token generation script or instructions.
- Containerize with Docker; include Healthcheck in the Dockerfile.
- Write at least two unit tests for authentication failure and successful inference.

### Evaluation Criteria:
- Security of JWT implementation (token validation, error messages)
- Clean separation of concerns (middleware, routes, business logic)
- Test coverage and clarity
- Docker best practices (multi‑stage builds, small final image)
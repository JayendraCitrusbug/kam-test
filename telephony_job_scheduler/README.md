# Telephony Job Scheduler Service

## Step 1: Environment Setup

Create a `.env` file in the root directory using the `.env.temp` file as a reference.

## Step 2: Dockerized Setup

Build and run the FastAPI project in Docker containers using the following commands:

```bash
docker compose build
docker compose up
```

---

## Job Scheduling

To schedule a job at a specific time, make a `POST` request to the `/jobs/` API.

📘 **API Documentation**:  
Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive Swagger docs.

📤 **Sample Payload**:

```json
{
  "job_name": "test",
  "phone_number": "+1234567890",
  "schedule_time": "2025-05-20 12:00"
}
```

This will:
- Create a new job
- Enqueue it in the Redis queue for background processing at the scheduled time

---

## Job Tracking (Real-Time Updates)

To track job status in real time, connect to the WebSocket endpoint:

```
ws://localhost:8001/ws/jobs
```

You can use **Postman** to connect to the websocket.

### Events You Will Receive:

- ✅ **Job Scheduled** – when the job is created and waiting
- 🔄 **Job In Progress** – when the job starts processing (simulated call)
- ✔️ **Job Completed** – when the job is done

These updates are broadcast in real time using Redis Pub/Sub and WebSocket.

---

## Notes

- Redis is used for both background job queuing and pub/sub communication.
- Jobs are processed and updated through the `JobWorkerService`.
- WebSocket clients receive real-time job updates using `ConnectionManager`.

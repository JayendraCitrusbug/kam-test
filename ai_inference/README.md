# Secure AI‑Inference API

## Step 1: Environment Setup

Create a `.env` file in the root directory using the `.env.temp` file as a reference.

## Step 2: Dockerized Setup

Build and run the FastAPI project in Docker containers using the following commands:

```bash
docker build -t ai-inference-app .
docker run -d -p 8080:8080 --name ai-inference-container ai-inference-app
```

## AI Inference API

📘 **API Documentation:**
Visit [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs) for the interactive Swagger UI.

Make a call to the AI Inference API by sending a `POST` request to the /infer/ endpoint.

📤 **Sample Payload:**
```json
{
  "text": "Hello World"
}
```

You will receive the inferred output in the response.

**Authentication**

Make a call to the AI Inference API by sending a `GET` request to the /infer/token/ endpoint.

You will receive a `token` in the response data. Use this token to authorize your API calls.

---

## Test Cases

To run the test cases:

1. Create a virtual environment:
```bash
python -m venv venv
pip install -r requirements.txt
```

2. Activate the virtual environment:

- On Windows:
```bash
venv\Scripts\activate
```

- On macOS/Linux:
```bash
source venv/bin/activate
```

3. Execute below command:
```bash
pytest
```
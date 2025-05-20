from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.logging import setup_logging
from src.routers.inference_router import router as inference_router
from src.middleware.request_middleware import RequestLoggerMiddleware

setup_logging()

app = FastAPI()


app = FastAPI(
    title="AI Inference API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add request logging middleware
app.add_middleware(RequestLoggerMiddleware)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inference_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}

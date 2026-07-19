from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import ProcessRequest, ProcessResponse
from app.services.orchestrator import process_article


app = FastAPI(title="TextCheck AI Style Rewriter")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/process", response_model=ProcessResponse)
def process(request: ProcessRequest) -> ProcessResponse:
    return process_article(request.text)

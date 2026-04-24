from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import upload_router, analysis_router, stories_router, export_router

settings = get_settings()

app = FastAPI(title="Archiscribe", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(analysis_router)
app.include_router(stories_router)
app.include_router(export_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/providers")
def list_providers():
    providers = []
    if settings.openai_api_key:
        providers.append({"id": "openai", "name": "OpenAI GPT-4o"})
    if settings.anthropic_api_key:
        providers.append({"id": "anthropic", "name": "Anthropic Claude"})
    if settings.google_api_key:
        providers.append({"id": "gemini", "name": "Google Gemini"})
    if not providers:
        providers.append({"id": "openai", "name": "OpenAI GPT-4o (configure API key)"})
    return {"providers": providers}
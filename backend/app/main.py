from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, auth, media, practice
from app.api.v1 import lessons
from app.core.config import get_settings

app = FastAPI(title="JL API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lessons.router, prefix="/api/v1")
app.include_router(practice.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(media.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
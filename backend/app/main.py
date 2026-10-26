from fastapi import FastAPI

from app.api.v1 import lessons

app = FastAPI(title="JL API")
app.include_router(lessons.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
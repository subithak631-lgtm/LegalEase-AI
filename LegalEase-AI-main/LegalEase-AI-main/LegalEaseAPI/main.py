from fastapi import FastAPI
from LegalEaseAPI.routes import router

app = FastAPI(
    title="LegalEase API",
    description="Backend AI API for generating custom legal documents",
    version="1.0.0"
)

# Base health check route
@app.get("/")
def home():
    return {"status": "online", "message": "LegalEase API is active"}

# Register Modular Router
app.include_router(router)
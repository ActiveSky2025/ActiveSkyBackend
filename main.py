from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routes import weather, activities

app = FastAPI(title="Outdoor Weather API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(weather.router, prefix="/api/weather", tags=["weather"])
app.include_router(activities.router, prefix="/api/activities", tags=["activities"])

@app.get("/")
def root():
    return {"message": "Outdoor Weather API", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}
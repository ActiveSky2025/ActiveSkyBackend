from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routes import weather, activities, spots
from routes import weather, activities, spots, users


app = FastAPI(title="ActiveSky API", version="1.0.0")

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
app.include_router(spots.router, prefix="/api/spots", tags=["spots"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

@app.get("/")
def root():
    return {"message": "ActiveSky API", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}
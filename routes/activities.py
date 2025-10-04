from fastapi import APIRouter

router = APIRouter()

@router.get("/spots")
async def get_activity_spots(lat: float, lon: float, activity: str = None):
    """Obtener spots de actividades cercanos"""
    return {
        "message": "Activity spots endpoint",
        "lat": lat,
        "lon": lon,
        "activity": activity,
        "spots": []
    }

@router.get("/types")
async def get_activity_types():
    """Obtener tipos de actividades disponibles"""
    return {
        "activities": [
            {"id": "running", "name": "Running", "icon": "🏃"},
            {"id": "fishing", "name": "Pesca", "icon": "🎣"},
            {"id": "hiking", "name": "Senderismo", "icon": "🥾"},
            {"id": "cycling", "name": "Ciclismo", "icon": "🚴"}
        ]
    }
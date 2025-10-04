from fastapi import APIRouter

router = APIRouter()

@router.get("/forecast")
async def get_forecast(lat: float, lon: float, date: str):
    """Obtener pronóstico del clima"""
    return {
        "message": "Weather forecast endpoint",
        "lat": lat,
        "lon": lon,
        "date": date
    }

@router.post("/recommendations")
async def get_recommendations(lat: float, lon: float, date: str, activity: str):
    """Obtener recomendaciones para actividad"""
    return {
        "message": "Recommendations endpoint",
        "activity": activity,
        "recommendation": "TODO: implementar lógica"
    }
from fastapi import APIRouter
from services import database_services as db

router = APIRouter()


@router.get("/")
async def get_all_activities():
    """Obtener todas las actividades disponibles"""
    activities = db.get_all_activities()
    return {"activities": activities, "total": len(activities)}


@router.get("/{slug}")
async def get_activity_by_slug(slug: str):
    """Obtener actividad específica por slug"""
    activity = db.get_activity_by_slug(slug)
    if not activity:
        return {"error": "Actividad no encontrada"}, 404
    return activity
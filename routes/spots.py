from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel
from services import database_services as db
from datetime import date
import uuid

router = APIRouter()


# ============================================
# SCHEMAS
# ============================================

class SpotCreate(BaseModel):
    name: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    activity_id: int
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None


class ReviewCreate(BaseModel):
    rating: int  # 1-5
    comment: Optional[str] = None
    user_id: Optional[str] = None  # ID del usuario logueado (opcional, debe ser UUID válido)


class VisitCreate(BaseModel):
    visit_date: date
    notes: Optional[str] = None
    user_id: Optional[str] = None  # ID del usuario logueado (opcional, debe ser UUID válido)
    weather_data: Optional[dict] = None  # Datos meteorológicos opcionales


# ============================================
# ENDPOINTS - SPOTS
# ============================================

@router.get("/nearby")
async def get_nearby_spots(
    lat: float,
    lon: float,
    radius_km: float = 10,
    activity_id: Optional[int] = None
):
    """
    Obtener spots cercanos a una ubicación.
    
    - **lat**: Latitud
    - **lon**: Longitud
    - **radius_km**: Radio de búsqueda en kilómetros (default: 10)
    - **activity_id**: Filtrar por actividad (opcional)
    """
    spots = db.get_spots_near_location(lat, lon, radius_km, activity_id)
    return {"spots": spots, "total": len(spots)}


@router.get("/activity/{activity_id}")
async def get_spots_by_activity(activity_id: int, limit: int = 50):
    """Obtener spots por tipo de actividad"""
    spots = db.get_spots_by_activity(activity_id, limit)
    return {"spots": spots, "total": len(spots)}


@router.get("/{spot_id}")
async def get_spot_detail(spot_id: str):
    """Obtener detalles completos de un spot"""
    try:
        spot = db.get_spot_by_id(spot_id)
        if not spot:
            raise HTTPException(status_code=404, detail="Spot no encontrado")
        
        # Agregar fotos
        photos = db.get_spot_photos(spot_id)
        spot['photos'] = photos
        
        return spot
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_new_spot(spot: SpotCreate, user_id: Optional[str] = None):
    """
    Crear un nuevo spot.
    Por ahora sin autenticación (user_id opcional).
    """
    try:
        spot_data = spot.dict()
        new_spot = db.create_spot(spot_data, user_id)
        return {"message": "Spot creado exitosamente", "spot": new_spot}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS - REVIEWS
# ============================================


@router.get("/{spot_id}/reviews")
async def get_spot_reviews(spot_id: str):
    """
    Obtener todas las reviews de un spot.
    Devuelve un arreglo con las reviews ordenadas por fecha (más recientes primero).
    """
    try:
        reviews = db.get_reviews_by_spot(spot_id)
        
        # Opcional: calcular estadísticas
        if reviews:
            avg_rating = sum(r['rating'] for r in reviews) / len(reviews)
            rating_distribution = {
                '5': len([r for r in reviews if r['rating'] == 5]),
                '4': len([r for r in reviews if r['rating'] == 4]),
                '3': len([r for r in reviews if r['rating'] == 3]),
                '2': len([r for r in reviews if r['rating'] == 2]),
                '1': len([r for r in reviews if r['rating'] == 1])
            }
        else:
            avg_rating = 0
            rating_distribution = {'5': 0, '4': 0, '3': 0, '2': 0, '1': 0}
        
        return {
            "reviews": reviews,
            "total": len(reviews),
            "average_rating": round(avg_rating, 2),
            "rating_distribution": rating_distribution
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{spot_id}/reviews")
async def add_review(spot_id: str, review: ReviewCreate):
    """Agregar una reseña a un spot"""
    try:
        # Validar que user_id esté presente
        if not review.user_id:
            raise HTTPException(status_code=400, detail="user_id es requerido. Debes estar logueado para dejar una reseña.")
        
        # Validar rating
        if review.rating < 1 or review.rating > 5:
            raise HTTPException(status_code=400, detail="Rating debe estar entre 1 y 5")
        
        new_review = db.create_review(spot_id, review.user_id, review.rating, review.comment)
        return {"message": "Reseña agregada exitosamente", "review": new_review}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





# ============================================
# ENDPOINTS - VISITS
# ============================================

@router.get("/{spot_id}/visits")
async def get_spot_visit_history(spot_id: str):
    """Obtener historial de visitas de un spot"""
    visits = db.get_visits_by_spot(spot_id)
    return {"visits": visits, "total": len(visits)}

@router.post("/{spot_id}/visit")
async def register_spot_visit(
    spot_id: str, 
    visit: VisitCreate
):
    """Registrar una visita a un spot (con datos meteorológicos opcionales)"""
    try:
        # Validar que user_id esté presente
        if not visit.user_id:
            raise HTTPException(status_code=400, detail="user_id es requerido. Debes estar logueado para registrar una visita.")
        
        new_visit = db.register_visit(
            visit.user_id, 
            spot_id, 
            visit.visit_date, 
            visit.notes,
            visit.weather_data  # Ahora viene del body
        )
        return {"message": "Visita registrada exitosamente", "visit": new_visit}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/visits/user/{user_id}")
async def get_user_visit_history(user_id: str):
    """Obtener historial de visitas de un usuario"""
    visits = db.get_user_visits(user_id)
    return {"visits": visits, "total": len(visits)}


# ============================================
# ENDPOINTS - PHOTOS
# ============================================

@router.post("/{spot_id}/photos")
async def upload_spot_photo(
    spot_id: str,
    file: UploadFile = File(...),
    caption: Optional[str] = Form(None),
    user_id: str = "anonymous"
):
    """
    Subir una foto a un spot.
    Acepta: JPG, JPEG, PNG, WEBP
    """
    try:
        # Validar extensión
        allowed_extensions = ['jpg', 'jpeg', 'png', 'webp']
        file_ext = file.filename.split('.')[-1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Formato de imagen no permitido")
        
        # Leer archivo
        file_bytes = await file.read()
        
        # Subir a Supabase Storage
        photo_url = db.upload_photo_to_storage(file_bytes, file_ext, user_id)
        
        # Registrar en base de datos
        photo_record = db.create_spot_photo(spot_id, user_id, photo_url, caption)
        
        return {
            "message": "Foto subida exitosamente",
            "photo": photo_record
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{spot_id}/photos")
async def get_spot_photos_list(spot_id: str):
    """Obtener todas las fotos de un spot"""
    photos = db.get_spot_photos(spot_id)
    return {"photos": photos, "total": len(photos)}
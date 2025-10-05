from typing import List, Dict, Any, Optional
from datetime import date
from services.supabase_client import get_supabase
import uuid

supabase = get_supabase()


# ============================================
# ACTIVITIES
# ============================================

def get_all_activities() -> List[Dict[str, Any]]:
    """Obtener todas las actividades disponibles"""
    response = supabase.table('activities').select('*').execute()
    return response.data


def get_activity_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    """Obtener actividad por slug"""
    response = supabase.table('activities').select('*').eq('slug', slug).single().execute()
    return response.data if response.data else None


# ============================================
# SPOTS
# ============================================

def get_spots_by_activity(activity_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Obtener spots por tipo de actividad"""
    response = supabase.table('spots') \
        .select('*, activities(name, slug, icon)') \
        .eq('activity_id', activity_id) \
        .limit(limit) \
        .execute()
    return response.data


def get_spots_near_location(lat: float, lon: float, radius_km: float = 10, activity_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Obtener spots cerca de una ubicación.
    Nota: Aproximación simple. Para mejor precisión usar PostGIS.
    """
    # Aproximación: 1 grado ≈ 111 km
    lat_range = radius_km / 111
    lon_range = radius_km / (111 * abs(lat) / 90 if lat != 0 else 1)
    
    query = supabase.table('spots').select('*, activities(name, slug, icon)')
    
    if activity_id:
        query = query.eq('activity_id', activity_id)
    
    response = query \
        .gte('latitude', lat - lat_range) \
        .lte('latitude', lat + lat_range) \
        .gte('longitude', lon - lon_range) \
        .lte('longitude', lon + lon_range) \
        .execute()
    
    return response.data


def create_spot(spot_data: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
    """Crear un nuevo spot"""
    if user_id:
        spot_data['created_by'] = user_id
    response = supabase.table('spots').insert(spot_data).execute()
    return response.data[0] if response.data else None


def get_spot_by_id(spot_id: str) -> Dict[str, Any]:
    """Obtener un spot por ID con reviews"""
    response = supabase.table('spots') \
        .select('*, activities(name, slug, icon), spot_reviews(rating, comment, created_at, users(username, avatar_url))') \
        .eq('id', spot_id) \
        .single() \
        .execute()
    return response.data


# ============================================
# REVIEWS
# ============================================

def create_review(spot_id: str, user_id: str, rating: int, comment: str = None) -> Dict[str, Any]:
    """Crear una reseña para un spot"""
    review_data = {
        'spot_id': spot_id,
        'user_id': user_id,
        'rating': rating,
        'comment': comment
    }
    response = supabase.table('spot_reviews').insert(review_data).execute()
    return response.data[0] if response.data else None


def get_reviews_by_spot(spot_id: str) -> List[Dict[str, Any]]:
    """Obtener todas las reseñas de un spot"""
    response = supabase.table('spot_reviews') \
        .select('*, users(username, avatar_url)') \
        .eq('spot_id', spot_id) \
        .order('created_at', desc=True) \
        .execute()
    return response.data


# ============================================
# VISITS
# ============================================

def register_visit(user_id: str, spot_id: str, visit_date: date, notes: str = None, weather_data: Dict = None) -> Dict[str, Any]:
    """Registrar una visita a un spot"""
    visit_data = {
        'user_id': user_id,
        'spot_id': spot_id,
        'visit_date': visit_date.isoformat(),
        'notes': notes,
        'weather_data': weather_data
    }
    response = supabase.table('user_visits').upsert(visit_data).execute()
    return response.data[0] if response.data else None


def get_user_visits(user_id: str) -> List[Dict[str, Any]]:
    """Obtener todas las visitas de un usuario"""
    response = supabase.table('user_visits') \
        .select('*, spots(name, latitude, longitude, activities(name, icon))') \
        .eq('user_id', user_id) \
        .order('visit_date', desc=True) \
        .execute()
    return response.data


# ============================================
# PHOTOS
# ============================================

def create_spot_photo(spot_id: str, user_id: str, photo_url: str, caption: str = None) -> Dict[str, Any]:
    """Registrar una foto de un spot"""
    photo_data = {
        'spot_id': spot_id,
        'user_id': user_id,
        'photo_url': photo_url,
        'caption': caption
    }
    response = supabase.table('spot_photos').insert(photo_data).execute()
    return response.data[0] if response.data else None


def get_spot_photos(spot_id: str) -> List[Dict[str, Any]]:
    """Obtener fotos de un spot"""
    response = supabase.table('spot_photos') \
        .select('*, users(username, avatar_url)') \
        .eq('spot_id', spot_id) \
        .order('created_at', desc=True) \
        .execute()
    return response.data


def upload_photo_to_storage(file_bytes: bytes, file_extension: str, user_id: str) -> str:
    """Subir foto al storage de Supabase y retornar URL pública"""
    filename = f"{user_id}/{uuid.uuid4()}.{file_extension}"
    
    supabase.storage.from_('spot-photos').upload(
        filename,
        file_bytes,
        {'content-type': f'image/{file_extension}'}
    )
    
    public_url = supabase.storage.from_('spot-photos').get_public_url(filename)
    return public_url


# ============================================
# USER PROFILE
# ============================================

def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Obtener perfil de usuario"""
    response = supabase.table('users') \
        .select('*, user_favorite_activities(activities(name, slug, icon))') \
        .eq('id', user_id) \
        .single() \
        .execute()
    return response.data


def update_user_profile(user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Actualizar perfil de usuario"""
    response = supabase.table('users') \
        .update(profile_data) \
        .eq('id', user_id) \
        .execute()
    return response.data[0] if response.data else None
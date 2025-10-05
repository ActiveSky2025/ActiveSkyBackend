from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field, EmailStr
from services import database_services as db
from typing import Optional
import uuid

router = APIRouter()

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    password: str = Field(..., min_length=6)  # En producción hashear

    class Config:
        json_schema_extra = {
            "example": {
                "username": "eljuguito90",
                "email": "eljuguito90@activesky.com",
                "full_name": "José González",
                "bio": "Amante de las actividades al aire libre",
                "avatar_url": "https://ui-avatars.com/api/?name=Jose",
                "password": "123456"
            }
        }

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None

@router.post("/")
async def create_user(user: UserCreate):
    """Crear nuevo usuario"""
    try:
        # Generar UUID para el usuario
        user_id = str(uuid.uuid4())
        
        user_data = {
            'id': user_id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'bio': user.bio,
            'avatar_url': user.avatar_url or f"https://ui-avatars.com/api/?name={user.full_name.replace(' ', '+')}&background=0dcaf0&color=fff",
            'password_hash': user.password  # ⚠️ En producción: bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
        }
        
        print(f"📥 Creando usuario: {user_data}")
        
        result = db.create_user(user_data)
        
        print(f"✅ Usuario creado: {result}")
        
        return {"message": "Usuario creado exitosamente", "user": result}
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="El username o email ya existe")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}")
async def get_user(user_id: str):
    """Obtener usuario por ID"""
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Ocultar password_hash
    if 'password_hash' in user:
        del user['password_hash']
    
    return user

@router.put("/{user_id}")
async def update_user(user_id: str, user_update: UserUpdate):
    """Actualizar usuario"""
    try:
        update_data = {k: v for k, v in user_update.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No hay datos para actualizar")
        
        result = db.update_user(user_id, update_data)
        
        if not result:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return {"message": "Usuario actualizado", "user": result}
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/visits")
async def get_user_visits(user_id: str):
    """Obtener visitas del usuario"""
    visits = db.get_user_visits(user_id)
    return {"visits": visits, "total": len(visits)}

@router.get("/{user_id}/reviews")
async def get_user_reviews(user_id: str):
    """Obtener reseñas del usuario"""
    reviews = db.get_user_reviews(user_id)
    return {"reviews": reviews, "total": len(reviews)}

@router.get("/by-email/{email}")
async def get_user_by_email(email: str):
    """Obtener usuario por email (para login)"""
    try:
        from services.supabase_client import get_supabase
        supabase = get_supabase()
        
        response = supabase.table('users').select('*').eq('email', email).single().execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        user = response.data
        
        # Ocultar password
        if 'password_hash' in user:
            del user['password_hash']
        
        return user
        
    except Exception as e:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
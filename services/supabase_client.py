from supabase import create_client, Client
from config import settings

# Cliente global de Supabase
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_supabase() -> Client:
    """Retorna instancia del cliente de Supabase"""
    return supabase
"""
Paquete de servicios para ActiveSky Backend

Este módulo contiene servicios para análisis meteorológico,
integración con APIs externas y procesamiento de datos climáticos.
"""

# Importar las funciones principales de weather_analytics
from .weather_analytics import (
    analyze_weather_data,
    analyze_temperature,
    analyze_precipitation,
    analyze_wind,
    analyze_clouds,
    analyze_uv,
    classify_precipitation_intensity,
    classify_wind_speed,
    classify_cloud_coverage,
    classify_uv_risk
)

# Definir qué funciones estarán disponibles con "from services import *"
_all_ = [
    # Funciones principales de análisis
    'analyze_weather_data',
    'analyze_temperature', 
    'analyze_precipitation',
    'analyze_wind',
    'analyze_clouds',
    'analyze_uv',
    
    # Funciones de clasificación
    'classify_precipitation_intensity',
    'classify_wind_speed', 
    'classify_cloud_coverage',
    'classify_uv_risk'
]

# Metadatos del paquete
_version_ = '1.0.0'
_author_ = 'ActiveSky Team'
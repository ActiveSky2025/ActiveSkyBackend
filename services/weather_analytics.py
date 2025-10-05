"""
Módulo de análisis estadístico para datos meteorológicos históricos de NASA POWER API
"""
from typing import List, Dict, Any
import statistics


def analyze_weather_data(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analiza datos meteorológicos históricos y devuelve estadísticas útiles.
    
    Args:
        results: Lista de diccionarios con parámetros de NASA POWER API
        
    Returns:
        Diccionario con análisis estadístico completo
    """
    if not results:
        return {"error": "No hay datos para analizar"}
    
    # Extraer todos los valores de cada parámetro
    temp_min_values = []
    temp_max_values = []
    wind_speed_values = []
    precipitation_values = []
    cloud_values = []
    uv_values = []
    
    for year_data in results:
        # Cada año puede tener múltiples días (si consultan rango)
        for date_key in year_data.get('T2M_MIN', {}).keys():
            if year_data.get('T2M_MIN', {}).get(date_key) is not None:
                temp_min_values.append(year_data['T2M_MIN'][date_key])
            if year_data.get('T2M_MAX', {}).get(date_key) is not None:
                temp_max_values.append(year_data['T2M_MAX'][date_key])
            if year_data.get('WS2M', {}).get(date_key) is not None:
                wind_speed_values.append(year_data['WS2M'][date_key])
            if year_data.get('PRECTOTCORR', {}).get(date_key) is not None:
                precipitation_values.append(year_data['PRECTOTCORR'][date_key])
            if year_data.get('CLOUD_AMT', {}).get(date_key) is not None:
                cloud_values.append(year_data['CLOUD_AMT'][date_key])
            if year_data.get('ALLSKY_SFC_UV_INDEX', {}).get(date_key) is not None:
                uv_values.append(year_data['ALLSKY_SFC_UV_INDEX'][date_key])
    
    # Análisis de temperatura
    temperature_analysis = analyze_temperature(temp_min_values, temp_max_values)
    
    # Análisis de precipitación (el más importante para probabilidades)
    precipitation_analysis = analyze_precipitation(precipitation_values)
    
    # Análisis de viento
    wind_analysis = analyze_wind(wind_speed_values)
    
    # Análisis de nubosidad
    cloud_analysis = analyze_clouds(cloud_values)
    
    # Análisis de índice UV
    uv_analysis = analyze_uv(uv_values)
    
    return {
        "temperature": temperature_analysis,
        "precipitation": precipitation_analysis,
        "wind": wind_analysis,
        "clouds": cloud_analysis,
        "uv": uv_analysis,
        "data_points": len(results),
        "years_analyzed": len(results)
    }


def analyze_temperature(min_values: List[float], max_values: List[float]) -> Dict[str, Any]:
    """Analiza temperaturas mínimas y máximas"""
    if not min_values or not max_values:
        return {"error": "Datos insuficientes"}
    
    return {
        "min": {
            "average": round(statistics.mean(min_values), 1),
            "median": round(statistics.median(min_values), 1),
            "lowest": round(min(min_values), 1),
            "highest": round(max(min_values), 1),
            "std_dev": round(statistics.stdev(min_values), 1) if len(min_values) > 1 else 0
        },
        "max": {
            "average": round(statistics.mean(max_values), 1),
            "median": round(statistics.median(max_values), 1),
            "lowest": round(min(max_values), 1),
            "highest": round(max(max_values), 1),
            "std_dev": round(statistics.stdev(max_values), 1) if len(max_values) > 1 else 0
        },
        "range": f"{round(min(min_values), 1)}°C - {round(max(max_values), 1)}°C",
        "typical_range": f"{round(statistics.mean(min_values), 1)}°C - {round(statistics.mean(max_values), 1)}°C"
    }


def analyze_precipitation(values: List[float]) -> Dict[str, Any]:
    """
    Analiza precipitación y calcula probabilidades.
    Este es el análisis más importante para predicción de lluvia.
    """
    if not values:
        return {"error": "Datos insuficientes"}
    
    # Filtrar días con lluvia (> 0.1 mm para evitar trazas)
    rainy_days = [v for v in values if v > 0.1]
    total_days = len(values)
    rainy_days_count = len(rainy_days)
    
    # Calcular probabilidad de lluvia
    rain_probability = round((rainy_days_count / total_days) * 100, 1) if total_days > 0 else 0
    
    # Promedio de precipitación cuando llovió
    avg_when_rained = round(statistics.mean(rainy_days), 1) if rainy_days else 0
    
    # Clasificar intensidad de lluvia histórica
    intensity_classification = classify_precipitation_intensity(rainy_days)
    
    return {
        "probability_of_rain": rain_probability,  # % de probabilidad
        "rainy_days": rainy_days_count,
        "total_days_analyzed": total_days,
        "average_when_rained": avg_when_rained,  # mm
        "max_recorded": round(max(values), 1) if values else 0,
        "median_precipitation": round(statistics.median(values), 1),
        "intensity_distribution": intensity_classification,
        "recommendation": get_rain_recommendation(rain_probability, avg_when_rained)
    }


def classify_precipitation_intensity(rainy_days: List[float]) -> Dict[str, Any]:
    """Clasifica la intensidad de lluvia en categorías"""
    if not rainy_days:
        return {}
    
    drizzle = len([v for v in rainy_days if 0.1 < v < 2])  # Llovizna
    light = len([v for v in rainy_days if 2 <= v < 10])    # Ligera
    moderate = len([v for v in rainy_days if 10 <= v < 30])  # Moderada
    heavy = len([v for v in rainy_days if v >= 30])        # Fuerte
    
    total = len(rainy_days)
    
    return {
        "drizzle": {"count": drizzle, "percentage": round((drizzle/total)*100, 1)},
        "light": {"count": light, "percentage": round((light/total)*100, 1)},
        "moderate": {"count": moderate, "percentage": round((moderate/total)*100, 1)},
        "heavy": {"count": heavy, "percentage": round((heavy/total)*100, 1)}
    }


def get_rain_recommendation(probability: float, avg_mm: float) -> str:
    """Genera recomendación basada en probabilidad y cantidad de lluvia"""
    if probability < 20:
        return "Muy baja probabilidad de lluvia. Condiciones ideales."
    elif probability < 40:
        return "Baja probabilidad de lluvia. Probablemente seguro."
    elif probability < 60:
        return "Probabilidad moderada de lluvia. Considera llevar protección."
    elif probability < 80:
        return "Alta probabilidad de lluvia. Planifica con precaución."
    else:
        if avg_mm > 20:
            return "Muy alta probabilidad de lluvia intensa. No recomendado."
        else:
            return "Muy alta probabilidad de lluvia. Lleva equipo impermeable."


def analyze_wind(values: List[float]) -> Dict[str, Any]:
    """Analiza velocidad del viento"""
    if not values:
        return {"error": "Datos insuficientes"}
    
    avg_speed = statistics.mean(values)
    max_speed = max(values)
    
    return {
        "average_speed": round(avg_speed, 1),  # m/s
        "max_speed": round(max_speed, 1),
        "median_speed": round(statistics.median(values), 1),
        "classification": classify_wind_speed(avg_speed),
        "max_classification": classify_wind_speed(max_speed),
        "recommendation": get_wind_recommendation(avg_speed, max_speed)
    }


def classify_wind_speed(speed: float) -> str:
    """Clasifica velocidad del viento"""
    if speed < 2:
        return "Calma"
    elif speed < 5:
        return "Brisa ligera"
    elif speed < 10:
        return "Viento moderado"
    elif speed < 15:
        return "Viento fuerte"
    else:
        return "Viento muy fuerte"


def get_wind_recommendation(avg: float, max_wind: float) -> str:
    """Recomendación basada en viento"""
    if max_wind > 15:
        return "Vientos muy fuertes registrados. Precaución para actividades al aire libre."
    elif max_wind > 10:
        return "Vientos fuertes posibles. Considera actividades protegidas."
    elif avg < 5:
        return "Vientos generalmente tranquilos. Buenas condiciones."
    else:
        return "Vientos moderados. Condiciones aceptables."


def analyze_clouds(values: List[float]) -> Dict[str, Any]:
    """Analiza cobertura de nubes"""
    if not values:
        return {"error": "Datos insuficientes"}
    
    avg_cloud = statistics.mean(values)
    
    return {
        "average_coverage": round(avg_cloud, 1),  # %
        "median_coverage": round(statistics.median(values), 1),
        "min_coverage": round(min(values), 1),
        "max_coverage": round(max(values), 1),
        "classification": classify_cloud_coverage(avg_cloud),
        "sunny_days": len([v for v in values if v < 25]),
        "cloudy_days": len([v for v in values if v > 75])
    }


def classify_cloud_coverage(coverage: float) -> str:
    """Clasifica cobertura de nubes"""
    if coverage < 25:
        return "Despejado"
    elif coverage < 50:
        return "Parcialmente nublado"
    elif coverage < 75:
        return "Nublado"
    else:
        return "Muy nublado"


def analyze_uv(values: List[float]) -> Dict[str, Any]:
    """Analiza índice UV"""
    if not values:
        return {"error": "Datos insuficientes"}
    
    avg_uv = statistics.mean(values)
    max_uv = max(values)
    
    return {
        "average_index": round(avg_uv, 1),
        "max_index": round(max_uv, 1),
        "median_index": round(statistics.median(values), 1),
        "risk_level": classify_uv_risk(avg_uv),
        "max_risk_level": classify_uv_risk(max_uv),
        "recommendation": get_uv_recommendation(max_uv)
    }


def classify_uv_risk(uv_index: float) -> str:
    """Clasifica riesgo UV"""
    if uv_index < 3:
        return "Bajo"
    elif uv_index < 6:
        return "Moderado"
    elif uv_index < 8:
        return "Alto"
    elif uv_index < 11:
        return "Muy alto"
    else:
        return "Extremo"


def get_uv_recommendation(max_uv: float) -> str:
    """Recomendación basada en UV"""
    if max_uv < 3:
        return "Protección UV mínima requerida."
    elif max_uv < 6:
        return "Usa protector solar. Busca sombra al mediodía."
    elif max_uv < 8:
        return "Protección necesaria. Protector solar, sombrero y lentes."
    else:
        return "Protección extra necesaria. Evita exposición prolongada."
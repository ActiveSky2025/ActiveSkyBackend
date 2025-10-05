# recomendacion.py (adaptado para análisis estadísticos)

# Diccionario con los rangos óptimos para cada actividad (usando promedios históricos)
rangos = {
    "Running": {
        "temperatura": (10, 22),
        "viento": (0, 5),  # m/s
        "uv": (0, 6),
        "precipitacion_probabilidad": (0, 30),  # % de probabilidad
        "nubes": (0, 70)  # %
    },
    "Ciclismo": {
        "temperatura": (12, 26),
        "viento": (0, 7),  # m/s
        "uv": (0, 7),
        "precipitacion_probabilidad": (0, 40),
        "nubes": (0, 80)
    },
    "Senderismo": {
        "temperatura": (8, 24),
        "viento": (0, 6),  # m/s
        "uv": (0, 6),
        "precipitacion_probabilidad": (0, 30),
        "nubes": (0, 80)
    },
    "Camping": {
        "temperatura": (10, 22),
        "viento": (0, 4),  # m/s
        "uv": (0, 7),
        "precipitacion_probabilidad": (0, 20),
        "nubes": (0, 90)
    },
    "Picnic": {
        "temperatura": (15, 28),
        "viento": (0, 4),  # m/s
        "uv": (0, 6),
        "precipitacion_probabilidad": (0, 10),
        "nubes": (10, 70)
    },
    "Playa": {
        "temperatura": (20, 32),
        "viento": (0, 6),  # m/s
        "uv": (3, 8),  # Necesita algo de sol pero no extremo
        "precipitacion_probabilidad": (0, 10),
        "nubes": (10, 50)
    }
}

def extraer_datos_desde_analytics(analytics_result: dict) -> dict:
    """
    Extrae y calcula los datos relevantes del análisis estadístico para recomendaciones.
    
    Args:
        analytics_result: Resultado completo de analyze_weather_data
        
    Returns:
        Diccionario con datos normalizados para comparar con rangos
    """
    if not analytics_result or "error" in analytics_result:
        return {}
    
    temp = analytics_result.get('temperature', {})
    wind = analytics_result.get('wind', {})
    precip = analytics_result.get('precipitation', {})
    clouds = analytics_result.get('clouds', {})
    uv = analytics_result.get('uv', {})
    
    # Calcular temperatura promedio (entre mínima y máxima promedio)
    temp_min_avg = temp.get('min', {}).get('average', 0)
    temp_max_avg = temp.get('max', {}).get('average', 0)
    temperatura_promedio = (temp_min_avg + temp_max_avg) / 2
    
    return {
        "temperatura": round(temperatura_promedio, 1),
        "viento": wind.get('average_speed', 0),
        "uv": uv.get('average_index', 0),
        "precipitacion_probabilidad": precip.get('probability_of_rain', 0),
        "nubes": clouds.get('average_coverage', 0)
    }

def evaluar_actividad_con_analytics(analytics_result: dict, actividad: str) -> str:
    """
    Evalúa si las condiciones históricas son adecuadas para una actividad específica
    usando los datos del análisis estadístico.
    
    Args:
        analytics_result: Resultado de analyze_weather_data
        actividad: Nombre de la actividad a evaluar
        
    Returns:
        String con la recomendación
    """
    if actividad not in rangos:
        return f"Actividad '{actividad}' no está definida en los parámetros."
    
    # Extraer datos normalizados del análisis
    datos = extraer_datos_desde_analytics(analytics_result)
    
    if not datos:
        return "No hay datos suficientes para realizar la evaluación"
    
    reglas = rangos[actividad]
    recomendaciones = []

    for parametro, (min_val, max_val) in reglas.items():
        valor = datos.get(parametro, None)
        if valor is None:
            continue  # si falta un dato, lo ignora

        if valor < min_val:
            recomendaciones.append(f"{parametro.capitalize()} muy bajo ({valor}) para {actividad}")
        elif valor > max_val:
            recomendaciones.append(f"{parametro.capitalize()} muy alto ({valor}) para {actividad}")

    if not recomendaciones:
        return f"✅ Condiciones históricas recomendadas para {actividad}"
    else:
        return f"⚠ Condiciones históricas no recomendadas para {actividad}: " + "; ".join(recomendaciones)

def obtener_recomendaciones_multiples(analytics_result: dict, actividades: list = None) -> dict:
    """
    Obtiene recomendaciones para múltiples actividades basadas en el análisis histórico.
    
    Args:
        analytics_result: Resultado de analyze_weather_data
        actividades: Lista de actividades a evaluar (None = todas)
        
    Returns:
        Diccionario con recomendaciones para cada actividad
    """
    if actividades is None:
        actividades = list(rangos.keys())
    
    datos = extraer_datos_desde_analytics(analytics_result)
    if not datos:
        return {"error": "No hay datos suficientes para realizar evaluaciones"}
    
    resultados = {}
    for actividad in actividades:
        resultados[actividad] = evaluar_actividad_con_analytics(analytics_result, actividad)
    
    # Encontrar la mejor actividad (si hay alguna recomendada)
    actividades_recomendadas = [act for act in actividades if "✅" in resultados[act]]
    mejor_actividad = actividades_recomendadas[0] if actividades_recomendadas else None
    
    return {
        "datos_utilizados": datos,
        "recomendaciones": resultados,
        "mejor_opcion": mejor_actividad,
        "resumen": f"{len(actividades_recomendadas)} de {len(actividades)} actividades son recomendables"
    }   

# Función de compatibilidad hacia atrás - para usar con datos simples si es necesario
def evaluar_clima(valores: dict, actividad: str) -> str:
    """
    Función original adaptada para mantener compatibilidad.
    Útil si en algún momento necesitas evaluar con datos simples.
    """
    if actividad not in rangos:
        return f"Actividad '{actividad}' no está definida en los parámetros."

    reglas = rangos[actividad]
    recomendaciones = []

    for parametro, (min_val, max_val) in reglas.items():
        valor = valores.get(parametro, None)
        if valor is None:
            continue

        if valor < min_val:
            recomendaciones.append(f"{parametro.capitalize()} muy bajo ({valor}) para {actividad}")
        elif valor > max_val:
            recomendaciones.append(f"{parametro.capitalize()} muy alto ({valor}) para {actividad}")

    if not recomendaciones:
        return f"✅ Clima recomendado para {actividad}"
    else:
        return f"⚠ Clima no recomendado para {actividad}: " + "; ".join(recomendaciones)


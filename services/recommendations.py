from funcion import (
    temperatura,
    humedad,
    viento,
    uv,
    precipitacion,
    nubes
)


# Diccionario con los rangos óptimos para cada actividad
rangos = {
    "Running": {
        "temperatura": (10, 22),
        "humedad": (40, 60),
        "viento": (0, 20),
        "uv": (0, 6),
        "precipitacion": (0, 1),
        "nubes": (0, 70)
    },
    "Ciclismo": {
        "temperatura": (12, 26),
        "humedad": (30, 65),
        "viento": (0, 25),
        "uv": (0, 7),
        "precipitacion": (0, 2),
        "nubes": (0, 80)
    },
    "Senderismo": {
        "temperatura": (8, 24),
        "humedad": (30, 70),
        "viento": (0, 20),
        "uv": (0, 6),
        "precipitacion": (0, 1),
        "nubes": (0, 80)
    },
    "Camping": {
        "temperatura": (10, 22),
        "humedad": (40, 70),
        "viento": (0, 15),
        "uv": (0, 7),
        "precipitacion": (0, 2),
        "nubes": (0, 90)
    }
}

def evaluar_clima(valores, actividad):
    """
    valores: dict con temperatura, humedad, viento, uv, precipitacion, nubes
    actividad: str (ejemplo: "Running", "Ciclismo", "Senderismo", "Camping")
    """
    if actividad not in rangos:
        return f"Actividad '{actividad}' no está definida en los parámetros."

    reglas = rangos[actividad]
    recomendaciones = []

    for parametro, (min_val, max_val) in reglas.items():
        valor = valores.get(parametro, None)
        if valor is None:
            continue  # si falta un dato, lo ignora

        if valor < min_val:
            recomendaciones.append(f"{parametro.capitalize()} muy bajo ({valor}) para {actividad}")
        elif valor > max_val:
            recomendaciones.append(f"{parametro.capitalize()} muy alto ({valor}) para {actividad}")

    if not recomendaciones:
        return f"✅ Clima recomendado para {actividad}"
    else:
        return f"⚠️ Clima no recomendado para {actividad}: " + "; ".join(recomendaciones)


# ----------------------
# Ejemplo de uso
# ----------------------

# Supongamos que la API te da estos valores:
valores_clima = {
    "temperatura": 28,
    "humedad": 65,
    "viento": 10,
    "uv": 8,
    "precipitacion": 0.5,
    "nubes": 50
}

actividad_usuario = "Running"

print(evaluar_clima(valores_clima, actividad_usuario))

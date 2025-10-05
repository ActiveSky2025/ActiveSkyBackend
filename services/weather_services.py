from typing import Any, Dict, Optional
from datetime import date, datetime
import requests

class ValidationError(Exception):
    """Excepción lanzada cuando la entrada no es válida."""


class ExternalAPIError(Exception):
    """Excepción lanzada cuando la llamada a la API externa falla."""


def get_weather_for(day: str,
                    place: Any,
                    activity: str,
                    options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    
    print("get_weather_for called with:", day, place, activity, options)
    opts = options or {}

    # 1) Validar/normalizar fecha
    try:
        parsed_day = datetime.strptime(day, "%Y%m%d").date()
        
    except Exception:
        raise ValidationError("'day' debe tener formato 'YYYYMMDD'")

    # 2) Normalizar place (aquí intentamos aceptar "lat, lon" en string)
    normalized_place: Dict[str, Any]
    if isinstance(place, dict) and 'lat' in place and 'lon' in place:
        normalized_place = { 'lat': float(place['lat']), 'lon': float(place['lon']), 'name': opts.get('place_name') }
    elif isinstance(place, str):
        # Intentar parsear coords en formato "lat, lon" (strings), ejemplo: "12.212, 2121.2"
        place_str = place.strip()
        coords = [p.strip() for p in place_str.split(',')]
        if len(coords) == 2:
            try:
                lat = float(coords[0])
                lon = float(coords[1])
                normalized_place = { 'lat': lat, 'lon': lon, 'name': opts.get('place_name') or place_str }
            except ValueError:
                # Si no se pueden convertir a float, tratamos el string como nombre de lugar
                normalized_place = { 'lat': None, 'lon': None, 'name': place_str }
        else:
            # No es "lat, lon" → lo dejamos como nombre
            normalized_place = { 'lat': None, 'lon': None, 'name': place_str }
    else:
        raise ValidationError("'place' debe ser dict{lat,lon} o string 'City,Country' o 'lat, lon'")

    # 3) Validar activity simple
    if not isinstance(activity, str) or not activity:
        raise ValidationError("'activity' debe ser un string no vacío")

    # 4) Aquí llamaríamos a la API externa. De momento devolvemos un resultado de ejemplo.
        
        
    parameters = "T2M_MIN,T2M_MAX,WS2M,PRECTOTCORR,CLOUD_AMT,ALLSKY_SFC_UV_INDEX"

    url  = "https://power.larc.nasa.gov/api/temporal/daily/point"

 
    results = []

    for i in range(1, 30):  
        year = parsed_day.year - i
        try:
            query_date = parsed_day.replace(year=year)
        except ValueError:
            # caso 29-feb en años no bisiestos: ajustar a 28-feb
            query_date = date(year, parsed_day.month, parsed_day.day - 1)

        start = int(query_date.strftime("%Y%m%d"))
        end = start  # misma fecha inicio/fin para un día concreto

        payload = {
            "start": start,
            "end": end,
            "latitude": normalized_place['lat'],
            "longitude": normalized_place['lon'],
            "community": "ag",
            "parameters": parameters,
            "format": "JSON"
        }

        try:
            r = requests.get(url, params=payload, timeout=7)
            r.raise_for_status()
            resp = r.json()
        except requests.exceptions.RequestException as e:
            # captura timeouts, conexión y HTTP errors
            raise ExternalAPIError(f"Error al llamar a la API externa: {e}")

        results.append(resp['properties']['parameter'])




    sample_result = {
        'weather': { 'data': results }
    }

    return sample_result


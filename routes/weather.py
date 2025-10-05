from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from services.weather_services import get_weather_for, ValidationError, ExternalAPIError
import services.weather_services as weather_services
import json
import io

router = APIRouter()


@router.get("/forecast")
async def get_weather_forecast(
    day: str,          # Formato: YYYYMMDD, ejemplo: 20251005
    lat: float,        # Ejemplo: 19.4326
    lon: float,        # Ejemplo: -99.1332
    activity: str,     # Ejemplo: "hiking"
    place_name: str = None
):
    """
    Obtener pronóstico basado en datos históricos de NASA POWER.
    
    - **day**: Fecha en formato YYYYMMDD (ej: 20251005)
    - **lat**: Latitud del lugar
    - **lon**: Longitud del lugar
    - **activity**: Tipo de actividad (running, cycling, hiking, etc)
    - **place_name**: Nombre opcional del lugar
    """
    try:
        place = {"lat": lat, "lon": lon}
        options = {"place_name": place_name} if place_name else None
        
        result = get_weather_for(day, place, activity, options)
        return result
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ExternalAPIError as e:
        raise HTTPException(status_code=503, detail=f"Error en API externa: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/recommendations")
async def get_forecast(date: str, activity: str, coordinates: str):
    """
    Obtener recomendaciones meteorológicas basadas en análisis histórico.
    
    - **date**: Fecha en formato YYYYMMDD (ej: 20251005)
    - **activity**: Tipo de actividad (running, cycling, hiking, etc)
    - **coordinates**: Coordenadas en formato "lat,lon" (ej: "19.4326,-99.1332")
    """
    try:
        weather_data = weather_services.get_weather_for(date, coordinates, activity)
        
        # Regresar weather_data
        return {
            "message": "ENDPOINT DE PRONOSTICO",
            "activity": activity,
            "coordinates": coordinates,
            "date": date,
            "weather": weather_data
        }
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ExternalAPIError as e:
        raise HTTPException(status_code=503, detail=f"Error en API externa: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/forecast/download")
async def download_weather_data(
    day: str,
    lat: float,
    lon: float,
    activity: str,
    format: str = "json"  # json o csv
):
    """
    Descargar datos meteorológicos en formato JSON o CSV.
    Requisito de NASA: metadata con unidades y source links accesibles.
    """
    try:
        place = {"lat": lat, "lon": lon}
        result = get_weather_for(day, place, activity)
        
        if format.lower() == "csv":
            # Convertir a CSV
            csv_data = convert_to_csv(result)
            return StreamingResponse(
                io.StringIO(csv_data),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=weather_{day}_{activity}.csv"}
            )
        else:
            # JSON por defecto
            return JSONResponse(
                content=result,
                headers={"Content-Disposition": f"attachment; filename=weather_{day}_{activity}.json"}
            )
            
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def convert_to_csv(data: dict) -> str:
    """Convierte el resultado a formato CSV"""
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["Metric", "Value", "Unit"])
    
    # Metadata
    writer.writerow(["=== METADATA ===", "", ""])
    writer.writerow(["Source", data['metadata']['source'], ""])
    writer.writerow(["Location Lat", data['metadata']['location']['latitude'], "degrees"])
    writer.writerow(["Location Lon", data['metadata']['location']['longitude'], "degrees"])
    writer.writerow(["Date Range", data['metadata']['date_range'], ""])
    
    # Temperature
    writer.writerow(["=== TEMPERATURE ===", "", ""])
    temp = data['analytics']['temperature']
    writer.writerow(["Avg Min Temp", temp['min']['average'], "°C"])
    writer.writerow(["Avg Max Temp", temp['max']['average'], "°C"])
    
    # Precipitation
    writer.writerow(["=== PRECIPITATION ===", "", ""])
    precip = data['analytics']['precipitation']
    writer.writerow(["Rain Probability", precip['probability_of_rain'], "%"])
    writer.writerow(["Avg When Rained", precip['average_when_rained'], "mm"])
    
    # Wind
    writer.writerow(["=== WIND ===", "", ""])
    wind = data['analytics']['wind']
    writer.writerow(["Avg Wind Speed", wind['average_speed'], "m/s"])
    writer.writerow(["Classification", wind['classification'], ""])
    
    return output.getvalue()
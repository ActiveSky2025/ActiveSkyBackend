from fastapi import APIRouter
import services.weather_services as weather_services


router = APIRouter()

@router.get("/recommendations")
async def get_forecast(date: str, activity: str, coordinates: str):

   weather_data =  weather_services.get_weather_for(date, coordinates, activity)
   
   

   # Regresar weather_data
   return {
        "message": "ENDPOINT DE PRONOSTICO",
        "activity": activity,
        "coordinates": coordinates,
        "date": date,
        "weather": weather_data
    }
#hykmmj     



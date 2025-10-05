import requests


parameters = "T2M_MIN,T2M_MAX,WS2M,IMERG_PRECLIQUID_PROB,CLOUD_AMT,ALLSKY_SFC_UV_INDEX"

url  = "https://power.larc.nasa.gov/api/temporal/daily/point"
payload = {"start" : day, "end": day, "latitude": normalized_place['lat'], "longitude": normalized_place['lon'], "community": "ag", "parameters": parameters, "format": "JSON"}


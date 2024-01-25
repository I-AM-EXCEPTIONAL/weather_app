from django.shortcuts import render
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

def get_weather_data(request):
    OWM_API_KEY = 'your-openweathermap-api-key'
    params = {
        "latitude": 52.52,
        "longitude": 13.41,
        "hourly": "temperature_2m"
    }

    responses = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=params)

    response = responses[0]
    coordinates = f"Coordinates {response.Latitude()}°E {response.Longitude()}°N"
    elevation = f"Elevation {response.Elevation()} m asl"
    timezone = f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}"
    utc_offset = f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s"

    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s"),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ),
        "temperature_2m": hourly_temperature_2m
    }

    hourly_dataframe = pd.DataFrame(data=hourly_data)

    context = {
        'coordinates': coordinates,
        'elevation': elevation,
        'timezone': timezone,
        'utc_offset': utc_offset,
        'hourly_dataframe': hourly_dataframe.to_html(),
    }

    return render(request, 'index.html', context)

from django.urls import path
from . import views

urlpatterns = [
    path('get_weather_data/', views.get_weather_data, name='get_weather_data'),
]



from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path('register', views.register),
    path('login', views.login),
    path('logout', views.logout),
    path('weather', views.weather, name ="weather"),
    path("delete/<str:city_name>", views.delete_city, name = "delete_city")
    
]
from django.urls import path
from YAAS_App.views import *


urlpatterns = [
    path('', index, name="index"),
    path("register", register, name="register")
]


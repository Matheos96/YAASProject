from django.urls import path
from YAAS_App.views import *


urlpatterns = [
    path('', index, name="index"),
    path('search', search, name="search"),
    path("register", register, name="register"),
    path("login", login_user, name="login_user"),
    path("my_account", my_account, name="my_account"),
    path("change_email_address", change_email, name="email_change"),
    path("change_email_address/done", change_email_done, name="email_change_done")
]


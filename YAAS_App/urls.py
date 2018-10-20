from django.urls import path, include
from YAAS_App.views import *
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    path('', index, name="index"),
    path('search', search, name="search"),
    path('admin_panel', admin_panel, name="admin_panel"),
    path("register", register, name="register"),
    path("login", login_user, name="login_user"),
    path("my_account", my_account, name="my_account"),
    path("change_email_address", change_email, name="email_change"),
    path("change_email_address/done", change_email_done, name="email_change_done"),
    path("setlang/<int:lang>", set_language, name="set_language"),
    path("rest/auctions", auction_list, name="auction-list"),
    path('rest/auctions/<int:pk>', auction_detail, name="auction-detail"),
    path('generatedata', generate_data, name="generate_data"),
    path('clear', delete_all)  # DEBUGGOMNG
]

urlpatterns = format_suffix_patterns(urlpatterns)

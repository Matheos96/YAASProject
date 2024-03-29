"""YAAS_Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import *

urlpatterns = [
    path('new', AddAuction.as_view(), name="new_auction"),
    path('confirm', confirm_form, name="confirm_form"),
    path('<int:auction_id>', AuctionView.as_view(), name="auction_view"),
    path('edit/<int:auction_id>', EditAuction.as_view(), name="edit_auction"),
    path('ban/<int:auction_id>', ban_auction, name="ban_auction"),
]

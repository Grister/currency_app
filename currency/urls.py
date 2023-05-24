from django.urls import path
from .views import scrape_privat, privat

urlpatterns = [
    path('privatbank/', privat, name='privat'),
    path('scrape_data/', scrape_privat, name='scrape_privat'),
]

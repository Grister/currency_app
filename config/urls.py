from django.contrib import admin
from django.urls import path, include

from core.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('rates/', include('currency.urls')),
    path('api/', include('api.urls')),
]

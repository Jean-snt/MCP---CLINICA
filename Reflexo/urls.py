from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('clinica.urls')),
    path('', include('clinica.urls')),  # Ruta principal para el dashboard
]
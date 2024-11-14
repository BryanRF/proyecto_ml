from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('clasificador/', views.classify_image, name='classify_image'),
    path('', views.upload_dataset, name='upload_dataset'),
    path('inicio/', views.inicio, name='inicio'),
     path('api/', include('app_ml.urls')),  # Incluir las URLs de la aplicación
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



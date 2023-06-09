from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.redcambnombre.views import Inicio
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Inicio.as_view(), name='inicio'),
    path('', include("apps.redcambnombre.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

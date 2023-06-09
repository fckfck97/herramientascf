# urls.py
from django.urls import path
from .views import CambioNombreImagenesView, ReductorImagenesView

urlpatterns = [
    path('cambioNombre/', CambioNombreImagenesView.as_view(), name='cambioNombre'),
    path('reductorImg/', ReductorImagenesView.as_view(), name='reductorImg')
]
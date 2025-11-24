# app_name/urls.py
from django.urls import path
from .views import ExcelUploadView

urlpatterns = [
    # El punto final que el frontend usará
    path('api/productos/upload/', ExcelUploadView.as_view(), name='producto-upload'),
]
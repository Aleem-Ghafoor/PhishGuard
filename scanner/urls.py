from django.urls import path
from . import views

urlpatterns = [
    path('scan/', views.scan, name='scan'),
    path('scan_api/', views.scan_api, name='scan_api'),
    path('history/api/', views.scan_history_api, name='scan_history_api'),
    path('history/', views.scan_history, name='scan_history'),
]
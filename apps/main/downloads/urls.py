from django.urls import path
from . import views

app_name = 'downloads'

urlpatterns = [
    path('public/downloads/', views.DownloadListView.as_view(), name='download_list'),
    path('public/downloads/download/<int:pk>/', views.download_redirect, name='download_redirect'),
] 
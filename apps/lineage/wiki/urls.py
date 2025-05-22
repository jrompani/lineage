from django.urls import path
from . import views

app_name = 'wiki'

urlpatterns = [
    path('public/wiki/', views.WikiHomeView.as_view(), name='home'),
    path('public/wiki/general/', views.WikiGeneralView.as_view(), name='general'),
    path('public/wiki/rates/', views.WikiRatesView.as_view(), name='rates'),
    path('public/wiki/raids/', views.WikiRaidsView.as_view(), name='raids'),
    path('public/wiki/assistance/', views.WikiAssistanceView.as_view(), name='assistance'),
    path('public/wiki/events/', views.WikiEventsView.as_view(), name='events'),
    path('public/wiki/updates/', views.WikiUpdatesView.as_view(), name='updates'),
    path('public/wiki/features/', views.WikiFeaturesView.as_view(), name='features'),
    path('public/wiki/page/<slug:slug>/', views.WikiPageDetailView.as_view(), name='page'),
    path('public/wiki/section/<int:pk>/', views.WikiSectionDetailView.as_view(), name='section'),
]

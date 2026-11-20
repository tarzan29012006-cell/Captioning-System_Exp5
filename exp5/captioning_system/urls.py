from django.urls import path
from . import views

urlpatterns = [
    # UI Web Pages
    path('', views.index, name='index'),
    path('history/', views.history_view, name='history'),
    path('caption/<int:pk>/', views.detail_view, name='detail'),
    path('caption/<int:pk>/delete/', views.delete_caption, name='delete_caption'),
    path('api-docs/', views.api_docs, name='api_docs'),

    # REST API Endpoints
    path('api/caption/', views.api_caption, name='api_caption'),
    path('api/history/', views.api_history, name='api_history'),
]

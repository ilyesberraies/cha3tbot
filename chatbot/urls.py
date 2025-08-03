from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # Page principale du chat à la racine (/)
    path('', views.chat_view, name='chat'),
    
    # API pour les messages du chatbot
    path('api/chat/', views.chat_api, name='chat_api'),
    
    # Endpoint de test pour Ollama
    path('api/test/', views.test_ollama, name='test_ollama'),
    
    # Routes de debug temporaires
    path('simple/', views.simple_test, name='simple_test'),
    path('api/simple/', views.api_test_simple, name='api_simple_test'),
]
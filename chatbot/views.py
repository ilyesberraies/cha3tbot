from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json
import requests
import logging
import re
from django.http import HttpResponse

# Configuration du logging
logger = logging.getLogger(__name__)

# Configuration Ollama depuis les settings Django
OLLAMA_URL = getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434')
MODEL_NAME = getattr(settings, 'OLLAMA_MODEL', 'mistral')
OLLAMA_TIMEOUT = getattr(settings, 'OLLAMA_TIMEOUT', 30)

def simple_test(request):
    return HttpResponse("✅ Vue simple fonctionne !")

def api_test_simple(request):
    return JsonResponse({"status": "✅ API simple fonctionne"})

def home_view(request):
    return render(request, 'chatbot/home.html')

def chat_view(request):
    """Vue pour afficher la page de chat"""
    return render(request, 'chatbot/chat.html')

@csrf_exempt  # Ajout du décorateur CSRF exempt
@require_http_methods(['POST'])
def chat_api(request):
    """API pour traiter les messages du chatbot"""
    try:
        # Récupérer le message depuis la requête
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()
        
        if not user_message:
            return JsonResponse({"error": "Message requis"}, status=400)
        
        if len(user_message) > 1000:  # Limite la longueur du message
            return JsonResponse({"error": "Message trop long"}, status=400)
        
        logger.info(f"Message reçu: {user_message}")
        
        # Créer un prompt spécialisé pour SKiDL
        prompt = f"""Tu es un assistant spécialisé en conception de circuits électroniques avec SKiDL (Python). 
Réponds de manière claire et concise à la question suivante, et si approprié, génère du code SKiDL.

Question: {user_message}

Si tu génères du code SKiDL, assure-toi qu'il soit syntaxiquement correct et bien commenté."""
        
        # Appel à l'API Ollama
        response = requests.post(
            f'{OLLAMA_URL}/api/generate',
            json={
                'model': MODEL_NAME,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.7,
                    'num_predict': 500
                }
            },
            timeout=OLLAMA_TIMEOUT  # Utilise le timeout des settings Django
        )
        
        # Vérifier la réponse
        if response.status_code != 200:
            logger.error(f"Erreur Ollama: {response.status_code} - {response.text}")
            return JsonResponse({
                'error': f'Erreur Ollama: {response.status_code}'
            }, status=503)
        
        # Traiter la réponse
        ollama_data = response.json()
        bot_response = ollama_data.get('response', 'Pas de réponse')
        
        logger.info(f"Réponse du bot: {bot_response[:100]}...")
        
        # Extraire le code SKiDL si présent
        skidl_code = None
        if '```' in bot_response:
            code_match = re.search(r'```(?:python)?\s*([\s\S]*?)\s*```', bot_response)
            if code_match:
                skidl_code = code_match.group(1).strip()
        
        return JsonResponse({
            'response': bot_response,
            'skidl_code': skidl_code
        })
        
    except requests.exceptions.ConnectionError:
        logger.error("Impossible de se connecter à Ollama")
        return JsonResponse({
            'error': 'Service LLM non disponible. Veuillez réessayer plus tard.'
        }, status=503)
        
    except requests.exceptions.Timeout:
        logger.error("Timeout lors de l'appel à Ollama")
        return JsonResponse({
            'error': 'Le service LLM met trop de temps à répondre. Veuillez réessayer.'
        }, status=504)
        
    except json.JSONDecodeError:
        logger.error("Erreur de décodage JSON")
        return JsonResponse({
            'error': 'Format de message invalide.'
        }, status=400)
        
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}")
        return JsonResponse({
            'error': 'Une erreur interne est survenue. Veuillez réessayer plus tard.'
        }, status=500)

@require_http_methods(['GET'])
def test_ollama(request):
    """Endpoint pour tester la connexion à Ollama"""
    try:
        response = requests.get(f'{OLLAMA_URL}/api/tags', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            has_mistral = any('mistral' in model for model in models)
            
            return JsonResponse({
                'status': 'OK',
                'ollama_connected': True,
                'models': models,
                'mistral_available': has_mistral
            })
        else:
            return JsonResponse({
                'status': 'ERROR',
                'ollama_connected': False,
                'error': f'HTTP {response.status_code}'
            }, status=503)
            
    except requests.exceptions.ConnectionError:
        return JsonResponse({
            'status': 'ERROR',
            'ollama_connected': False,
            'error': 'Ollama non accessible. Exécutez: ollama serve'
        }, status=503)
        
    except Exception as e:
        return JsonResponse({
            'status': 'ERROR',
            'ollama_connected': False,
            'error': str(e)
        }, status=500)

# Exemple d'utilisation du rate limiting avec django-ratelimit
# (après installation: pip install django-ratelimit)
# from ratelimit.decorators import ratelimit
# 
# @ratelimit(key='ip', rate='5/m', block=True)
# @csrf_exempt
# @require_http_methods(['POST'])
# def chat_api(request):
#     # ... reste du code
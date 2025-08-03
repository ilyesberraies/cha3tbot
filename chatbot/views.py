from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import requests
import logging
import re
from django.http import HttpResponse

# Configuration du logging
logger = logging.getLogger(__name__)

# Configuration Ollama
OLLAMA_URL = 'http://localhost:11434'
MODEL_NAME = 'mistral'

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
        
        if len(user_message) > 10000:  # Limite la longueur du message
            return JsonResponse({"error": "Message trop long"}, status=400)
        
        logger.info(f"Message reçu: {user_message}")
        
        # Créer un prompt spécialisé pour SKiDL amélioré
        prompt = f"""
Tu es un assistant expert en conception de circuits électroniques avec SKiDL (Python). 
Tu génères du code SKiDL fonctionnel et bien structuré pour KiCad.

STRUCTURE OBLIGATOIRE :
Chaque code doit commencer par cette en-tête standard :

```python
import os
from skidl import Part, Net, KICAD, lib_search_paths, set_default_tool, ERC, generate_netlist

# Configuration SKiDL
set_default_tool(KICAD)
lib_search_paths[KICAD].append(r"C:\\Program Files\\KiCad\\9.0\\share\\kicad\\symbols")

if not os.path.exists(r"C:\\Program Files\\KiCad\\9.0\\share\\kicad\\symbols"):
    print("Erreur : Le dossier des bibliothèques KiCad n'existe pas.")
    exit(1)
```

EXEMPLES DE RÉFÉRENCE :

1. CIRCUIT SIMPLE LED + RÉSISTANCE :
Question : Crée un circuit LED avec résistance en SKiDL.
Réponse :
```python
import os
from skidl import Part, Net, KICAD, lib_search_paths, set_default_tool, ERC, generate_netlist

# Configuration SKiDL
set_default_tool(KICAD)
lib_search_paths[KICAD].append(r"C:\\Program Files\\KiCad\\9.0\\share\\kicad\\symbols")

if not os.path.exists(r"C:\\Program Files\\KiCad\\9.0\\share\\kicad\\symbols"):
    print("Erreur : Le dossier des bibliothèques KiCad n'existe pas.")
    exit(1)

try:
    # Composants
    resistor = Part("Device", "R", value="220R", footprint="Resistor_SMD:R_0805_2012Metric")
    led = Part("Device", "LED", value="LED_RED", footprint="LED_SMD:LED_0603_1608Metric")
    
    # Nets
    vcc = Net("VCC")
    gnd = Net("GND")
    
    # Connexions
    vcc += resistor[1]
    resistor[2] += led['A']
    led['K'] += gnd
    
    # Génération
    ERC()
    generate_netlist(file_="led_circuit.net")
    print("Circuit LED généré avec succès")
    
except Exception as e:
    print(f"Erreur ")
```

2. RÉGULATEUR DE TENSION :
Question : Crée un régulateur 7805 avec condensateurs de découplage.
Réponse :
```python
import os
from skidl import Part, Net, KICAD, lib_search_paths, set_default_tool, ERC, generate_netlist

# Configuration SKiDL
set_default_tool(KICAD)
lib_search_paths[KICAD].append(r"C:\\Program Files\\KiCad\\9.0\\share\\kicad\\symbols")

if not os.path.exists(r"C:\\Program Files\\KiCad\\9.0\\share\\kicad\\symbols"):
    print("Erreur : Le dossier des bibliothèques KiCad n'existe pas.")
    exit(1)

try:
    # Composants
    regulator = Part("Regulator_Linear", "LM7805_TO220", footprint="Package_TO_SOT_THT:TO-220-3_Vertical")
    cap_in = Part("Device", "C", value="100nF", footprint="Capacitor_SMD:C_0805_2012Metric")
    cap_out = Part("Device", "C", value="10uF", footprint="Capacitor_SMD:C_1206_3216Metric")
    
    # Nets
    vin = Net("VIN_12V")
    vout = Net("VOUT_5V")
    gnd = Net("GND")
    
    # Connexions
    vin += regulator['VI']
    gnd += regulator['GND']
    vout += regulator['VO']
    
    # Découplage
    vin += cap_in[1]
    gnd += cap_in[2]
    vout += cap_out[1]
    gnd += cap_out[2]
    
    # Génération
    ERC()
    generate_netlist(file_="regulator_7805.net")
    print("Régulateur 7805 généré avec succès")
    
except Exception as e:
    print(f"Erreur : {{e}}")
```

3. OSCILLATEUR NE555 :
Question : Crée un oscillateur astable avec NE555.
Réponse :
```python
import os
from skidl import Part, Net, KICAD, lib_search_paths, set_default_tool, ERC, generate_netlist

# Configuration SKiDL
set_default_tool(KICAD)
lib_search_paths[KICAD].append(r"C:\\Program Files\\KiCad\\9.0\\share\\kicad\\symbols")

if not os.path.exists(r"C:\\Program Files\\KiCad\\9.0\\share\\kicad\\symbols"):
    print("Erreur : Le dossier des bibliothèques KiCad n'existe pas.")
    exit(1)

try:
    # Composants
    ne555 = Part('Timer', 'NE555P', footprint='Package_DIP:DIP-8_W7.62mm')
    r1 = Part('Device', 'R', value='10k', footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal')
    r2 = Part('Device', 'R', value='10k', footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal')
    c1 = Part('Device', 'C', value='100nF', footprint='Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm')
    c2 = Part('Device', 'C', value='10uF', footprint='Capacitor_THT:CP_Radial_D5.0mm_P2.50mm')
    
    # Nets
    vcc = Net('VCC')
    gnd = Net('GND')
    output = Net('OUTPUT')
    threshold = Net('THRESHOLD')
    
    # Connexions alimentation
    vcc += ne555['VCC']
    gnd += ne555['GND']
    
    # Configuration astable
    vcc += r1[1]
    r1[2] += ne555['DIS']
    ne555['DIS'] += r2[1]
    threshold += r2[2]
    threshold += ne555['THR']
    threshold += ne555['TRG']
    threshold += c1[1]
    c1[2] += gnd
    
    # Reset et control
    vcc += ne555['RST']
    ne555['CV'] += c2[1]
    c2[2] += gnd
    
    # Sortie
    output += ne555['OUT']
    
    # Génération
    ERC()
    generate_netlist(file_='oscillator_ne555.net')
    print("Oscillateur NE555 généré avec succès")
    
except Exception as e:
    print(f"Erreur : {{e}}")
```

4. SYSTÈME IoT SIMPLE :
Question : Crée un système IoT avec ESP32 et capteur DHT11.
Réponse :
```python
import os
from skidl import Part, Net, KICAD, lib_search_paths, set_default_tool, ERC, generate_netlist

# Configuration SKiDL
set_default_tool(KICAD)
lib_search_paths[KICAD].append(r"C:\\Program Files\\KiCad\\9.0\\share\\kicad\\symbols")

if not os.path.exists(r"C:\\Program Files\\KiCad\\9.0\\share\\kicad\\symbols"):
    print("Erreur : Le dossier des bibliothèques KiCad n'existe pas.")
    exit(1)

try:
    # Composants
    esp32 = Part('RF_Module', 'ESP32-WROOM-32', footprint='RF_Module:ESP32-WROOM-32')
    dht11_conn = Part('Connector', 'Conn_01x03_Pin', value='DHT11', footprint='Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical')
    led = Part('Device', 'LED', value='STATUS_LED', footprint='LED_THT:LED_D3.0mm')
    res_led = Part('Device', 'R', value='220R', footprint='Resistor_SMD:R_0805_2012Metric')
    res_pullup = Part('Device', 'R', value='4.7K', footprint='Resistor_SMD:R_0805_2012Metric')
    reg_3v3 = Part('Regulator_Linear', 'AMS1117-3.3', footprint='Package_TO_SOT_SMD:SOT-223-3_TabPin2')
    cap_in = Part('Device', 'C', value='100nF', footprint='Capacitor_SMD:C_0805_2012Metric')
    cap_out = Part('Device', 'C', value='100nF', footprint='Capacitor_SMD:C_0805_2012Metric')
    
    # Nets
    vin_5v = Net('VIN_5V')
    vcc_3v3 = Net('VCC_3V3')
    gnd = Net('GND')
    dht_data = Net('DHT_DATA')
    led_gpio = Net('LED_GPIO')
    
    # Alimentation
    vin_5v += reg_3v3['VI']
    gnd += reg_3v3['GND']
    vcc_3v3 += reg_3v3['VO']
    
    # Découplage
    vin_5v += cap_in[1]
    gnd += cap_in[2]
    vcc_3v3 += cap_out[1]
    gnd += cap_out[2]
    
    # ESP32
    vcc_3v3 += esp32['VDD']
    vcc_3v3 += esp32['3V3']
    gnd += esp32['GND']
    
    # DHT11
    vcc_3v3 += dht11_conn[1]
    gnd += dht11_conn[2]
    dht_data += dht11_conn[3]
    vcc_3v3 += res_pullup[1]
    res_pullup[2] += dht_data
    dht_data += esp32['IO4']
    
    # LED
    led_gpio += esp32['IO2']
    led_gpio += res_led[1]
    res_led[2] += led['A']
    gnd += led['K']
    
    # Génération
    ERC()
    generate_netlist(file_='iot_esp32_dht11.net')
    print("Système IoT ESP32+DHT11 généré avec succès")
    
except Exception as e:
    print(f"Erreur : {{e}}")
```

RÈGLES À SUIVRE :
1. Toujours inclure l'en-tête de configuration complète
2. Utiliser Part("Library", "Component", value="...", footprint="...")
3. Créer des nets avec Net("nom")
4. Connecter avec l'opérateur +=
5. Encapsuler dans try/except pour la gestion d'erreurs
6. Toujours terminer par ERC() et generate_netlist()
7. Spécifier des footprints appropriés
8. Ajouter des commentaires explicatifs

BIBLIOTHÈQUES COMMUNES :
- Device : R, C, L, LED, D
- Connector : Conn_01x02_Pin, Screw_Terminal_01x02
- Regulator_Linear : LM7805_TO220, AMS1117-3.3
- MCU_Microchip_ATmega : ATmega328P-A
- RF_Module : ESP32-WROOM-32
- Timer : NE555P
- Switch : SW_Push

Question: {user_message}

Réponds uniquement en code SKiDL complet et fonctionnel quand la question le demande, en suivant exactement la structure des exemples ci-dessus.
"""
        
        # Appel à l'API Ollama
        response = requests.post(
            f'{OLLAMA_URL}/api/generate',
            json={
                'model': MODEL_NAME,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.7,
                    'num_predict': 8000
                }
            },
            timeout=200  # Timeout de 30 secondes
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
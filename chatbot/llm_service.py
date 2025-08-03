# chatbot/llm_service.py

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

OLLAMA_URL = 'http://<adresse_ip_ollama>:11434'

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data['message']
        
        response = requests.post(f'{OLLAMA_URL}/api/generate', 
            json={
                'model': 'mistral',
                'prompt': message,
                'stream': False
            }
        )
        
        if response.status_code == 200:
            return jsonify({
                'response': response.json()['response']
            })
        else:
            return jsonify({'error': 'Erreur Ollama'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)



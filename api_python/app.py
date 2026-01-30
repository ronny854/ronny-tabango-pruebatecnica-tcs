from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import uuid
import jwt
import datetime
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for web interface

# Load configuration from environment variables
SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key-only-for-dev')
REQUIRED_API_KEY = os.getenv('API_KEY', '')
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 1))

# Validate critical configuration
if not REQUIRED_API_KEY:
    logger.error("API_KEY not configured in .env file")
    raise ValueError("API_KEY must be set in environment variables")


def validate_api_key():
    """Validate the API Key from headers"""
    api_key = request.headers.get('X-Parse-REST-API-Key')
    is_valid = api_key == REQUIRED_API_KEY

    if not is_valid:
        logger.warning(f"Invalid API key attempt from {request.remote_addr}")

    return is_valid


def generate_jwt():
    """Generate a unique JWT token for each transaction"""
    payload = {
        'transaction_id': str(uuid.uuid4()),
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    logger.info(f"Generated JWT for transaction: {payload['transaction_id']}")
    return token


@app.route('/DevOps', methods=['POST', 'GET', 'PUT', 'DELETE', 'PATCH'])
def devops_endpoint():
    """
    DevOps endpoint that handles POST requests with API Key validation
    Returns ERROR for any other HTTP method
    """
    # Check if method is POST
    if request.method != 'POST':
        logger.warning(f"Invalid method {request.method} attempted on /DevOps from {request.remote_addr}")
        return "ERROR", 405

    # Validate API Key
    if not validate_api_key():
        return jsonify({"error": "Unauthorized - Invalid API Key"}), 401

    # Get JWT from headers (optional validation)
    jwt_token = request.headers.get('X-JWT-KWY')

    try:
        # Parse JSON payload
        data = request.get_json()

        if not data:
            logger.error("Empty or invalid JSON payload received")
            return jsonify({"error": "Invalid JSON payload"}), 400

        # Extract the "to" field from payload
        to_recipient = data.get('to', '')

        logger.info(f"Processing request for recipient: {to_recipient}")

        # Generate unique JWT for this transaction
        unique_jwt = generate_jwt()

        # Return the required response
        response = {
            "message": f"Hello {to_recipient} your message will be send"
        }

        # Add JWT to response headers
        response_obj = jsonify(response)
        response_obj.headers['X-JWT-KWY'] = unique_jwt

        logger.info(f"Successfully processed request for {to_recipient}")
        return response_obj, 200

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 400


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "service": "DevOps Microservice"
    }), 200


# HTML Template for the web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevOps Microservice - Testing Interface</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }

        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }

        .test-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }

        .test-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 25px;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        .test-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }

        .test-button:active {
            transform: translateY(0);
        }

        .test-button:disabled {
            background: #ccc;
            cursor: not-allowed;
            box-shadow: none;
        }

        .form-group {
            margin-bottom: 15px;
        }

        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: 600;
        }

        .form-group input,
        .form-group textarea {
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 1em;
            transition: border-color 0.3s ease;
        }

        .form-group input:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        .response-container {
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            display: none;
        }

        .response-container.success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }

        .response-container.error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }

        .response-container.info {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
        }

        .response-title {
            font-weight: bold;
            margin-bottom: 10px;
            font-size: 1.1em;
        }

        .response-content {
            background: white;
            padding: 15px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            word-break: break-all;
            max-height: 400px;
            overflow-y: auto;
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .config-info {
            background: #fff3cd;
            border: 1px solid #ffeeba;
            color: #856404;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .config-info strong {
            display: block;
            margin-bottom: 5px;
        }

        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
            margin-left: 10px;
        }

        .badge.success {
            background: #28a745;
            color: white;
        }

        .badge.error {
            background: #dc3545;
            color: white;
        }

        .badge.warning {
            background: #ffc107;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 DevOps Microservice</h1>
            <p>Interfaz de Pruebas - Testing Interface</p>
        </div>

        <div class="card">
            <h2>⚙️ Configuración / Configuration</h2>
            <div class="form-group">
                <label for="apiKey">API Key (X-Parse-REST-API-Key):</label>
                <input type="text" id="apiKey" placeholder="Ingrese su API Key">
            </div>
            <div class="form-group">
                <label for="recipient">Destinatario / Recipient (to):</label>
                <input type="text" id="recipient" value="Juan Perez" placeholder="Nombre del destinatario">
            </div>
        </div>

        <div class="card">
            <h2>🧪 Pruebas Automatizadas / Automated Tests</h2>
            <div class="test-grid">
                <button class="test-button" onclick="runTest('valid_post')">
                    ✅ POST Válido con API Key
                </button>
                <button class="test-button" onclick="runTest('invalid_api_key')">
                    ❌ POST sin API Key válida
                </button>
                <button class="test-button" onclick="runTest('get_method')">
                    🔴 GET Method (debe fallar)
                </button>
                <button class="test-button" onclick="runTest('put_method')">
                    🔴 PUT Method (debe fallar)
                </button>
                <button class="test-button" onclick="runTest('delete_method')">
                    🔴 DELETE Method (debe fallar)
                </button>
                <button class="test-button" onclick="runTest('patch_method')">
                    🔴 PATCH Method (debe fallar)
                </button>
                <button class="test-button" onclick="runTest('invalid_json')">
                    ⚠️ POST con JSON inválido
                </button>
                <button class="test-button" onclick="runTest('health_check')">
                    💚 Health Check
                </button>
                <button class="test-button" onclick="runAllTests()" style="grid-column: 1 / -1; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                    🚀 Ejecutar Todas las Pruebas
                </button>
            </div>
        </div>

        <div class="card">
            <h2>📊 Resultados / Results</h2>
            <div id="responseContainer" class="response-container">
                <div class="response-title" id="responseTitle"></div>
                <div class="response-content" id="responseContent"></div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE_URL = window.location.origin;

        function showResponse(title, content, type = 'info') {
            const container = document.getElementById('responseContainer');
            const titleEl = document.getElementById('responseTitle');
            const contentEl = document.getElementById('responseContent');

            container.className = 'response-container ' + type;
            container.style.display = 'block';
            titleEl.textContent = title;
            contentEl.textContent = typeof content === 'object' ? JSON.stringify(content, null, 2) : content;
        }

        async function runTest(testType) {
            const apiKey = document.getElementById('apiKey').value;
            const recipient = document.getElementById('recipient').value;

            const tests = {
                valid_post: async () => {
                    const response = await fetch(`${API_BASE_URL}/DevOps`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Parse-REST-API-Key': apiKey
                        },
                        body: JSON.stringify({ to: recipient })
                    });
                    const data = await response.json();
                    const jwt = response.headers.get('X-JWT-KWY');

                    showResponse(
                        '✅ POST Válido - Status: ' + response.status,
                        {
                            status: response.status,
                            response: data,
                            jwt_token: jwt
                        },
                        response.ok ? 'success' : 'error'
                    );
                },
                invalid_api_key: async () => {
                    const response = await fetch(`${API_BASE_URL}/DevOps`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Parse-REST-API-Key': 'invalid-key'
                        },
                        body: JSON.stringify({ to: recipient })
                    });
                    const data = await response.json();

                    showResponse(
                        '❌ POST sin API Key válida - Status: ' + response.status,
                        {
                            status: response.status,
                            response: data
                        },
                        response.status === 401 ? 'success' : 'error'
                    );
                },
                get_method: async () => {
                    const response = await fetch(`${API_BASE_URL}/DevOps`, {
                        method: 'GET',
                        headers: {
                            'X-Parse-REST-API-Key': apiKey
                        }
                    });
                    const text = await response.text();

                    showResponse(
                        '🔴 GET Method - Status: ' + response.status,
                        {
                            status: response.status,
                            response: text,
                            expected: 'ERROR (405)'
                        },
                        response.status === 405 ? 'success' : 'error'
                    );
                },
                put_method: async () => {
                    const response = await fetch(`${API_BASE_URL}/DevOps`, {
                        method: 'PUT',
                        headers: {
                            'X-Parse-REST-API-Key': apiKey
                        }
                    });
                    const text = await response.text();

                    showResponse(
                        '🔴 PUT Method - Status: ' + response.status,
                        {
                            status: response.status,
                            response: text,
                            expected: 'ERROR (405)'
                        },
                        response.status === 405 ? 'success' : 'error'
                    );
                },
                delete_method: async () => {
                    const response = await fetch(`${API_BASE_URL}/DevOps`, {
                        method: 'DELETE',
                        headers: {
                            'X-Parse-REST-API-Key': apiKey
                        }
                    });
                    const text = await response.text();

                    showResponse(
                        '🔴 DELETE Method - Status: ' + response.status,
                        {
                            status: response.status,
                            response: text,
                            expected: 'ERROR (405)'
                        },
                        response.status === 405 ? 'success' : 'error'
                    );
                },
                patch_method: async () => {
                    const response = await fetch(`${API_BASE_URL}/DevOps`, {
                        method: 'PATCH',
                        headers: {
                            'X-Parse-REST-API-Key': apiKey
                        }
                    });
                    const text = await response.text();

                    showResponse(
                        '🔴 PATCH Method - Status: ' + response.status,
                        {
                            status: response.status,
                            response: text,
                            expected: 'ERROR (405)'
                        },
                        response.status === 405 ? 'success' : 'error'
                    );
                },
                invalid_json: async () => {
                    const response = await fetch(`${API_BASE_URL}/DevOps`, {
                        method: 'POST',
                        headers: {
                            'X-Parse-REST-API-Key': apiKey
                        }
                    });
                    const data = await response.json();

                    showResponse(
                        '⚠️ POST con JSON inválido - Status: ' + response.status,
                        {
                            status: response.status,
                            response: data
                        },
                        response.status === 400 ? 'success' : 'error'
                    );
                },
                health_check: async () => {
                    const response = await fetch(`${API_BASE_URL}/health`);
                    const data = await response.json();

                    showResponse(
                        '💚 Health Check - Status: ' + response.status,
                        {
                            status: response.status,
                            response: data
                        },
                        response.ok ? 'success' : 'error'
                    );
                }
            };

            try {
                showResponse('⏳ Ejecutando prueba...', 'Por favor espere...', 'info');
                await tests[testType]();
            } catch (error) {
                showResponse('❌ Error', error.message, 'error');
            }
        }

        async function runAllTests() {
            const testTypes = [
                'health_check',
                'valid_post',
                'invalid_api_key',
                'get_method',
                'put_method',
                'delete_method',
                'patch_method',
                'invalid_json'
            ];

            let results = [];

            showResponse('⏳ Ejecutando todas las pruebas...', 'Por favor espere...', 'info');

            for (const testType of testTypes) {
                try {
                    await runTest(testType);
                    await new Promise(resolve => setTimeout(resolve, 500));
                } catch (error) {
                    results.push({test: testType, error: error.message});
                }
            }

            showResponse(
                '✅ Todas las pruebas completadas',
                'Revise los resultados anteriores. Última prueba: ' + testTypes[testTypes.length - 1],
                'success'
            );
        }
    </script>
</body>
</html>
'''


@app.route('/', methods=['GET'])
def index():
    """Serve the web interface for testing"""
    return render_template_string(HTML_TEMPLATE)


if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    logger.info(f"Starting DevOps Microservice on {host}:{port}")
    logger.info(f"Debug mode: {debug}")

    app.run(host=host, port=port, debug=debug)

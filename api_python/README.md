# DevOps Microservice - Producción

Microservicio Flask con interfaz gráfica para pruebas y validación de API.

## Características

- Endpoint `/DevOps` con validación de API Key
- Generación de JWT tokens para cada transacción
- Interfaz web gráfica para ejecutar todas las pruebas
- Configuración mediante variables de entorno (.env)
- Logging completo de operaciones
- Health check endpoint
- CORS habilitado
- Listo para producción

## Instalación

1. Crear un entorno virtual:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar .env:
```bash
cp .env.example .env
# Editar .env con tus valores
```

## Uso

1. Ejecutar la aplicación:
```bash
python app.py
```

2. Abrir navegador en `http://localhost:5000`

3. Usar la interfaz web para ejecutar pruebas

## API Key

Por defecto: `2f5ae96c-b558-4c7b-a590-a501ae1c3f6c`

Configurable en archivo .env

## Docker (Recomendado)

### Opción 1: Docker Compose (Más Fácil)
```bash
# Iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

### Opción 2: Docker Manual
```bash
# Construir imagen
docker build -t devops-microservice .

# Ejecutar contenedor
docker run -d -p 5000:5000 --env-file .env --name devops-microservice devops-microservice
```

Ver [DOCKER.md](DOCKER.md) para más detalles.

## Endpoints

- `POST /DevOps` - Endpoint principal (requiere API Key)
- `GET /health` - Health check
- `GET /` - Interfaz web de pruebas

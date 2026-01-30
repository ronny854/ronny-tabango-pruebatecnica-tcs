# Guía de Despliegue con Docker

## Construcción de la Imagen

### Opción 1: Docker Build Simple
```bash
docker build -t devops-microservice:latest .
```

### Opción 2: Multi-platform Build
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t devops-microservice:latest .
```

## Ejecución del Contenedor

### Opción 1: Con archivo .env (Recomendado)
```bash
docker run -d \
  --name devops-microservice \
  -p 5000:5000 \
  --env-file .env \
  devops-microservice:latest
```

### Opción 2: Con variables de entorno en línea
```bash
docker run -d \
  --name devops-microservice \
  -p 5000:5000 \
  -e SECRET_KEY="your-secret-key-here" \
  -e API_KEY="2f5ae96c-b558-4c7b-a590-a501ae1c3f6c" \
  -e FLASK_ENV=production \
  -e FLASK_DEBUG=False \
  -e HOST=0.0.0.0 \
  -e PORT=5000 \
  -e JWT_EXPIRATION_HOURS=1 \
  devops-microservice:latest
```

### Opción 3: Modo interactivo (para debugging)
```bash
docker run -it --rm \
  --name devops-microservice \
  -p 5000:5000 \
  --env-file .env \
  devops-microservice:latest
```

## Docker Compose (Recomendado para Producción)

### Iniciar servicios
```bash
docker-compose up -d
```

### Ver logs
```bash
docker-compose logs -f
```

### Detener servicios
```bash
docker-compose down
```

### Reconstruir y reiniciar
```bash
docker-compose up -d --build
```

## Verificación

### Health Check
```bash
docker ps  # Verificar que el contenedor esté "healthy"
```

### Ver logs del contenedor
```bash
docker logs -f devops-microservice
```

### Probar el endpoint
```bash
curl http://localhost:5000/health
```

### Acceder a la interfaz web
Abrir en el navegador: http://localhost:5000

## Comandos Útiles

### Ejecutar shell dentro del contenedor
```bash
docker exec -it devops-microservice /bin/bash
```

### Ver estadísticas del contenedor
```bash
docker stats devops-microservice
```

### Inspeccionar el contenedor
```bash
docker inspect devops-microservice
```

### Eliminar el contenedor
```bash
docker stop devops-microservice
docker rm devops-microservice
```

### Eliminar la imagen
```bash
docker rmi devops-microservice:latest
```

## Características de Producción

### Seguridad
- Usuario no-root (appuser) ejecuta la aplicación
- Variables sensibles mediante .env
- Health check integrado
- Logging estructurado

### Performance
- Gunicorn con 4 workers
- Timeout de 120 segundos
- Logs rotativos (max 10MB, 3 archivos)

### Monitoreo
- Health check cada 30 segundos
- Logs accesibles vía docker logs
- Reinicio automático con docker-compose

## Troubleshooting

### El contenedor no inicia
```bash
docker logs devops-microservice
```

### Health check falla
```bash
docker exec devops-microservice curl http://localhost:5000/health
```

### Variables de entorno no se cargan
```bash
docker exec devops-microservice env | grep -E 'API_KEY|SECRET_KEY'
```

### Puerto 5000 ya está en uso
```bash
# Cambiar el puerto en docker-compose.yml o usar:
docker run -p 8080:5000 --env-file .env devops-microservice
```

## Despliegue en la Nube

### AWS ECS
```bash
# Push a ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
docker tag devops-microservice:latest ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/devops-microservice:latest
docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/devops-microservice:latest
```

### Google Cloud Run
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/devops-microservice
gcloud run deploy --image gcr.io/PROJECT-ID/devops-microservice --platform managed
```

### Azure Container Instances
```bash
az acr build --registry myregistry --image devops-microservice:latest .
az container create --resource-group myResourceGroup --name devops-microservice --image myregistry.azurecr.io/devops-microservice:latest --dns-name-label devops-microservice --ports 5000
```

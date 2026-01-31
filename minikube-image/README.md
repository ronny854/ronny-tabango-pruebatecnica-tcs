# Laboratorio Minikube + Azure DevOps Agent

Entorno de desarrollo con Kubernetes (Minikube) y Azure DevOps Agent comunicados mediante SSH con autenticación por llaves.

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Network                           │
│                         (k8s-network)                           │
│                                                                 │
│  ┌─────────────────────┐         ┌─────────────────────────┐   │
│  │   minikube-server   │   SSH   │      azure-agent        │   │
│  │                     │◄────────│                         │   │
│  │  - Minikube         │  keys   │  - Azure DevOps Agent   │   │
│  │  - Docker-in-Docker │         │  - kubectl              │   │
│  │  - SSH Server       │         │  - SSH Client           │   │
│  │  - Dashboard        │         │                         │   │
│  └─────────────────────┘         └─────────────────────────┘   │
│                                                                 │
│  Volumen compartido: ssh-keys (para autenticación SSH)          │
└─────────────────────────────────────────────────────────────────┘
```

## Estructura del Proyecto

```
minikube-image/
├── docker-compose.yml      # Orquestación de contenedores
├── .env                    # Variables de entorno (credenciales)
├── .env.example            # Plantilla de variables
├── .gitignore              # Archivos ignorados por git
├── README.md               # Este archivo
├── minikube-server/        # Contenedor con Minikube
│   ├── Dockerfile
│   └── entrypoint.sh
└── azure-agent/            # Contenedor con Azure Agent
    ├── Dockerfile
    └── entrypoint.sh
```

## Requisitos Previos

- Docker Desktop instalado y corriendo
- Docker Compose v2+
- Mínimo 4GB de RAM disponible para Docker
- (Opcional) Cuenta de Azure DevOps con un Agent Pool configurado

## Configuración Inicial

### 1. Configurar Variables de Entorno

Edita el archivo `.env` con tus credenciales de Azure DevOps:

```bash
# Azure DevOps Agent Configuration
AZP_URL=https://dev.azure.com/tu-organizacion
AZP_TOKEN=tu-personal-access-token
AZP_POOL=Default
AZP_AGENT_NAME=azure-agent-docker
```

**Nota:** Si no configuras las credenciales, el azure-agent se ejecutará en modo standalone sin registrarse en Azure DevOps.

### 2. Construir las Imágenes

```bash
docker-compose build --no-cache
```

### 3. Iniciar el Laboratorio

```bash
docker-compose up -d
```

### 4. Ver Logs de Inicialización

```bash
# Ver logs de ambos servicios
docker-compose logs -f

# Ver logs solo de minikube
docker-compose logs -f minikube-server

# Ver logs solo del agent
docker-compose logs -f azure-agent
```

## Acceso a los Contenedores

### Acceder al contenedor Minikube

```bash
docker exec -it minikube-server bash
```

### Acceder al contenedor Azure Agent

```bash
docker exec -it azure-agent bash
```

## Comandos de Kubernetes

### Desde el host (usando docker exec)

```bash
# Ver nodos del cluster
docker exec minikube-server kubectl get nodes

# Ver todos los pods
docker exec minikube-server kubectl get pods -A

# Ver servicios
docker exec minikube-server kubectl get svc -A

# Estado de minikube
docker exec minikube-server minikube status
```

### Desde azure-agent (via SSH)

```bash
# Ejecutar kubectl remotamente
docker exec azure-agent ssh minikube-server "kubectl get nodes"

# Ver pods
docker exec azure-agent ssh minikube-server "kubectl get pods -A"

# Ejecutar kubectl directamente (usa kubeconfig copiado)
docker exec azure-agent kubectl get nodes
```

## Probar Conexión SSH

### Verificar que las SSH keys fueron generadas

```bash
# Ver clave pública generada
docker exec azure-agent cat /ssh-keys/id_rsa.pub

# Verificar authorized_keys en minikube-server
docker exec minikube-server cat /root/.ssh/authorized_keys
```

### Probar conexión SSH desde azure-agent

```bash
# Conexión simple
docker exec azure-agent ssh minikube-server "echo 'SSH funciona correctamente'"

# Verificar hostname y estado de minikube
docker exec azure-agent ssh minikube-server "hostname && minikube status"

# Sesión SSH interactiva
docker exec -it azure-agent ssh minikube-server
```

### Conexión SSH desde tu máquina local

```bash
# El puerto 22 está mapeado al 2222
# Nota: Requiere la clave privada del volumen
ssh -p 2222 -i <path-to-private-key> root@localhost
```

## Acceso al Dashboard de Kubernetes

Una vez que minikube esté corriendo, el dashboard estará disponible en:

```
http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/http:kubernetes-dashboard:/proxy/
```

## Puertos Expuestos

| Puerto | Servicio | Descripción |
|--------|----------|-------------|
| 2222 | SSH | Acceso SSH al minikube-server |
| 8001 | Dashboard | Kubernetes Dashboard (kubectl proxy) |
| 8443 | API Server | Kubernetes API Server |
| 30000-30100 | NodePort | Rango para servicios NodePort |

## Comandos Útiles

### Gestión del Laboratorio

```bash
# Iniciar
docker-compose up -d

# Detener
docker-compose down

# Detener y eliminar volúmenes (reset completo)
docker-compose down -v

# Reiniciar un servicio específico
docker-compose restart minikube-server

# Ver estado de los contenedores
docker-compose ps
```

### Debugging

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs del proxy de kubectl
docker exec minikube-server cat /var/log/kubectl-proxy.log

# Ver logs de Docker daemon
docker exec minikube-server cat /var/log/dockerd.log

# Verificar estado de SSH
docker exec minikube-server service ssh status
```

### Desplegar una Aplicación de Prueba

```bash
# Crear un deployment de nginx
docker exec minikube-server kubectl create deployment nginx --image=nginx

# Esperar a que el pod esté listo
docker exec minikube-server kubectl wait --for=condition=ready pod -l app=nginx --timeout=60s

# Exponer el deployment con un NodePort específico (en el rango 30000-30100)
docker exec minikube-server kubectl expose deployment nginx --port=80 --type=NodePort --name=nginx-external

# Parchear el servicio para usar un puerto fijo accesible desde el host
docker exec minikube-server kubectl patch svc nginx-external -p '{"spec":{"ports":[{"port":80,"nodePort":30080}]}}'

# Ver el servicio creado
docker exec minikube-server kubectl get svc nginx-external
```

### Acceder a la Aplicación desde tu Máquina Local

```bash
# Obtener la IP del nodo minikube
docker exec minikube-server minikube ip

# La aplicación estará disponible en:
# http://localhost:30080

# Verificar con curl desde el host
curl http://localhost:30080

# O abrir en el navegador
start http://localhost:30080      # Windows
open http://localhost:30080       # macOS
xdg-open http://localhost:30080   # Linux
```

### Comando Rápido: Desplegar y Obtener URL

```bash
# Script completo para desplegar y exponer el servicio
docker exec minikube-server bash -c '
  kubectl create deployment nginx --image=nginx 2>/dev/null || true
  kubectl wait --for=condition=ready pod -l app=nginx --timeout=60s
  kubectl expose deployment nginx --port=80 --type=ClusterIP --name=nginx-svc 2>/dev/null || true
  echo ""
  echo "Deployment nginx creado correctamente"
'

# Crear port-forward para acceder desde localhost (ejecutar en segundo plano)
docker exec -d minikube-server kubectl port-forward --address 0.0.0.0 svc/nginx-svc 30080:80

# Esperar a que el port-forward esté listo
sleep 2

echo "=========================================="
echo "  APP DISPONIBLE EN: http://localhost:30080"
echo "=========================================="
```

**Nota:** El port-forward es necesario porque Minikube corre en Docker-in-Docker y los NodePorts no son accesibles directamente desde el host.

### Eliminar la Aplicación de Prueba

```bash
docker exec minikube-server kubectl delete deployment nginx
docker exec minikube-server kubectl delete svc nginx-external nginx-nodeport 2>/dev/null
```

## Solución de Problemas

### El contenedor minikube-server no inicia

```bash
# Verificar logs de Docker daemon
docker-compose logs minikube-server | grep -i error

# Verificar que Docker Desktop tiene suficiente memoria
# Recomendado: mínimo 4GB
```

### SSH no conecta

```bash
# Verificar que el servicio SSH está corriendo
docker exec minikube-server service ssh status

# Verificar que las keys existen
docker exec azure-agent ls -la /ssh-keys/

# Regenerar keys (reiniciar con volúmenes limpios)
docker-compose down -v
docker-compose up -d
```

### Dashboard no carga

```bash
# Verificar que el proxy está corriendo
docker exec minikube-server ps aux | grep "kubectl proxy"

# Reiniciar el proxy manualmente
docker exec minikube-server kubectl proxy --address='0.0.0.0' --port=8001 --accept-hosts='.*' &

# Verificar pods del dashboard
docker exec minikube-server kubectl get pods -n kubernetes-dashboard
```

### Azure Agent no se registra

```bash
# Verificar variables de entorno
docker exec azure-agent env | grep AZP

# Verificar logs del agent
docker-compose logs azure-agent

# Verificar conectividad con Azure DevOps
docker exec azure-agent curl -s https://dev.azure.com
```

## Limpiar Todo

```bash
# Detener y eliminar contenedores, redes y volúmenes
docker-compose down -v

# Eliminar imágenes construidas
docker rmi minikube-image-minikube-server minikube-image-azure-agent

# Limpiar todo Docker (cuidado: elimina TODO)
docker system prune -a --volumes
```

# DevOps Microservice - Prueba Tecnica TCS

## Tabla de Contenidos

1. [Descripcion del Proyecto](#descripcion-del-proyecto)
2. [Arquitectura General](#arquitectura-general)
3. [Estructura de Carpetas](#estructura-de-carpetas)
4. [Microservicio Python (Flask)](#microservicio-python-flask)
5. [Pipeline CI/CD en Azure DevOps](#pipeline-cicd-en-azure-devops)
   - [Parametros del Pipeline](#parametros-del-pipeline)
   - [Variables del Pipeline](#variables-del-pipeline)
   - [Service Connections Requeridas](#service-connections-requeridas)
   - [Flujo del Pipeline](#flujo-del-pipeline)
   - [Cuadro de Tareas por Job](#cuadro-de-tareas-por-job)
6. [Versionamiento Semantico](#versionamiento-semantico)
7. [Manifiestos de Kubernetes](#manifiestos-de-kubernetes)
8. [Configuracion del Agente Self-Hosted con Minikube](#configuracion-del-agente-self-hosted-con-minikube)
   - [Prerequisitos](#prerequisitos)
   - [Configuracion del .env](#configuracion-del-env)
   - [Levantar el Entorno](#levantar-el-entorno)
   - [Registrar el Agent Pool en Azure DevOps](#registrar-el-agent-pool-en-azure-devops)
9. [Ejecucion del Pipeline](#ejecucion-del-pipeline)
   - [Ejecucion Normal (CI + CD)](#ejecucion-normal-ci--cd)
   - [Ejecucion de Rollback](#ejecucion-de-rollback)
10. [Evidencias de Ejecucion](#evidencias-de-ejecucion)

---

## Descripcion del Proyecto

Este proyecto implementa un microservicio REST desarrollado en **Python (Flask)** con un pipeline completo de **CI/CD en Azure DevOps**. El pipeline realiza la integracion continua (build, tests unitarios, analisis de codigo con SonarCloud, build de imagen Docker, escaneo de vulnerabilidades con Trivy y push a DockerHub) y el despliegue continuo en un cluster de **Minikube** mediante un agente self-hosted.

El microservicio expone los siguientes endpoints:

| Endpoint | Metodo | Descripcion |
|----------|--------|-------------|
| `/` | GET | Interfaz web para pruebas interactivas |
| `/DevOps` | POST | Endpoint principal - Valida API Key, procesa payload JSON y retorna mensaje con JWT |
| `/health` | GET | Health check del servicio |

---

## Arquitectura General

```
                    Azure DevOps Pipeline
                    =====================
    [Trigger: Push/PR]     [Manual: Rollback]
            |                       |
            v                       v
    +---------------+       +---------------+
    |   CI Stage    |       |   CD Stage    |
    |  (3 Jobs)     |       |  (1 Job)      |
    +---------------+       +---------------+
    | BuildJob      |       | DeployJob     |
    | TestJob       |       | (minikube-    |
    | DockerJob     |       |  agents pool) |
    +-------+-------+       +-------+-------+
            |                       |
            v                       v
    +---------------+       +---------------+
    |  DockerHub    |       | Minikube      |
    |  Registry     |------>| Cluster       |
    +---------------+       +---------------+
                            | Namespace:    |
                            | devops-       |
                            | microservice  |
                            +---------------+
                            | - Deployment  |
                            | - Service LB  |
                            | - ConfigMap   |
                            | - Secret      |
                            | - HPA         |
                            +---------------+
```

---

## Estructura de Carpetas

```
ronny-tabango-pruebatecnica-tcs/
|
|-- api_python/                          # Microservicio Python Flask
|   |-- app.py                           # Aplicacion principal
|   |-- Dockerfile                       # Dockerfile multi-stage
|   |-- docker-compose.yml               # Docker Compose para desarrollo local
|   |-- requirements.txt                 # Dependencias Python
|   |-- .env.example                     # Ejemplo de variables de entorno
|   |-- tests/                           # Tests unitarios
|       |-- conftest.py                  # Fixtures de pytest
|       |-- test_app.py                  # 25 tests unitarios
|
|-- devops/                              # Pipeline Azure DevOps (Pipeline as Code)
|   |-- azure-pipelines.yml              # Archivo principal del pipeline
|   |-- stages/                          # Templates de stages
|   |   |-- ci.yml                       # Stage CI - Integracion Continua
|   |   |-- cd.yml                       # Stage CD - Despliegue Continuo
|   |-- jobs/                            # Templates de jobs
|   |   |-- build.yml                    # Job: Build App Python
|   |   |-- test.yml                     # Job: Unit Tests & Sonar Analysis
|   |   |-- docker.yml                   # Job: Docker Build, Scan & Push
|   |   |-- deploy.yml                   # Job: Deploy to Minikube
|   |-- steps/                           # Templates de steps (reutilizables)
|       |-- python/
|       |   |-- install-dependencies.yml # Instalar dependencias Python
|       |-- test/
|       |   |-- run-unit-tests.yml       # Ejecutar tests unitarios
|       |   |-- sonar-analysis.yml       # Analisis SonarCloud
|       |-- docker/
|       |   |-- build-docker.yml         # Build imagen Docker
|       |   |-- trivy-scan.yml           # Escaneo vulnerabilidades Trivy
|       |   |-- push-dockerhub.yml       # Push a DockerHub
|       |-- minikube/
|           |-- deploy-minikube.yml      # Deploy en Minikube via SSH
|
|-- k8s/                                 # Manifiestos de Kubernetes (IaC)
|   |-- kustomization.yaml               # Configuracion Kustomize
|   |-- namespace.yaml                   # Namespace: devops-microservice
|   |-- configmap.yaml                   # Variables de entorno no sensibles
|   |-- secret.yaml                      # Variables sensibles (SECRET_KEY, API_KEY)
|   |-- deployment.yaml                  # Deployment con IMAGE_PLACEHOLDER
|   |-- service.yaml                     # Service tipo LoadBalancer
|   |-- hpa.yaml                         # HorizontalPodAutoscaler
|   |-- deploy.sh                        # Script de deploy en Minikube
|
|-- minikube-image/                      # Imagenes Docker del entorno Minikube + Agente
|   |-- docker-compose.yml               # Orquestacion de contenedores
|   |-- .env.example                     # Variables de configuracion del agente
|   |-- azure-agent/                     # Imagen del agente Azure DevOps
|   |   |-- Dockerfile
|   |   |-- entrypoint.sh
|   |-- minikube-server/                 # Imagen del servidor Minikube
|       |-- Dockerfile
|       |-- entrypoint.sh
|
|-- configVersion.json                   # Version semantica del proyecto
|-- DevOps_Microservice.postman_collection.json  # Coleccion Postman para pruebas
```

---

## Microservicio Python (Flask)

### Tecnologias

| Tecnologia | Version | Proposito |
|------------|---------|-----------|
| Python | 3.11 | Runtime |
| Flask | 3.0.0 | Framework web |
| PyJWT | 2.8.0 | Generacion de tokens JWT |
| Gunicorn | - | Servidor WSGI de produccion |
| pytest | 8.3.4 | Framework de testing |
| pytest-cov | 6.0.0 | Cobertura de codigo |

### Endpoints

| Endpoint | Metodo | Headers Requeridos | Descripcion |
|----------|--------|--------------------|-------------|
| `/` | GET | Ninguno | Interfaz web de testing |
| `/DevOps` | POST | `X-Parse-REST-API-Key`, `Content-Type: application/json` | Procesa mensaje y retorna respuesta con JWT |
| `/DevOps` | GET, PUT, DELETE, PATCH | - | Retorna `ERROR` con status 405 |
| `/health` | GET | Ninguno | Health check: `{"status": "healthy"}` |

### Ejemplo de uso del endpoint `/DevOps`

```bash
curl -X POST http://localhost:30080/DevOps \
  -H "Content-Type: application/json" \
  -H "X-Parse-REST-API-Key: 2f5ae96c-b558-4c7b-a590-a501ae1c3f6c" \
  -d '{"to": "Juan Perez"}'
```

**Respuesta:**
```json
{
  "message": "Hello Juan Perez your message will be send"
}
```

---

## Pipeline CI/CD en Azure DevOps

### Parametros del Pipeline

Los parametros se configuran al momento de ejecutar el pipeline manualmente desde Azure DevOps:

| Parametro | Tipo | Valor por Defecto | Descripcion |
|-----------|------|-------------------|-------------|
| `semanticVersion` | string | `none` | Controla el modo de ejecucion. `none` = ejecucion normal (CI + CD). Cualquier otro valor (ej: `1.0.0`) = modo rollback, salta CI y ejecuta solo CD con la version especificada |
| `imageName` | string | `ronnyt854/devops-microservice` | Nombre completo de la imagen Docker en DockerHub (usuario/repositorio) |
| `sonarProjectName` | string | `ronny-tabango-pruebatecnica-tcs` | Nombre del proyecto configurado en SonarCloud |
| `sonarOrganization` | string | `ronny854` | Organizacion en SonarCloud |

### Variables del Pipeline

Las variables se definen en el archivo `azure-pipelines.yml` y son compartidas entre todos los stages y jobs:

| Variable | Valor | Descripcion |
|----------|-------|-------------|
| `containerRegistry` | `docker.io` | Registry de Docker donde se almacenan las imagenes |
| `dockerHubServiceConnection` | `dockerRegistryServiceConnection` | Nombre de la Service Connection en Azure DevOps para autenticarse con DockerHub |
| `sonarServiceConnection` | `conection-sonarqube-github-account` | Nombre de la Service Connection en Azure DevOps para conectarse con SonarCloud |

### Service Connections Requeridas

Para que el pipeline funcione correctamente, se deben configurar las siguientes **Service Connections** en Azure DevOps (Project Settings > Service Connections):

| Service Connection | Tipo | Proposito | Configuracion |
|-------------------|------|-----------|---------------|
| `dockerRegistryServiceConnection` | Docker Registry | Autenticacion con DockerHub para push/pull de imagenes | Tipo: Docker Hub. Requiere Docker ID y Password o Access Token de DockerHub |
| `conection-sonarqube-github-account` | SonarCloud | Conexion con SonarCloud para analisis de codigo | Tipo: SonarCloud. Requiere token de SonarCloud generado en Account > Security |

#### Como crear la Service Connection de DockerHub

1. Ir a **Project Settings** > **Service Connections** > **New Service Connection**
2. Seleccionar **Docker Registry**
3. Seleccionar **Docker Hub**
4. Ingresar **Docker ID** y **Password** (o Access Token)
5. Nombre de la conexion: `dockerRegistryServiceConnection`
6. Marcar **Grant access permission to all pipelines**

![alt text](capturasPantalla/serviceConnectionDocker.png)

#### Como crear la Service Connection de SonarCloud

1. Ir a **Project Settings** > **Service Connections** > **New Service Connection**
2. Seleccionar **SonarCloud**
3. Ingresar el **token** generado en SonarCloud (My Account > Security > Generate Tokens)
4. Nombre de la conexion: `conection-sonarqube-github-account`
5. Marcar **Grant access permission to all pipelines**

![alt text](capturasPantalla/serviceConnectionSonar.png)

> **Importante:** En SonarCloud, se debe **desactivar el Automatic Analysis** del proyecto para evitar conflictos con el analisis desde el pipeline. Ir a SonarCloud > Proyecto > Administration > Analysis Method > Desactivar "Automatic Analysis".

### Flujo del Pipeline

#### Triggers Automaticos

El pipeline se ejecuta automaticamente cuando:

- **Push** a cualquier rama (`*`) con cambios en `api_python/`, `devops/` o `k8s/`
- **Pull Request** hacia las ramas `main`, `master` o `develop`

#### Modo Normal (semanticVersion = "none")

```
azure-pipelines.yml
    |
    +-- CI Stage (Continuous Integration)
    |   |
    |   +-- BuildJob (Build App Python)
    |   |   |-- Read Version (configVersion.json)
    |   |   |-- Install Dependencies
    |   |   |-- Validate Python Build
    |   |   |-- Publish Build Artifacts
    |   |
    |   +-- TestJob (Unit Tests & Sonar Analysis)  [depende de BuildJob]
    |   |   |-- Download Build Artifacts
    |   |   |-- Install Dependencies
    |   |   |-- Run Unit Tests
    |   |   |-- SonarCloud Prepare / Analyze / Publish
    |   |
    |   +-- DockerJob (Docker Build, Scan & Push)  [depende de BuildJob + TestJob]
    |       |-- Download Build Artifacts
    |       |-- Docker Build
    |       |-- Trivy Vulnerability Scan
    |       |-- DockerHub Login / Push / Cleanup
    |
    +-- CD Stage (Continuous Deployment)  [depende de CI]
        |
        +-- DeployJob (Deploy to Minikube)  [pool: minikube-agents]
            |-- Verify SSH Connection
            |-- Transfer K8s Manifests (con imagen inyectada)
            |-- Prepare Deploy Script
            |-- Deploy to Minikube
```

![alt text](capturasPantalla/pipelineNormal.png)

#### Modo Rollback (semanticVersion = "1.0.0")

```
azure-pipelines.yml
    |
    +-- CI Stage --> OMITIDO (no se ejecuta)
    |
    +-- CD Stage (sin dependencia de CI)
        |
        +-- DeployJob (Deploy to Minikube)  [pool: minikube-agents]
            |-- Verify SSH Connection
            |-- Verify DockerHub Version (valida que la version existe)
            |-- Transfer K8s Manifests
            |-- Prepare Deploy Script
            |-- Deploy to Minikube (Rollback)
```

![alt text](capturasPantalla/pipelineRollback.png)

### Cuadro de Tareas por Job

#### Stage CI - BuildJob (Build App Python)

| Step | Descripcion |
|------|-------------|
| **Read Version** | Lee la version semantica del archivo `configVersion.json` y la exporta como variable de salida `configVersion` para los demas jobs |
| **Setup Python 3.11** | Configura Python 3.11 en el agente de build |
| **Install Dependencies** | Instala las dependencias del proyecto desde `requirements.txt` junto con herramientas de testing (pytest, pytest-cov, flake8) |
| **Validate Python Build** | Valida que la aplicacion Flask se importa correctamente ejecutando `from app import app` |
| **Copy Source Code** | Copia el codigo fuente Python al directorio de artifacts |
| **Copy configVersion.json** | Copia el archivo de version al directorio de artifacts |
| **Publish Build Artifacts** | Publica los artifacts de build para que los demas jobs los consuman |

![alt text](capturasPantalla/buildJob.png)

#### Stage CI - TestJob (Unit Tests & Sonar Analysis)

| Step | Descripcion |
|------|-------------|
| **Download Build Artifacts** | Descarga los artifacts generados por el BuildJob |
| **Show Version** | Muestra en consola la version leida del BuildJob |
| **Setup Python 3.11** | Configura Python 3.11 en el agente |
| **Install Dependencies** | Instala dependencias de Python |
| **Run Unit Tests** | Ejecuta los 25 tests unitarios con pytest generando reportes JUnit XML y cobertura XML |
| **Publish Test Results** | Publica los resultados de los tests en Azure DevOps (pestana Tests) |
| **Publish Code Coverage** | Publica el reporte de cobertura de codigo en Azure DevOps (pestana Code Coverage) |
| **SonarCloud Prepare** | Prepara la configuracion del scanner de SonarCloud con el project key y la organizacion |
| **SonarCloud Analyze** | Ejecuta el analisis estatico de codigo con SonarCloud |
| **SonarCloud Publish** | Publica los resultados del analisis y espera el Quality Gate |

![alt text](capturasPantalla/testJob.png)

#### Stage CI - DockerJob (Docker Build, Scan & Push)

| Step | Descripcion |
|------|-------------|
| **Download Build Artifacts** | Descarga los artifacts del BuildJob incluyendo el codigo fuente |
| **Show Version** | Muestra la version que se usara como tag de la imagen Docker |
| **Docker Build** | Construye la imagen Docker usando multi-stage build. Tag: `docker.io/ronnyt854/devops-microservice:<version>` |
| **List Docker Images** | Lista las imagenes Docker disponibles en el agente para verificacion |
| **Docker Image Vulnerability Scan - Trivy** | Ejecuta Trivy para escanear vulnerabilidades HIGH y CRITICAL en la imagen Docker |
| **DockerHub Login** | Se autentica en DockerHub usando la Service Connection configurada |
| **Docker Push** | Sube la imagen a DockerHub con dos tags: `latest` y la version semantica. Exporta `imageFullNameTag` como variable de salida |
| **Docker Cleanup** | Cierra sesion de DockerHub y limpia imagenes no utilizadas |

![alt text](capturasPantalla/dockerJob.png)

#### Stage CD - DeployJob (Deploy to Minikube)

| Step | Descripcion |
|------|-------------|
| **Verify SSH Connection** | Verifica la conectividad SSH con el servidor minikube y valida que minikube esta corriendo |
| **Verify DockerHub Version (Rollback)** | Solo en modo rollback: verifica que la version especificada existe en DockerHub via API |
| **Transfer K8s Manifests** | Inyecta la imagen en `deployment.yaml` reemplazando `IMAGE_PLACEHOLDER` via `sed`, luego transfiere todos los manifiestos k8s al servidor minikube via SCP |
| **Prepare Deploy Script** | Asigna permisos de ejecucion al script `deploy.sh` en el servidor remoto |
| **Deploy to Minikube** | Ejecuta `deploy.sh` en el servidor minikube: pull de imagen, `kubectl apply -k`, rollout status, port-forward en puerto 30080 |

![alt text](capturasPantalla/deployJob.png)

---

## Versionamiento Semantico

La version del proyecto se gestiona desde un unico archivo: **`configVersion.json`**

```json
{
  "version": "1.0.2"
}
```

Esta version se utiliza para:

1. **Tag de la imagen Docker**: `docker.io/ronnyt854/devops-microservice:1.0.2`
2. **Tag `latest`**: siempre apunta a la ultima version publicada
3. **Rollback**: permite desplegar una version anterior especificando el numero en el parametro `semanticVersion`

Para actualizar la version, simplemente editar `configVersion.json` y hacer push. El pipeline automaticamente leera la nueva version y la utilizara en todo el flujo.

---

## Manifiestos de Kubernetes

Los manifiestos se encuentran en `k8s/` y se gestionan con **Kustomize**:

| Manifiesto | Descripcion |
|------------|-------------|
| `kustomization.yaml` | Define los recursos a aplicar, namespace comun y labels compartidos |
| `namespace.yaml` | Crea el namespace `devops-microservice` |
| `configmap.yaml` | Variables de entorno no sensibles: `FLASK_ENV=production`, `PORT=30080`, `JWT_EXPIRATION_HOURS=1` |
| `secret.yaml` | Variables sensibles: `SECRET_KEY`, `API_KEY` (tipo Opaque) |
| `deployment.yaml` | Deployment con 2 replicas, rolling update, liveness/readiness probes, resource limits. Usa `IMAGE_PLACEHOLDER` que se reemplaza en el pipeline |
| `service.yaml` | Service tipo LoadBalancer, puerto 80 -> targetPort 30080 |
| `hpa.yaml` | HorizontalPodAutoscaler: min 2, max 5 replicas. Escala por CPU (70%) y memoria (80%) |
| `deploy.sh` | Script de deploy que ejecuta `kubectl apply -k`, espera rollout y configura port-forward |

### Estrategia de Deploy

- **Rolling Update**: `maxSurge: 1`, `maxUnavailable: 0` (zero downtime)
- **Health Checks**: Liveness probe cada 30s, Readiness probe cada 10s en `/health:30080`
- **Autoescalado**: HPA escala entre 2 y 5 replicas segun uso de CPU/memoria
- **Inyeccion de imagen**: El pipeline reemplaza `IMAGE_PLACEHOLDER` en `deployment.yaml` con la imagen real antes de transferir al servidor

---

## Configuracion del Agente Self-Hosted con Minikube

El directorio `minikube-image/` contiene la configuracion Docker para levantar un entorno con:

- **minikube-server**: Contenedor con Docker-in-Docker que ejecuta Minikube
- **azure-agent**: Contenedor con el agente de Azure DevOps que se conecta via SSH al minikube-server

Ambos contenedores comparten un volumen de SSH keys para la comunicacion segura entre ellos.

### Prerequisitos

- Docker y Docker Compose instalados en la maquina host
- Cuenta en Azure DevOps con permisos para crear Agent Pools
- Personal Access Token (PAT) de Azure DevOps con permisos de **Agent Pools (Read & Manage)**

### Configuracion del .env

1. Copiar el archivo de ejemplo:

```bash
cd minikube-image
cp .env.example .env
```

2. Editar `.env` con los valores correspondientes:

```env
# URL de tu organizacion Azure DevOps
AZP_URL=https://dev.azure.com/tu-organizacion

# Personal Access Token (PAT)
AZP_TOKEN=tu-token-aqui

# Nombre del Agent Pool (debe coincidir con el pool creado en Azure DevOps)
AZP_POOL=minikube-agents

# Nombre del agente
AZP_AGENT_NAME=azure-agent-docker
```

#### Como generar el Personal Access Token (PAT)

1. Ir a Azure DevOps > **User Settings** (icono de usuario arriba a la derecha) > **Personal Access Tokens**
2. Click en **New Token**
3. Configurar:
   - **Name**: `minikube-agent`
   - **Scopes**: Custom > **Agent Pools** > Read & Manage
   - **Expiration**: Segun necesidad
4. Copiar el token generado y pegarlo en `AZP_TOKEN` del `.env`

### Registrar el Agent Pool en Azure DevOps

1. Ir a **Organization Settings** > **Agent Pools**
2. Click en **Add pool**
3. Configurar:
   - **Pool type**: Self-hosted
   - **Name**: `minikube-agents`
   - Marcar **Grant access permission to all pipelines**
4. Click en **Create**

### Levantar el Entorno

```bash
cd minikube-image

# Construir y levantar los contenedores
docker-compose up -d --build

# Verificar que ambos contenedores estan corriendo
docker-compose ps

# Ver logs del agente para confirmar registro exitoso
docker-compose logs -f azure-agent

# Ver logs del servidor minikube
docker-compose logs -f minikube-server
```

El contenedor `minikube-server` tarda aproximadamente 2-3 minutos en iniciar Minikube completamente. El `azure-agent` esperara a que minikube-server este saludable antes de registrarse con Azure DevOps.

#### Verificar que todo funciona

```bash
# Verificar que minikube esta corriendo
docker exec minikube-server minikube status

# Verificar que el agente esta registrado (debe aparecer Online en Azure DevOps)
docker exec azure-agent bash -c "ls /azp/agent"

# Probar conectividad SSH entre agente y minikube-server
docker exec azure-agent ssh minikube-server "echo 'SSH OK' && minikube status"
```

#### Acceder al Dashboard de Minikube

Una vez que minikube esta corriendo, se puede acceder al dashboard de Kubernetes desde el host mediante el siguiente enlace:

```
http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/http:kubernetes-dashboard:/proxy/
```

![alt text](capturasPantalla/agenteAzure.png)

![alt text](capturasPantalla/minikubeDashboard.png)

### Puertos Expuestos

| Puerto | Servicio | Descripcion |
|--------|----------|-------------|
| 2222 | SSH | Acceso SSH al servidor minikube |
| 8443 | Kubernetes API | API Server de Minikube |
| 30000-30100 | NodePort | Rango de puertos NodePort para servicios |

---

## Ejecucion del Pipeline

### Ejecucion Normal (CI + CD)

Esta es la ejecucion por defecto que se dispara automaticamente con cada push o se puede ejecutar manualmente:

1. Ir a **Pipelines** > Seleccionar el pipeline > **Run pipeline**
2. Dejar `semanticVersion` en `none` (valor por defecto)
3. Click en **Run**

El pipeline ejecutara:
- **CI**: Build Python > Tests + SonarCloud > Docker Build + Trivy + Push DockerHub
- **CD**: Deploy en Minikube con la imagen recien construida

![alt text](capturasPantalla/formularioPipelineNormal.png)
![alt text](capturasPantalla/pipelineNormal.png)

### Ejecucion de Rollback

Para desplegar una version anterior:

1. Ir a **Pipelines** > Seleccionar el pipeline > **Run pipeline**
2. En `semanticVersion` ingresar la version deseada, por ejemplo: `1.0.0`
3. Click en **Run**

El pipeline:
- **Omite** el stage CI completamente
- Verifica que la version `1.0.0` exista en DockerHub
- Despliega esa version directamente en Minikube

![alt text](capturasPantalla/formularioPipelineRollback.png)

![alt text](capturasPantalla/pipelineRollback.png)

---

## Evidencias de Ejecucion

### Pipeline - Vista General

![alt text](capturasPantalla/pipelineNormal.png)

### Stage CI - BuildJob

![alt text](capturasPantalla/stepReadVersion.png)

![alt text](capturasPantalla/stepBuilPython.png)

### Stage CI - TestJob

![alt text](capturasPantalla/stepLogUnitTest.png)

![alt text](capturasPantalla/stepPublishCoverageTest.png)

![alt text](capturasPantalla/stepAnalisisSonar.png)

![alt text](capturasPantalla/stepPublishTest.png)


### Stage CI - DockerJob

![alt text](capturasPantalla/stepDockerBuild.png)

![alt text](capturasPantalla/stepTrivyAnalisis.png)

![alt text](capturasPantalla/stepDockerPush.png)

### SonarCloud

![alt text](capturasPantalla/dashboardSonar.png)

### DockerHub

![alt text](capturasPantalla/dockerHub.png)

### Stage CD - DeployJob

![alt text](capturasPantalla/stepCheckServer.png)

![alt text](capturasPantalla/stepTransferManifiestos.png)

![alt text](capturasPantalla/stepDeployApp.png)

### Pruebas del Servicio Desplegado

Una vez finalizado el deploy, se realizaron pruebas funcionales contra el microservicio expuesto en `http://localhost:30080` para validar el correcto funcionamiento de los endpoints.

#### Prueba 1 - Endpoint POST `/DevOps` (Request valido)

Envio de un request POST con API Key valida y payload JSON correcto. Se valida la respuesta exitosa con el mensaje esperado.

![alt text](capturasPantalla/Prueba1.png)

#### Prueba 2 - Endpoint POST `/DevOps` (API Key invalida)

Envio de un request POST con una API Key no valida. Se valida que el servicio rechaza la peticion correctamente.

![alt text](capturasPantalla/Prueba2.png)


#### Prueba 3 - Metodo no permitido (`GET /DevOps`)

Validacion de que los metodos HTTP no permitidos (GET, PUT, DELETE, PATCH) retornan `ERROR` con status 405.

![alt text](capturasPantalla/Prueba3.png)

![alt text](capturasPantalla/Prueba4.png)

### Kubernetes - Estado del Cluster

2 Pods con el servicio desplegado
![alt text](capturasPantalla/podsKubernetes.png)

Servicio de LoadBalancer
![alt text](capturasPantalla/loadBalancer.png)

### Rollback

Se despliega la version 1.0.2 con errores en la sintaxis de la web

![alt text](capturasPantalla/rollback1.png)

Se coloca la version 1.0.0 en los parametros para realizar el proceso de rollback

![alt text](capturasPantalla/formularioPipelineRollback.png)

Se realiza una validación si la imagen con esa version existe en dockerHub

![alt text](capturasPantalla/verifyVersion.png)

Verificamos la tarea de rollback

![alt text](capturasPantalla/deployRollback.png)

Entramos nuevamente en la url http://localhost:30080/ y validamos que el rollback fue exitoso

![alt text](capturasPantalla/rollbackSuccess.png)





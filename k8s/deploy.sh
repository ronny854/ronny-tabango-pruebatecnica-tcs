#!/bin/bash
set -euo pipefail

# =============================================================================
# deploy.sh - Deploy DevOps Microservice en Minikube
# =============================================================================
# Uso: deploy.sh <IMAGE_FULL_TAG>
#   IMAGE_FULL_TAG: Imagen completa con tag (ej: docker.io/ronnyt854/devops-microservice:1.0.0)
#
# La imagen ya viene inyectada en deployment.yaml desde el pipeline.
# =============================================================================

DEPLOY_IMAGE="${1:?ERROR: Se requiere la imagen completa como argumento (ej: registry/image:tag)}"

NAMESPACE="devops-microservice"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="${SCRIPT_DIR}"
SERVICE_NAME="devops-microservice"
SERVICE_PORT=80
EXPOSE_PORT=30080

echo "=========================================="
echo "  Deploy DevOps Microservice en Minikube"
echo "=========================================="
echo "  Imagen:    ${DEPLOY_IMAGE}"
echo "  Namespace: ${NAMESPACE}"
echo "=========================================="

# -----------------------------------------------------------------------------
# 1. Verificar que minikube y kubectl estan disponibles
# -----------------------------------------------------------------------------
echo ""
echo "[1/5] Verificando herramientas..."
kubectl version --client --short 2>/dev/null || kubectl version --client
minikube status || { echo "ERROR: Minikube no esta corriendo"; exit 1; }

# -----------------------------------------------------------------------------
# 2. Pull de la imagen en minikube
# -----------------------------------------------------------------------------
echo ""
echo "[2/5] Descargando imagen ${DEPLOY_IMAGE} en minikube..."
docker pull "${DEPLOY_IMAGE}" || {
  echo "WARN: No se pudo hacer pull. Verificando si existe localmente..."
  docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "${DEPLOY_IMAGE}" || {
    echo "ERROR: La imagen ${DEPLOY_IMAGE} no existe localmente ni en el registry"
    exit 1
  }
}

# -----------------------------------------------------------------------------
# 3. Aplicar manifiestos de Kubernetes
# -----------------------------------------------------------------------------
echo ""
echo "[3/5] Aplicando manifiestos de Kubernetes..."
echo "Imagen en deployment.yaml:"
grep "image:" "${K8S_DIR}/deployment.yaml" || true

kubectl apply -k "${K8S_DIR}"

# -----------------------------------------------------------------------------
# 4. Esperar a que el deployment este listo
# -----------------------------------------------------------------------------
echo ""
echo "[4/5] Esperando a que los pods esten listos..."
kubectl rollout status deployment/${SERVICE_NAME} -n ${NAMESPACE} --timeout=120s

echo ""
echo "Estado de los pods:"
kubectl get pods -n ${NAMESPACE} -o wide

echo ""
echo "Estado del servicio:"
kubectl get svc -n ${NAMESPACE}

# -----------------------------------------------------------------------------
# 5. Exponer el servicio y mostrar URL de acceso
# -----------------------------------------------------------------------------
echo ""
echo "[5/5] Exponiendo servicio LoadBalancer..."

# Matar cualquier port-forward anterior del mismo servicio
pkill -f "kubectl port-forward.*svc/${SERVICE_NAME}" 2>/dev/null || true
sleep 1

# Ejecutar port-forward en segundo plano
nohup kubectl port-forward svc/${SERVICE_NAME} ${EXPOSE_PORT}:${SERVICE_PORT} \
  -n ${NAMESPACE} --address 0.0.0.0 \
  > /tmp/port-forward-${SERVICE_NAME}.log 2>&1 &

PF_PID=$!
sleep 2

# Verificar que el port-forward esta corriendo
if kill -0 $PF_PID 2>/dev/null; then
  echo ""
  echo "=========================================="
  echo "  DEPLOY EXITOSO"
  echo "=========================================="
  echo ""
  echo "  Servicio expuesto en:"
  echo "    -> http://localhost:${EXPOSE_PORT}"
  echo ""
  echo "  Health check:"
  echo "    -> http://localhost:${EXPOSE_PORT}/health"
  echo ""
  echo "  Interfaz web:"
  echo "    -> http://localhost:${EXPOSE_PORT}/"
  echo ""
  echo "  Imagen desplegada: ${DEPLOY_IMAGE}"
  echo "  Port-forward PID: ${PF_PID}"
  echo "  Log: /tmp/port-forward-${SERVICE_NAME}.log"
  echo ""
  echo "  Para detener el port-forward:"
  echo "    kill ${PF_PID}"
  echo "=========================================="

  # Verificar health check
  echo ""
  echo "Verificando health check..."
  sleep 3
  curl -s --max-time 5 "http://localhost:${EXPOSE_PORT}/health" || echo "WARN: Health check no respondio aun, puede tardar unos segundos"
else
  echo "ERROR: El port-forward no se pudo iniciar"
  cat /tmp/port-forward-${SERVICE_NAME}.log 2>/dev/null
  exit 1
fi

echo ""
echo "Deploy completado."

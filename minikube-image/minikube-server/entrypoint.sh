#!/bin/bash
set -e

# Función para configurar SSH keys
setup_ssh_keys() {
    echo "Configurando SSH keys..."

    # Esperar a que la clave pública esté disponible en el volumen compartido
    timeout=120
    while [ $timeout -gt 0 ]; do
        if [ -f /ssh-keys/id_rsa.pub ]; then
            echo "Clave pública encontrada."
            # Agregar la clave pública a authorized_keys
            cat /ssh-keys/id_rsa.pub >> /root/.ssh/authorized_keys
            chmod 600 /root/.ssh/authorized_keys
            echo "SSH key agregada a authorized_keys."
            break
        fi
        echo "Esperando clave pública... ($timeout segundos restantes)"
        sleep 5
        timeout=$((timeout - 5))
    done

    if [ $timeout -le 0 ]; then
        echo "AVISO: No se encontró clave pública en /ssh-keys/id_rsa.pub"
    fi
}

# Iniciar servicio SSH
echo "Iniciando servicio SSH..."
service ssh start

# Configurar SSH keys en segundo plano
setup_ssh_keys &

# Iniciar el daemon de Docker en segundo plano
echo "Iniciando Docker daemon..."
dockerd > /var/log/dockerd.log 2>&1 &

# Esperar a que Docker esté listo
echo "Esperando a que Docker esté disponible..."
timeout=60
while [ $timeout -gt 0 ]; do
    if docker info >/dev/null 2>&1; then
        echo "Docker está listo."
        break
    fi
    sleep 1
    timeout=$((timeout - 1))
done

if [ $timeout -eq 0 ]; then
    echo "Error: Docker no pudo iniciar. Logs:"
    cat /var/log/dockerd.log
    exit 1
fi

# Ejecutar el comando pasado como argumento (minikube start)
echo "Ejecutando: $@"
"$@"

# Habilitar el addon de dashboard
echo "Habilitando dashboard..."
minikube addons enable dashboard
minikube addons enable metrics-server

# Esperar a que todos los pods del dashboard estén listos
echo "Esperando a que el dashboard esté disponible..."
sleep 10

# Esperar pods en kubernetes-dashboard namespace
kubectl wait --for=condition=ready pod --all -n kubernetes-dashboard --timeout=180s || true

# Mostrar estado de los pods del dashboard
echo "Pods del dashboard:"
kubectl get pods -n kubernetes-dashboard

# Mostrar servicios disponibles
echo "Servicios del dashboard:"
kubectl get svc -n kubernetes-dashboard

# Iniciar kubectl proxy en segundo plano para exponer el dashboard
echo "Iniciando proxy para el dashboard..."
kubectl proxy --address='0.0.0.0' --port=8001 --accept-hosts='.*' > /var/log/kubectl-proxy.log 2>&1 &

sleep 5

# Mostrar información de acceso
echo ""
echo "========================================"
echo "  MINIKUBE DASHBOARD DISPONIBLE"
echo "========================================"
echo ""
echo "URL del Dashboard:"
echo "http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/http:kubernetes-dashboard:/proxy/"
echo ""
echo "Estado del cluster:"
minikube status
echo ""
echo "Nodos:"
kubectl get nodes
echo ""
echo "SSH habilitado con autenticación por key"
echo "========================================"

# Mantener el contenedor corriendo
tail -f /dev/null

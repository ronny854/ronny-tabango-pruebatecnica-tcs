#!/bin/bash
set -e

# Variables de entorno requeridas
AZP_URL=${AZP_URL:-""}
AZP_TOKEN=${AZP_TOKEN:-""}
AZP_POOL=${AZP_POOL:-"Default"}
AZP_AGENT_NAME=${AZP_AGENT_NAME:-"azure-agent-docker"}

# Generar SSH keys si no existen
echo "Configurando SSH keys..."
if [ ! -f /ssh-keys/id_rsa ]; then
    echo "Generando nuevas SSH keys..."
    ssh-keygen -t rsa -b 4096 -f /ssh-keys/id_rsa -N "" -C "azureagent@azure-agent"
    chmod 600 /ssh-keys/id_rsa
    chmod 644 /ssh-keys/id_rsa.pub
    echo "SSH keys generadas."
else
    echo "SSH keys ya existen."
fi

# Copiar keys al directorio .ssh del usuario
cp /ssh-keys/id_rsa ~/.ssh/id_rsa
cp /ssh-keys/id_rsa.pub ~/.ssh/id_rsa.pub
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub

# Configurar SSH para no verificar host en primera conexión
cat > ~/.ssh/config << 'EOF'
Host minikube-server
    HostName minikube-server
    User root
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    LogLevel ERROR
EOF
chmod 600 ~/.ssh/config

# Esperar a que el servidor minikube esté disponible y tenga la key configurada
echo "Esperando conexión SSH con minikube-server..."
timeout=180
while [ $timeout -gt 0 ]; do
    if ssh -o ConnectTimeout=5 minikube-server "echo 'SSH OK'" 2>/dev/null; then
        echo "Conexión SSH con minikube-server establecida."
        break
    fi
    echo "Esperando minikube-server... ($timeout segundos restantes)"
    sleep 5
    timeout=$((timeout - 5))
done

if [ $timeout -le 0 ]; then
    echo "AVISO: No se pudo establecer conexión SSH con minikube-server"
fi

# Copiar kubeconfig desde minikube-server
echo "Obteniendo kubeconfig de minikube-server..."
ssh minikube-server "cat /root/.kube/config" > ~/.kube/config 2>/dev/null || true

# Ajustar la URL del API server en kubeconfig para apuntar a minikube-server
if [ -f ~/.kube/config ]; then
    sed -i 's/127.0.0.1/minikube-server/g' ~/.kube/config
    sed -i 's/localhost/minikube-server/g' ~/.kube/config
    echo "Kubeconfig configurado."
fi

# Verificar si se proporcionaron las credenciales de Azure DevOps
if [ -z "$AZP_URL" ] || [ -z "$AZP_TOKEN" ]; then
    echo ""
    echo "========================================"
    echo "  AZURE AGENT - MODO STANDALONE"
    echo "========================================"
    echo ""
    echo "No se proporcionaron credenciales de Azure DevOps."
    echo "El contenedor se ejecutará sin registrar el agente."
    echo ""
    echo "Para registrar el agente, proporcione:"
    echo "  - AZP_URL: URL de tu organización Azure DevOps"
    echo "  - AZP_TOKEN: Personal Access Token"
    echo "  - AZP_POOL: Pool de agentes (default: Default)"
    echo ""
    echo "Prueba de conectividad SSH (con key):"
    ssh minikube-server "hostname && minikube status" || echo "SSH no disponible aún"
    echo ""
    echo "========================================"

    # Mantener el contenedor corriendo
    tail -f /dev/null
fi

# Configurar el agente
echo "Configurando Azure DevOps Agent..."
./config.sh --unattended \
    --url "$AZP_URL" \
    --auth pat \
    --token "$AZP_TOKEN" \
    --pool "$AZP_POOL" \
    --agent "$AZP_AGENT_NAME" \
    --acceptTeeEula \
    --replace

# Ejecutar el agente
echo "Iniciando Azure DevOps Agent..."
./run.sh

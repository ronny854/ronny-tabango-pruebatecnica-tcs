# Imagen base Ubuntu con Docker para ejecutar Minikube
FROM ubuntu:22.04

# Variables de entorno
ENV MINIKUBE_VERSION=v1.32.0
ENV KUBECTL_VERSION=v1.29.0
ENV MINIKUBE_HOME=/root/.minikube
ENV KUBECONFIG=/root/.kube/config
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    iptables \
    iproute2 \
    conntrack \
    sudo \
    systemctl \
    openssh-server \
    && rm -rf /var/lib/apt/lists/*

# Configurar SSH para autenticación con keys
RUN mkdir -p /var/run/sshd && \
    mkdir -p /root/.ssh && \
    chmod 700 /root/.ssh && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && \
    sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# Crear directorio compartido para SSH keys
RUN mkdir -p /ssh-keys

# Instalar Docker
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y docker-ce docker-ce-cli containerd.io && \
    rm -rf /var/lib/apt/lists/*

# Instalar kubectl
RUN curl -LO "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" && \
    chmod +x kubectl && \
    mv kubectl /usr/local/bin/

# Instalar Minikube
RUN curl -LO "https://storage.googleapis.com/minikube/releases/${MINIKUBE_VERSION}/minikube-linux-amd64" && \
    chmod +x minikube-linux-amd64 && \
    mv minikube-linux-amd64 /usr/local/bin/minikube

# Crear directorios necesarios
RUN mkdir -p /root/.kube /root/.minikube

# Script de inicio
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Exponer puertos
EXPOSE 22 8001 8443 10250 30000-32767

# Volumen para persistencia
VOLUME ["/var/lib/docker", "/root/.minikube"]

ENTRYPOINT ["/entrypoint.sh"]
CMD ["minikube", "start", "--driver=docker", "--force"]

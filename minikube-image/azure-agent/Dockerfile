# Imagen base Ubuntu para Azure DevOps Agent
FROM ubuntu:22.04

# Variables de entorno
ENV DEBIAN_FRONTEND=noninteractive
ENV AGENT_VERSION=4.266.2
ENV KUBECTL_VERSION=v1.29.0

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    jq \
    libicu70 \
    libssl3 \
    openssh-client \
    sudo \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Instalar kubectl
RUN curl -LO "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" && \
    chmod +x kubectl && \
    mv kubectl /usr/local/bin/

# Crear usuario para el agente
RUN useradd -m -s /bin/bash azureagent && \
    echo 'azureagent ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Crear directorio del agente
RUN mkdir -p /azp/agent && \
    chown -R azureagent:azureagent /azp

# Descargar Azure DevOps Agent
WORKDIR /azp/agent
RUN curl -LsS https://download.agent.dev.azure.com/agent/${AGENT_VERSION}/vsts-agent-linux-x64-${AGENT_VERSION}.tar.gz | tar -xz && \
    chown -R azureagent:azureagent /azp

# Crear directorios .ssh y .kube para el usuario
RUN mkdir -p /home/azureagent/.ssh && \
    mkdir -p /home/azureagent/.kube && \
    chown -R azureagent:azureagent /home/azureagent/.ssh && \
    chown -R azureagent:azureagent /home/azureagent/.kube && \
    chmod 700 /home/azureagent/.ssh

# Crear directorio compartido para SSH keys
RUN mkdir -p /ssh-keys && \
    chown -R azureagent:azureagent /ssh-keys

# Script de inicio
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Cambiar al usuario azureagent
USER azureagent
WORKDIR /azp/agent

ENTRYPOINT ["/entrypoint.sh"]

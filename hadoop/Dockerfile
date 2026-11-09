
# Imagen base
FROM debian:bookworm-slim

# Version de Hadoop
ARG HADOOP_VERSION=3.4.1

# Variables de entorno
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# Instalar Java, Python, SSH y herramientas
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk-headless \
    python3 \
    python3-pip \
    openssh-server \
    openssh-client \
    wget \
    curl \
    procps \
    ca-certificates \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Descargar e instalar Hadoop
RUN wget -q \
    https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz \
    -O /tmp/hadoop.tar.gz \
    && tar -xzf /tmp/hadoop.tar.gz -C /opt \
    && mv /opt/hadoop-${HADOOP_VERSION} /opt/hadoop \
    && rm /tmp/hadoop.tar.gz

# Crear usuario Hadoop
RUN useradd -m -s /bin/bash hadoop

# Crear directorios necesarios
RUN mkdir -p \
    /run/sshd \
    /shared-ssh \
    /data/input \
    /data/output \
    /app/mapreduce \
    && chown -R hadoop:hadoop \
    /opt/hadoop \
    /home/hadoop \
    /data/output \
    /app/mapreduce

# Configurar Java para Hadoop
RUN echo "export JAVA_HOME=${JAVA_HOME}" >> \
    ${HADOOP_HOME}/etc/hadoop/hadoop-env.sh

# Configuracion SSH
RUN mkdir -p /etc/ssh/sshd_config.d && \
    printf '%s\n' \
    "PubkeyAuthentication yes" \
    "PasswordAuthentication no" \
    "KbdInteractiveAuthentication no" \
    "PermitRootLogin no" \
    "AllowUsers hadoop" \
    "AuthorizedKeysFile .ssh/authorized_keys" \
    > /etc/ssh/sshd_config.d/99-hadoop.conf

# Copiar configuraciones
COPY core-site.xml ${HADOOP_CONF_DIR}/core-site.xml
COPY mapred-site.xml ${HADOOP_CONF_DIR}/mapred-site.xml

# Copiar script de inicio
COPY entrypoint.sh /entrypoint.sh

RUN python3 -c "p='/entrypoint.sh'; b=open(p,'rb').read(); b=b.removeprefix(bytes.fromhex('efbbbf')).replace(b'\r\n',b'\n').replace(b'\r',b'\n'); open(p,'wb').write(b)" \
    && chmod +x /entrypoint.sh

# Puerto SSH
EXPOSE 22

# Iniciar contenedor
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]

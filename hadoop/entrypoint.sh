
#!/bin/bash

set -e

echo "Iniciando configuracion SSH..."

# Crear directorios
mkdir -p /run/sshd
mkdir -p /shared-ssh
mkdir -p /home/hadoop/.ssh

# Asignar permisos
chown -R hadoop:hadoop /shared-ssh
chown -R hadoop:hadoop /home/hadoop/.ssh

chmod 700 /shared-ssh
chmod 700 /home/hadoop/.ssh

# Generar llave si no existe
if [ ! -f /shared-ssh/id_ed25519 ]; then

    su -s /bin/bash hadoop -c \
    "ssh-keygen -t ed25519 -N '' -f /shared-ssh/id_ed25519"

fi

# Configurar llave publica autorizada
cp /shared-ssh/id_ed25519.pub \
   /home/hadoop/.ssh/authorized_keys

# Copiar llave privada para localhost
cp /shared-ssh/id_ed25519 \
   /home/hadoop/.ssh/id_ed25519

# Configurar permisos
chown -R hadoop:hadoop /home/hadoop/.ssh

chmod 700 /home/hadoop/.ssh
chmod 600 /home/hadoop/.ssh/authorized_keys
chmod 600 /home/hadoop/.ssh/id_ed25519

# Generar claves del servidor SSH
ssh-keygen -A

# Iniciar servidor SSH
echo "Iniciando servidor SSH..."

 /usr/sbin/sshd

echo "SSH iniciado correctamente."

# Mantener contenedor activo como usuario hadoop
exec su - hadoop -s /bin/bash -c "tail -f /dev/null"

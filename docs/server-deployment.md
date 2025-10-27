
# Despliegue del servidor on‑premise y tunelización con Cloudflare

Este documento recoge el procedimiento seguido para publicar servicios de un servidor on‑premise usando Cloudflare Tunnel y subdominios. Está escrito como guía paso a paso basada en la instalación realizada para el dominio del proyecto CTEI (cteisabaneta.space). Ajusta nombres y valores según tu entorno.

## Resumen de la solución

- Compras un dominio en un registrador (ej. Namecheap).
- Apuntas el dominio a Cloudflare (cambias los nameservers en el panel del registrador).
- Creas un túnel (Cloudflare Tunnel / cloudflared) en tu servidor on‑premise y lo configuras con un archivo `config.yml` que mapea subdominios a servicios locales (HTTP, TCP, SSH, etc.).
- Instalas `cloudflared` como servicio systemd para mantener el túnel activo.
- Para administración SSH remota se puede usar `cloudflared access ssh` y un alias para simplificar la conexión.

## Prerrequisitos

- Tener control del dominio comprado y acceso al panel del registrador (Namecheap u otro).
- Acceso root o sudo al servidor Linux on‑premise donde correrá `cloudflared`.
- (Opcional) Docker / docker‑compose instalados en el servidor para desplegar tu aplicación.

## Pasos detallados

### 1) Comprar dominio

Compra el dominio en el registrador elegido (en el caso de ejemplo se usó Namecheap para `cteisabaneta.space`).

### 2) Añadir dominio en Cloudflare

1. Entra a Cloudflare y pulsa el botón "Add site" (Agregar sitio).
2. Selecciona la opción para conectarlo con un dominio y escribe el dominio que compraste.
3. Cloudflare te dará un conjunto de nameservers.
4. Copia esos nameservers.

### 3) Cambiar nameservers en el registrador

1. Entra al panel de control del registrador (ej. Namecheap) y localiza la opción de `Manage` o `DNS` del dominio.
2. Busca la sección `Nameservers` y selecciona la opción para `Custom DNS` (nameservers personalizados).
3. Pega los nameservers proporcionados por Cloudflare.
4. Guarda los cambios y espera la propagación DNS (puede tardar desde minutos hasta 24‑48 horas, aunque normalmente es más rápida).

### 4) Instalar `cloudflared` en el servidor Linux

Conéctate al servidor y ejecuta los siguientes comandos:

```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/cloudflared
cloudflared --version
```

Esto descarga el binario oficial, lo hace ejecutable y lo coloca en `/usr/local/bin`.

### 5) Iniciar sesión en Cloudflare desde el servidor

Autentica `cloudflared` con la cuenta que controla el dominio:

```bash
cloudflared login
```

Este comando abrirá una URL para autenticar en Cloudflare (si estás en un servidor sin navegador copia la URL y pégala en un navegador donde estés autenticado). Al terminar se generará el archivo `~/.cloudflared/cert.pem` asociado a tu cuenta.

### 6) Crear el túnel

```bash
cloudflared tunnel create mi-tunel
```

Esto creará un túnel y generará un archivo de credenciales JSON en `~/.cloudflared/` (ej. `ID_TUNEL.json`).

### 7) Preparar configuración y mover credenciales

1. Crea el directorio de configuración de `cloudflared`:

```bash
sudo mkdir -p /etc/cloudflared
```

2. Copia los archivos generados por el login y el comando `tunnel create` a `/etc/cloudflared`:

```bash
sudo cp ~/.cloudflared/cert.pem ~/.cloudflared/<ID_TUNEL>.json /etc/cloudflared/
```

3. Ajusta propietarios y permisos por seguridad:

```bash
sudo chown root:root /etc/cloudflared/*.json /etc/cloudflared/cert.pem
sudo chmod 640 /etc/cloudflared/*.json /etc/cloudflared/cert.pem
```

4. Crea el archivo de configuración `/etc/cloudflared/config.yml`:

```yaml
tunnel: mi-tunel
credentials-file: /etc/cloudflared/<ID_TUNEL>.json
origincert: /etc/cloudflared/cert.pem

ingress:
	- hostname: ssh.cteisabaneta.space
		service: ssh://localhost:22

	- service: http_status:404
```

Explicación breve:
- `tunnel` es el nombre del túnel creado.
- `credentials-file` es la ruta al archivo JSON de credenciales del túnel.
- `origincert` es el certificado de la cuenta Cloudflare.
- `ingress` define reglas que mapean hostnames (subdominios) a servicios locales (HTTP, TCP, SSH, etc.).

### 8) Instalar `cloudflared` como servicio systemd

Instala y activa el servicio:

```bash
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

Verifica el estado:

```bash
sudo systemctl status cloudflared
```

> Nota: el comando `cloudflared service install` suele crear y habilitar la unidad systemd. Si quieres personalizar la línea de ejecución (por ejemplo, incluir `--no-autoupdate` o un `--config` distinto), crea o edita la unidad systemd manualmente.

### 9) Ajustar el unit file systemd (opcional / recomendado si necesitas flags)

1. Edita `/etc/systemd/system/cloudflared.service` y cambia la línea `ExecStart` a algo como:

```
ExecStart=/usr/local/bin/cloudflared --no-autoupdate --config /etc/cloudflared/config.yml tunnel run mi-tunel
```

2. Recarga systemd y reinicia el servicio:

```bash
sudo systemctl daemon-reload
sudo systemctl restart cloudflared
sudo systemctl status cloudflared
```

### 10) Acceso SSH del administrador vía Cloudflare

Para que un administrador pueda conectarse por SSH a través del túnel sin exponer puertos públicamente, puedes usar `cloudflared access ssh`.

En la máquina cliente (administrador):

```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/
cloudflared --version
```

Añade un alias práctico en `~/.bashrc` o `~/.profile`:

```bash
# alias para conectar por SSH a través de Cloudflare Access
alias ssh-ctei='ssh -o ProxyCommand="cloudflared access ssh --hostname ssh.cteisabaneta.space" ctei@ssh.cteisabaneta.space'
```

Luego recarga tu shell (`source ~/.bashrc`) y conecta con:

```bash
ssh-ctei
```

Esto usa `cloudflared access ssh` como proxy para la conexión SSH. Es conveniente cuando quieres que la administración se haga sólo vía Cloudflare Access.

### 11) Desplegar la aplicación en el servidor

Una vez conectado por SSH al servidor on‑premise, clona o actualiza el repo y levanta tus servicios Docker:

```bash
# dentro del servidor
git clone <repo-url> ctei || (cd ctei && git pull)
cd ctei
sudo docker-compose down
sudo docker-compose up --build -d
```

Esto dejará la aplicación corriendo en los puertos locales que hayas definido (ej. `8000` para Django, `1883` para Mosquitto, etc.).

### 12) Añadir nuevos servicios al túnel (ejemplo)

Si agregas un nuevo servicio local (por ejemplo una API, un broker MQTT, etc.), actualiza `/etc/cloudflared/config.yml` añadiendo reglas `ingress` para cada subdominio:

```yaml
tunnel: mi-tunel
credentials-file: /etc/cloudflared/3a314f5b-6fd5-484d-8557-270c6cb74ccc.json
origincert: /etc/cloudflared/cert.pem

ingress:
	- hostname: ssh.cteisabaneta.space
		service: ssh://localhost:22
	- hostname: dashboard.cteisabaneta.space
		service: http://localhost:8000
	- hostname: mqtt.cteisabaneta.space
		service: tcp://localhost:1883
	- service: http_status:404
```

Después de editar el `config.yml` reinicia el servicio:

```bash
sudo systemctl restart cloudflared
sudo systemctl status cloudflared
```

## Notas de seguridad y buenas prácticas

- No publiques puertos innecesarios en el firewall del servidor; deja solo el acceso por Cloudflare Tunnel.
- Guarda `cert.pem` y el archivo de credenciales del túnel en `/etc/cloudflared` con permisos restringidos (ya indicado arriba).
- Considera usar Cloudflare Access y políticas (Teams) para controlar quién puede usar los subdominios críticos (ej. SSH, panel de administración).
- Habilita autenticación de dos factores (2FA) en la cuenta Cloudflare que gestiona el dominio.
- Si usas Docker, evita ejecutar contenedores como root y fija versiones en tus imágenes.

## Depuración y problemas comunes

- Si el túnel no levanta, revisa los logs del servicio:

```bash
sudo journalctl -u cloudflared -f
```

- Comprueba la resolución DNS del subdominio: `dig dashboard.cteisabaneta.space`.
- Asegúrate de que `cloudflared` esté autenticado y que los archivos en `/etc/cloudflared` existan y sean legibles por el servicio.
- Revisa `cloudflared tunnel list` y `cloudflared tunnel info mi-tunel` para comprobar el estado del túnel.

## Resumen rápido de comandos

```bash
# instalar cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/cloudflared

# autenticar
cloudflared login

# crear túnel
cloudflared tunnel create mi-tunel

# copiar credenciales y configurar
sudo mkdir -p /etc/cloudflared
sudo cp ~/.cloudflared/cert.pem ~/.cloudflared/<ID_TUNEL>.json /etc/cloudflared/
sudo chown root:root /etc/cloudflared/*.json /etc/cloudflared/cert.pem
sudo chmod 640 /etc/cloudflared/*.json /etc/cloudflared/cert.pem

# instalar como servicio
sudo cloudflared service install
sudo systemctl enable --now cloudflared

# revisar logs
sudo journalctl -u cloudflared -f
```
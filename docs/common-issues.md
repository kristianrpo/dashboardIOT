
# Problemas comunes y procedimientos de recuperación

Este documento agrupa los pasos más frecuentes para desplegar la aplicación en el servidor on‑premise (CTEI), y las acciones a tomar cuando alguno de los componentes críticos falla (base de datos Aiven, broker MQTT en CloudAMQP, scripts para dispositivos IoT, etc.).

> Nota importante: Las variables de entorno no se versionan. Si añadiste nuevas variables en el repositorio local o en la rama `main`, recuerda actualizarlas manualmente en el servidor (archivo `.env` en el servidor o en la configuración de los contenedores) antes de reiniciar servicios.

## 1) Flujo de despliegue rápido (push -> ssh -> pull -> docker compose)

Escenario típico: haces cambios, pusheas a `main` en GitHub, y quieres que el servidor en CTEI refleje esos cambios.

1. En tu máquina local:

```bash
git add .
git commit -m "Descripción del cambio"
git push origin main
```

2. Conéctate por SSH al servidor (usa tu alias `ssh-ctei` si lo configuraste con cloudflared):

```bash
ssh-ctei
# o ssh usuario@ip_si_acceso_directo
```

3. Dentro del servidor, ve al directorio del proyecto (`cteI` en el ejemplo) y actualiza el código:

```bash
cd ~/ctei || cd /opt/ctei  # depende dónde lo hayas clonado
git pull origin main
```

4. Comprueba si ya hay contenedores corriendo y decide la acción correcta:

```bash
docker compose ps
# si existe la pila en ejecución
sudo docker compose down
# luego (o si no existía) reconstruye y levanta
sudo docker compose up --build -d
```

Alternativa segura (evita `down` si no estás seguro):

```bash
if docker compose ps | grep -q "Up"; then
	sudo docker compose down
fi
sudo docker compose up --build -d
```

5. Después del `up`, verifica los logs para detectar errores:

```bash
sudo docker compose logs -f web   # o el servicio que te interese
sudo docker compose logs -f mqtt
```

6. Si añadiste variables de entorno nuevas, edítalas en el servidor (por ejemplo en `/opt/ctei/.env` o donde tengas el `.env`) antes de ejecutar `docker compose up`. Recuerda que las variables locales no se suben al repo remoto.

Comandos útiles adicionales

```bash
sudo docker compose exec web python manage.py migrate
sudo docker compose exec web python manage.py collectstatic --noinput
```

## 2) Base de datos remota (Aiven) — verificar y reactivar

Si la aplicación no puede conectarse a la base de datos, sigue estos pasos:

1. Inicia sesión en la consola de Aiven: https://console.aiven.io/ (o https://aiven.io/ si usas la página principal) con la cuenta que administra la instancia.
2. Verifica el estado del servicio PostgreSQL. Aiven en planes gratuitos puede desactivar instancias por inactividad; si el servicio aparece detenido o en estado `inactive`/`stopped`, actívalo desde la consola.
3. Si la instancia existe pero la aplicación no conecta:

	- Verifica las credenciales (host, puerto, db, user, password) en la consola de Aiven y compáralas con las variables en el `.env` del servidor.
	- Si las credenciales cambiaron, actualiza el `.env` en el servidor y reinicia los contenedores (`sudo docker compose restart web`).

4. Si la instancia original se ha perdido o está inaccesible y no es recuperable, crea una nueva instancia PostgreSQL desde la consola Aiven y:

	- Crea la base de datos/usuario según necesites.
	- Actualiza las variables de entorno en el servidor con los nuevos datos.
	- Ejecuta migraciones y carga datos si tienes backups:

```bash
sudo docker compose exec web python manage.py migrate
# si tienes dump
pg_restore -h <HOST> -U <USER> -d <DB> backup.dump
```

5. Monitorización: añade alertas (si Aiven lo permite) o marca en tu calendario verificar la instancia periódicamente si usas un plan gratuito que inhabilita por inactividad.

## 3) Broker MQTT (CloudAMQP / CloudAMQP / LMQ)

El proyecto usa actualmente un servicio de colas en la nube (CloudAMQP / LMQ). Para comprobarlo:

1. Entra al panel del proveedor (ej. https://customer.cloudamqp.com/login) y autentícate.
2. Verifica que la instancia/plan esté `running` y sin errores.
3. Comprueba las credenciales (host, port, user, password) y compáralas con el `.env` en el servidor.
4. Si el broker está caído o revocado, restáuralo o crea una nueva instancia y actualiza las variables en el servidor.

Comprobaciones en la aplicación

```bash
# Revisa logs del servicio que se conecta al broker
sudo docker compose logs -f web
# o el servicio responsable del mqtt
sudo docker compose logs -f mqtt
```

## 4) Scripts para IoT — localización y recuperación

Si no recuerdas dónde quedó un sketch (firmware) que se flasheó a un dispositivo ESP32, revisa la carpeta `scripts-iot/` del repositorio. Allí se pretende mantener los últimos scripts/firmwares. Pasos:

```bash
cd ~/ctei/scripts-iot
ls -la
```

Buenas prácticas

- Mantén una convención de nombres (ej. `pets_v2_2025-10-27.cpp` o `machine_2.cpp`) y un archivo `README` dentro de `scripts-iot/` con la lista de versiones y a qué dispositivo corresponde.
- Haz backups de los binarios o de los `.cpp` antes de modificarlos.

## Comprobaciones generales y troubleshooting

- Verifica contenedores corriendo:

```bash
sudo docker ps
sudo docker compose ps
```

- Logs en tiempo real:

```bash
sudo docker compose logs -f
sudo journalctl -u cloudflared -f  # si usas cloudflared
```

- Falló la migración o hay errores Django: inspecciona `web` logs y ejecuta `python manage.py migrate` manualmente dentro del contenedor.

- Si sospechas variables de entorno faltantes: compara `.env.example` con el `.env` en el servidor:

```bash
diff .env.example .env || true
```

## Checklist rápido para emergencias

1. ¿El código en `main` está actualizado? `git pull` en servidor.
2. ¿Contenedores arriba? `docker compose ps`.
3. ¿Logs con errores? `docker compose logs -f`.
4. ¿BD accesible? Entrar a Aiven y activar/chequear credenciales.
5. ¿MQTT activo? Entrar al panel CloudAMQP y verificar.
6. ¿Confías en los scripts IoT? Revisa `scripts-iot/` y copia de seguridad.

## Recomendaciones finales

- Mantén un archivo `DEPLOY.md` o un `Makefile` con los pasos de despliegue usados (push, ssh, pull, up). Esto reduce errores humanos.
- Registra cambios en variables de entorno en un `ENV_CHANGES.md` que explique qué variables se agregaron y qué deben modificarse en el servidor.
- Automatiza el deploy con GitHub Actions + un job que haga SSH al servidor y ejecute los comandos de despliegue si confías en el flujo; si no, sigue con el proceso manual descrito arriba.



# Dashboard IOT — Documentación general

Este documento explica la arquitectura general del proyecto "dashboardIOT", cómo instalarlo, las variables de entorno necesarias (tomadas de `.env.example`), la configuración para PostgreSQL y cómo correr la aplicación en desarrollo y producción.

## Resumen

`dashboardIOT` es una aplicación Django que ofrece un panel para gestionar dispositivos IoT (basado en carpetas como `pets`, `garbage`, `orchards`) y expone algunos endpoints API (vía `api/`) para acciones como dispensar comida. El repositorio incluye código para el frontend (templates), lógica de apps Django y scripts relacionados con los dispositivos (carpeta `scripts-iot`).

Principales carpetas y su responsabilidad

- `dashboardIOT/` — Configuración del proyecto Django (settings, urls, wsgi/asgi). Aquí está la configuración global del proyecto.
- `pets/`, `garbage/`, `orchards/` — Aplicaciones Django por dominio. Cada app contiene `models.py`, `views.py`, `urls.py`, `templates/` y `migrations/` cuando aplica. Son el lugar para la lógica específica de cada dominio.
- `api/` — Endpoints REST (o handlers) que sirven para comunicación con dispositivos o para acciones consumidas por el frontend. Contiene `serializers/` y `endpoints/`.
- `templates/` y `static/` — Recursos de frontend (HTML Jinja/Django, CSS, JS, imágenes). En las apps a menudo hay carpetas `templates/<app_name>/` con sus vistas.
- `scripts-iot/` — Código fuente C++/Arduino/ESP para los dispositivos (ESP32) que se despliegan a los dispositivos físicos.
- `docs/` — Documentación del proyecto (este archivo y otros).
- `manage.py`, `Dockerfile`, `docker-compose.yml` — Scripts y definiciones para desarrollo, construcción y despliegue.

## Arquitectura y flujo de datos

1. Dispositivos IoT (ESP32) ejecutan firmware ubicado en `scripts-iot/` y se comunican con el backend mediante MQTT para enviar/recibir comandos y telemetría.
2. El backend Django expone endpoints de administración y vistas web para usuarios, y suscribe/publica a topics MQTT para comunicación con los dispositivos (configuración MQTT en variables de entorno).
3. PostgreSQL se usa como base de datos relacional para persistir usuarios, configuraciones, logs y estados de máquinas.
4. El frontend (templates + static) consume los endpoints Web/API para mostrar el estado y permitir acciones (por ejemplo: dispensar porciones desde la UI que luego genera mensajes MQTT).

Diagrama lógico (simplificado)

Client (browser)
	↕ HTTP/HTTPS
Django (views + api)
	↕ MQTT
MQTT broker (configurado vía env)
	↕
ESP32 devices (scripts-iot)

Persistencia: Django ↔ PostgreSQL

## Requisitos previos

- Python 3.10+ (o la versión usada en el proyecto)
- PostgreSQL (local o remoto)
- Node/npm solo si vas a compilar assets (opcional, si se usan herramientas frontend)
- Docker y docker-compose (opcional, recomendado para desarrollo reproducible)

## Variables de entorno

Se usa un archivo `.env` (no incluido en el repo). Revisa `.env.example` y crea tu `.env` con los valores apropiados.

Variables encontradas en `.env.example`:

- `SECRET_KEY` — Clave secreta de Django. Obligatoria en producción.
- `DEBUG` — `True`/`False`. En desarrollo `True`.
- `ALLOWED_HOSTS` — Hosts permitidos, separados por comas.

- PostgreSQL
	- `POSTGRES_DB` — Nombre de la base de datos.
	- `POSTGRES_USER` — Usuario de la BD.
	- `POSTGRES_PASSWORD` — Password del usuario.
	- `POSTGRES_HOST` — Host de la BD (ej. `localhost` o `db` si usas docker-compose).
	- `POSTGRES_PORT` — Puerto (ej. `5432`).

- Aplicación y MQTT
	- `APPLICATION_URL` — URL base de la aplicación.
	- `MQTT_BROKER` — Host del broker MQTT.
	- `MQTT_PORT` — Puerto del broker (normalmente `1883` o `8883` para TLS).
	- `MQTT_USER` — Usuario MQTT (si aplica).
	- `MQTT_PASSWORD` — Password MQTT (si aplica).
	- `DJANGO_SETTINGS_MODULE` — Módulo de settings (ej. `dashboardIOT.settings`).

- Otros
	- `TOTAL_HEIGHT_GARBAGE`, `RUN_MAIN` — Variables propias del proyecto (usar valores apropiados o dejar en blanco en desarrollo).

Importante
- No subas tu `.env` a repositorios públicos.
- Para Docker, `docker-compose.yml` puede leer estas variables desde un fichero `.env` o puedes inyectarlas en el servicio `environment`.

## Instalación y ejecución (modo desarrollo)

Opción A — Usando Python localmente

1. Clona el repositorio y sitúate en la carpeta del proyecto:

```bash
git clone <repo-url>
cd ctei
```

2. Crea un entorno virtual e instala dependencias:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Crea un archivo `.env` basado en `.env.example` y completa las variables (ver sección anterior). Ejemplo mínimo para desarrollo con PostgreSQL local:

```ini
SECRET_KEY=dev-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB=dashboard
POSTGRES_USER=dashboard_user
POSTGRES_PASSWORD=dashboard_pass
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
APPLICATION_URL=http://localhost:8000
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USER=
MQTT_PASSWORD=
DJANGO_SETTINGS_MODULE=dashboardIOT.settings
```

4. Crea la base de datos PostgreSQL y el usuario (si no existe). Ejemplos rápidos:

```bash
# En Linux con psql
sudo -u postgres psql
CREATE DATABASE dashboard;
CREATE USER dashboard_user WITH ENCRYPTED PASSWORD 'dashboard_pass';
GRANT ALL PRIVILEGES ON DATABASE dashboard TO dashboard_user;
\q
```

5. Aplica migraciones y carga datos iniciales (si aplica):

```bash
python manage.py migrate
# opcional: python manage.py loaddata initial_data.json
python manage.py createsuperuser
```

6. Ejecuta el servidor de desarrollo:

```bash
python manage.py runserver
```

Visita `http://localhost:8000`.

Opción B — Usando Docker Compose (recomendado y usado para el dpeloyment on-premise sobre el servidor del CTEI)

1. Asegúrate de tener Docker y docker-compose instalados.
2. Crea `.env` o adapta `docker-compose.yml` para que las variables de entorno estén disponibles a los servicios.
3. Levanta los servicios:

```bash
docker-compose up --build
```

4. Ejecuta migraciones dentro del contenedor (si no está automatizado):

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

5. Accede al servicio en la URL definida (ej. `http://localhost:8000`).

## Configuración y uso de PostgreSQL

- Si usas una instalación local, crea la base de datos y el usuario con `psql` (ver comandos arriba).
- Si usas Docker, el servicio `db` en `docker-compose.yml` puede usar la imagen oficial `postgres` y tomar `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` desde variables de entorno.
- Verifica que `dashboardIOT/settings.py` o el loader de configuración lea la variable `DATABASE_URL` o construya la configuración de base de datos a partir de `POSTGRES_*`.
- Para conexiones remotas, asegúrate de configurar `pg_hba.conf` y el firewall adecuadamente.

Backup y restauración

- Dump:

```bash
pg_dump -U dashboard_user -h localhost -d dashboard -F c -f backup.dump
```

- Restore:

```bash
pg_restore -U dashboard_user -h localhost -d dashboard -c backup.dump
```

## MQTT

- Define `MQTT_BROKER`, `MQTT_PORT`, `MQTT_USER` y `MQTT_PASSWORD` en tu `.env`.
- Asegúrate de tener un broker MQTT accesible (p. ej. Mosquitto, EMQX o un broker cloud).
- El backend Django u otro componente debe conectarse al broker con estas credenciales para publicar/subscribir a topics (por ejemplo `pets/dispense`).



## Estructura recomendada de cada aplicación (`pets`, `garbage`, `orchards`)

- `apps.py` — Configuración del app.
- `models.py` — Modelos de la base de datos.
- `admin.py` — Registro de modelos para admin.
- `views.py` — Vistas basadas en clases o funciones.
- `urls.py` — Ruteo de la app (incluir desde `dashboardIOT/urls.py`).
- `templates/<app_name>/` — Templates HTML específicos de la app.
- `static/<app_name>/` — Archivos estáticos (js, css, img) específicos.
- `migrations/` — Migraciones de la BD.
- `serializers/` Serializadores para APIs.




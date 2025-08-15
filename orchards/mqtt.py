import threading
import json
import paho.mqtt.client as mqtt
from datetime import timedelta
from django.utils import timezone
from .models import Orchard, WeeklyValue

MQTT_BROKER = "jaragua-01.lmq.cloudamqp.com"
MQTT_PORT = 1883
MQTT_TOPIC = "huerta"
MQTT_USER = "kufvoati:kufvoati"
MQTT_PASSWORD = "U80l2J0lRbj84BceoCF0lYVRdPe_a9rD"

def store_daily_average(statistic, new_value):
    today = timezone.now().date()
    daily_value, created = WeeklyValue.objects.get_or_create(
        statistic=statistic,
        day=today,
        defaults={'value': new_value}
    )

    if not created:
        # Promedio simple entre valor existente y nuevo valor
        daily_value.value = (daily_value.value + new_value) / 2
        daily_value.save()

    # Eliminar datos de hace más de 7 días
    cutoff_date = today - timedelta(days=7)
    WeeklyValue.objects.filter(statistic=statistic, day__lt=cutoff_date).delete()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Conectado a MQTT")
        client.subscribe(MQTT_TOPIC)
        print(f"🟢 Suscrito al tópico: {MQTT_TOPIC}")
    else:
        print(f"❌ Fallo en la conexión MQTT. Código: {rc}")

def on_message(client, userdata, msg):
    print(f"\n📩 Mensaje recibido en el tópico: {msg.topic}")
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)

        orchard_id = data.get("id")
        temperature = data.get("temperature")
        air_humidity = data.get("air_humidity")
        soil_moisture = data.get("soil_moisture")
        pump_state = data.get("pump_state")

        if orchard_id:
            try:
                orchard = Orchard.objects.get(id=orchard_id)
            except Orchard.DoesNotExist:
                print(f"🌱 Huerta con ID {orchard_id} no encontrada.")
                return

            stats = list(orchard.statistics.all().order_by('id'))

            if len(stats) >= 3:
                stats[0].value = soil_moisture
                stats[1].value = air_humidity
                stats[2].value = temperature

                for i, stat in enumerate(stats[:3]):
                    stat.save()
                    if i == 0:
                        store_daily_average(stat, soil_moisture)
                    elif i == 1:
                        store_daily_average(stat, air_humidity)
                    elif i == 2:
                        store_daily_average(stat, temperature)

                orchard.status = pump_state
                orchard.save()

                print(f"✅ Estadísticas y estado actualizados para la huerta {orchard.name}")
            else:
                print("⚠️ No hay suficientes estadísticas creadas para esta huerta.")

    except json.JSONDecodeError:
        print("❌ Error al decodificar el mensaje JSON.")
    except Exception as e:
        print(f"❌ Error general en on_message: {e}")

def start_mqtt():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    thread = threading.Thread(target=client.loop_forever)
    thread.daemon = True
    thread.start()

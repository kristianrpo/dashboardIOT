from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from decouple import config
import requests
from pets.models import PetMachine
from api.serializers.pets import PetMachineSerializer
from dashboardIOT.settings import MQTT_BROKER, MQTT_PORT, MQTT_USER, MQTT_PASSWORD
import paho.mqtt.client as mqtt
import json

@api_view(['GET'])
def get(request):
    try:
        machines = PetMachine.objects.all()
        serializer = PetMachineSerializer(machines, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    except requests.RequestException as e:
        return Response({"message": f"No se pudo conectar con el ESP32: {e}", "is_success": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['get'])
def dispense(request):
    try:
        params = {"id": request.GET.get("id", None)}
        pet_machine = PetMachine.objects.filter(id=params["id"]).first()
        pet_machine.dispense_count += 1
        pet_machine.save()

        MQTT_TOPIC = f"pets/dispense"
        message = {"id": params["id"], "rotations": pet_machine.portion_size}
        message_json = json.dumps(message)
        client = mqtt.Client()
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.publish(MQTT_TOPIC, message_json)
        client.disconnect()

        print(params)
        print(MQTT_TOPIC)
        print(message)
        print(MQTT_BROKER)
        print(MQTT_PORT)
        print(MQTT_USER)
        print(MQTT_PASSWORD)

        return Response({"message": f"La máquina {params['id']} recibió la tarea correctamente", "is_success": True}, status=status.HTTP_200_OK)
    except requests.RequestException as e:
        response_message = ""
        return Response({"message": f"No se pudo conectar con el ESP32: {e}", "is_success": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['PATCH'])
def update(request):
    try:
        payload = {
            "type": request.data.get("type"),
            "id": request.data.get("id"),
            "portion_size": request.data.get("portion_size"),
            "automatic_start_date": request.data.get("automatic_start_date"),
            "automatic_end_date": request.data.get("automatic_end_date"),
        }

        PetMachine.objects.filter(id=payload["id"]).update(
            type=payload["type"],
            portion_size=payload["portion_size"],
            automatic_start_date=payload["automatic_start_date"],
            automatic_end_date=payload["automatic_end_date"]
        )

        return Response({
            "message": f"La máquina {payload['id']} fue actualizada correctamente",
            "is_success": True
        }, status=status.HTTP_200_OK)

    except requests.RequestException as e:
        return Response({
            "message": f"No se pudo conectar con el ESP32: {e}",
            "is_success": False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from decouple import config
import requests
from pets.models import PetMachine, ScheduledTask
from api.serializers.pets import PetMachineSerializer, ScheduledTaskSerializer, PetMachineDetailSerializer
from dashboardIOT.settings import MQTT_BROKER, MQTT_PORT, MQTT_USER, MQTT_PASSWORD
import paho.mqtt.client as mqtt
import json
from django.utils import timezone
from datetime import datetime
import pytz

@api_view(['GET'])
def get(request):
    try:
        machines = PetMachine.objects.all()
        
        for machine in machines:
            if machine.last_refill:
                local_time = timezone.localtime(machine.last_refill)
                machine.last_refill = local_time.strftime("%d-%m-%Y %H:%M:%S")
            if machine.next_refill:
                next_refill = machine.next_refill
                if isinstance(next_refill, datetime):
                    local_time = timezone.localtime(next_refill)
                    machine.next_refill = local_time.strftime("%d-%m-%Y %H:%M:%S")
                else:
                    machine.next_refill = None
            else:
                machine.last_refill = None
        serializer = PetMachineSerializer(machines, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    except requests.RequestException as e:
        return Response({"message": f"Error al conectar con la base de datos: {e}", "is_success": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def get_by_id(request, machine_id):
    try:
        pet_machine = PetMachine.objects.filter(id=machine_id).first()
        if not pet_machine:
            return Response({"message": "Máquina no encontrada", "is_success": False}, status=status.HTTP_404_NOT_FOUND)

        serializer = PetMachineDetailSerializer(pet_machine)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except requests.RequestException as e:
        return Response({"message": f"Error al conectar con la base de datos: {e}", "is_success": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
def dispense(request):
    try:
        params = {"id": request.GET.get("id", None)}
        pet_machine = PetMachine.objects.filter(id=params["id"]).first()
        
        pet_machine.dispense_count += 1

        pet_machine.last_refill = timezone.now()
        pet_machine.save()

        MQTT_TOPIC = f"pets/dispense"
        message = {"id": params["id"], "rotations": pet_machine.portion_size}
        message_json = json.dumps(message)
        client = mqtt.Client()
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.publish(MQTT_TOPIC, message_json)
        client.disconnect()

        return Response({"message": f"La máquina {params['id']} recibió la tarea correctamente", "is_success": True}, status=status.HTTP_200_OK)
    except requests.RequestException as e:
        return Response({"message": f"No se pudo conectar con el ESP32: {e}", "is_success": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['PATCH'])
def update(request):
    try:
        payload = {
            "id": request.data.get("id"),
            "portion_size": request.data.get("portion_size")
        }

        PetMachine.objects.filter(id=payload["id"]).update(
            portion_size=payload["portion_size"],
        )

        return Response({
            "message": f"La máquina {payload['id']} fue actualizada correctamente",
            "is_success": True
        }, status=status.HTTP_200_OK)

    except requests.RequestException as e:
        return Response({
            "message": f"Error al conectar con la base de datos: {e}",
            "is_success": False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def add_schedule_task(request):
    machine_id = request.data.get("machine_id")
    try:
        machine = PetMachine.objects.get(id=machine_id)
    except PetMachine.DoesNotExist:
        print(f"Máquina con ID {machine_id} no encontrada")
        return Response(
            {"message": "Máquina no encontrada"},
            status=status.HTTP_404_NOT_FOUND
        )

    data = request.data.copy()
    data["machine"] = machine.id

    serializer = ScheduledTaskSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        machine.update_next_refill()
        return Response(
            {"message": "Tarea programada guardada correctamente", "task": serializer.data},
            status=status.HTTP_201_CREATED
        )
    else:
        return Response(
            {"message": "Error de validación", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
@api_view(['GET'])
def get_scheduled_tasks(request):
    try:
        machine_id = request.GET.get("machine_id", None)
        if not machine_id:
            return Response({"message": "ID de máquina no proporcionado"}, status=status.HTTP_400_BAD_REQUEST)
        
        tasks = PetMachine.objects.get(id=machine_id).scheduled_tasks.all()
        machine = PetMachine.objects.get(id=machine_id)
        if not tasks:
            tasks = ScheduledTask.objects.none()
            machine.next_refill = None
            machine.save()
            
        
        serializer = ScheduledTaskSerializer(tasks, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    except PetMachine.DoesNotExist:
        return Response({"message": "Máquina no encontrada"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error al obtener tareas programadas: {e}")
        return Response({"message": "Error al obtener tareas programadas"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['DELETE'])
def delete_schedule_task(request, task_id):
    try:
        task = ScheduledTask.objects.filter(id=task_id).first()
        if not task:
            return Response(
                {"message": "Tarea programada no encontrada", "is_success": False},
                status=status.HTTP_404_NOT_FOUND
            )

        task.delete()
        return Response(
            {"message": "Tarea programada eliminada correctamente", "is_success": True},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"message": f"Error al eliminar la tarea programada: {e}", "is_success": False},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
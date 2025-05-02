from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from decouple import config
import requests
from dashboardIOT.constants import ENDPOINTS
@api_view(['GET'])
def get(request):
    try:
        esp32_url = config('ESP32_URL', default = "")
        endpoint = ENDPOINTS["pets"]["food-machines"]
        
        response = requests.get(esp32_url + endpoint)
        response.raise_for_status()
        machines = response.json()

        return Response(machines, status=status.HTTP_200_OK)
    except requests.RequestException as e:
        return Response({"message": f"No se pudo conectar con el ESP32: {e}", "is_success": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['get'])
def dispense(request):
    try:
        esp32_url = config('ESP32_URL', default = "")
        endpoint = ENDPOINTS["pets"]["dispense"]
        params = {"id": request.GET.get("id", None)}
        response = requests.get(esp32_url + endpoint, params=params)
        response.raise_for_status()
        return Response({"message": f"La máquina {params['id']} dispensó correctamente", "is_success": True}, status=status.HTTP_200_OK)
    except requests.RequestException as e:
        response_message = ""
        return Response({"message": f"No se pudo conectar con el ESP32: {e}", "is_success": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['PATCH'])
def update(request):
    try:
        esp32_url = config('ESP32_URL', default="")
        endpoint = ENDPOINTS["pets"]["update-machine"]

        payload = {
            "type": request.data.get("type"),
            "id": request.data.get("id"),
            "portion_size": request.data.get("portion_size"),
            "automatic_start_date": request.data.get("automatic_start_date"),
            "automatic_end_date": request.data.get("automatic_end_date"),
        }

        response = requests.patch(esp32_url + endpoint, json=payload)
        response.raise_for_status()

        return Response({
            "message": f"La máquina {payload['id']} fue actualizada correctamente",
            "is_success": True
        }, status=status.HTTP_200_OK)

    except requests.RequestException as e:
        return Response({
            "message": f"No se pudo conectar con el ESP32: {e}",
            "is_success": False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

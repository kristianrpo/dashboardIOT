from django.shortcuts import render
from .utils import format_date
from django.shortcuts import render
from django.urls import reverse
import requests
from decouple import config
def index(request):
    template_data = {}
    template_data["title"] = "Dashboard de máquina de cómidas - 4 elementos Sabaneta"

    response = requests.get(config('APPLICATION_URL', default = "") + reverse("api.pets.get"),None)
    if response.status_code == 200:
        machines = response.json()
    else:
        template_data["is_success"] = response.json().get("is_success", False)
        template_data["message"] = response.json().get("message", "No se pudo conectar con el ESP32")

    for machine in machines:
        machine["next_refill"] = format_date(machine["next_refill"])
        machine["last_refill"] = format_date(machine["last_refill"])
        machine["automatic_start_date"] = format_date(machine["automatic_start_date"])
        machine["automatic_end_date"] = format_date(machine["automatic_end_date"])
    
    
    type_filter = request.GET.get('type', None)
    if type_filter:
        machines = [machine for machine in machines if machine['type'] == type_filter]

    template_data["machines"] = machines
    return render(request, "pets/index.html", {"template_data": template_data})

def edit(request):
    template_data = {}
    template_data["title"] = "Configuración de máquinas - 4 elementos Sabaneta"

    return render(request, "pets/edit.html", {"template_data": template_data})
    
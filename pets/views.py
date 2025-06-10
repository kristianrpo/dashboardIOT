from django.shortcuts import render
from django.urls import reverse
from decouple import config
from .forms import ScheduledTaskForm
import requests

def index(request):
    template_data = {}
    template_data["title"] = "Dashboard de máquina de cómida para mascotas - 4 elementos Sabaneta"

    response = requests.get(config('APPLICATION_URL', default = "") + reverse("api.pets.get"),None)
    if response.status_code == 200:
        machines = response.json()
    else:
        template_data["is_success"] = response.json().get("is_success", False)
        template_data["message"] = response.json().get("message", "No se pudo conectar con el ESP32")

    template_data["machines"] = machines
    return render(request, "pets/index.html", {"template_data": template_data})

def edit(request, machine_id):
    template_data = {}
    template_data["title"] = "Configuración de máquinas - 4 elementos Sabaneta"

    response = requests.get(config('APPLICATION_URL', default = "") + reverse("api.pets.get_by_id", args=[machine_id]), None)
    if response.status_code == 200:
        machine = response.json()
    else:
        template_data["is_success"] = response.json().get("is_success", False)
        template_data["message"] = response.json().get("message", "No se pudo conectar con el ESP32")

    template_data["machine"] = machine
    template_data["tasks"] = machine.get("scheduled_tasks", [])

    form = ScheduledTaskForm()
    template_data["form"] = form

    return render(request, "pets/edit.html", {"template_data": template_data})

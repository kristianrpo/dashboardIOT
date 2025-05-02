from django.shortcuts import render
from decouple import config
from .utils import format_date
from django.shortcuts import render

def index(request):
    template_data = {}
    template_data["title"] = "Dashboard de máquina de cómidas - 4 elementos Sabaneta"
    machines = [
    {
        "type": "Perros",
        "number": 1,
        "next_refill": "2023-10-01T12:00:00Z",
        "last_refill": "2023-09-01T12:00:00Z",
        "automatic_start_date": "2023-09-01T08:00:00Z",
        "automatic_end_date": "2023-09-30T08:00:00Z",
        "dispense_count": 0,
        "portion_size": 200,
        "no_food": False 
    },
    {
        "type": "Gatos",
        "number": 1,
        "next_refill": "2023-10-01T12:00:00Z",
        "last_refill": "2023-09-01T12:00:00Z",
        "automatic_start_date": "2023-09-01T08:00:00Z",
        "automatic_end_date": "2023-09-30T08:00:00Z",
        "dispense_count": 0,
        "portion_size": 150,
        "no_food": True  
    },
    {
        "type": "Perros",
        "number": 2,
        "next_refill": "2023-10-01T12:00:00Z",
        "last_refill": "2023-09-01T12:00:00Z",
        "automatic_start_date": "2023-09-01T08:00:00Z",
        "automatic_end_date": "2023-09-30T08:00:00Z",
        "dispense_count": 0,
        "portion_size": 200,
        "no_food": False 
    },
    {
        "type": "Gatos",
        "number": 2,
        "next_refill": "2023-10-01T12:00:00Z",
        "last_refill": "2023-09-01T12:00:00Z",
        "automatic_start_date": "2023-09-01T08:00:00Z",
        "automatic_end_date": "2023-09-30T08:00:00Z",
        "dispense_count": 0,
        "portion_size": 150,
        "no_food": True 
    },
    {
        "type": "Perros",
        "number": 3,
        "next_refill": "2023-10-01T12:00:00Z",
        "last_refill": "2023-09-01T12:00:00Z",
        "automatic_start_date": "2023-09-01T08:00:00Z",
        "automatic_end_date": "2023-09-30T08:00:00Z",
        "dispense_count": 0,
        "portion_size": 200,
        "no_food": False
    },
    {
        "type": "Gatos",
        "number": 3,
        "next_refill": "2023-10-01T12:00:00Z",
        "last_refill": "2023-09-01T12:00:00Z",
        "automatic_start_date": "2023-09-01T08:00:00Z",
        "automatic_end_date": "2023-09-30T08:00:00Z",
        "dispense_count": 0,
        "portion_size": 150,
        "no_food": True 
    },
    {
        "type": "Perros",
        "number": 4,
        "next_refill": "2023-10-01T12:00:00Z",
        "last_refill": "2023-09-01T12:00:00Z",
        "automatic_start_date": "2023-09-01T08:00:00Z",
        "automatic_end_date": "2023-09-30T08:00:00Z",
        "dispense_count": 0,
        "portion_size": 200,
        "no_food": False
    },
    {
        "type": "Gatos",
        "number": 4,
        "next_refill": "2023-10-01T12:00:00Z",
        "last_refill": "2023-09-01T12:00:00Z",
        "automatic_start_date": "2023-09-01T08:00:00Z",
        "automatic_end_date": "2023-09-30T08:00:00Z",
        "dispense_count": 0,
        "portion_size": 150,
        "no_food": True
    }
]


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
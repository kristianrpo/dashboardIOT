from django.shortcuts import render
from decouple import config

def index(request):
    template_data = {}
    template_data["title"] = "Dashboard ECOZONA - 4 elementos Sabaneta"
    garbage_info = [{"title": "RAAE","fill_name": "raae"},{"title": "TAPAS DE PLÁSTICO","fill_name": "caps"},{"title": "LUMINARIAS","fill_name": "luminaires"}, {"title": "PILAS Y BATERÍAS","fill_name": "batteries"}, {"title": "MEDICAMENTOS","fill_name": "medicines"}, {"title": "ACEITES","fill_name": "oils"}]
    
    template_data["garbage_info"] = garbage_info
    template_data["total_height_garbage"] = config("TOTAL_HEIGHT_GARBAGE", default = 100)
    return render(request, "garbage/index.html", {"template_data": template_data})
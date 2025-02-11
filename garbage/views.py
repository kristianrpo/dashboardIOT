from django.shortcuts import render
def index(request):
    template_data = {}
    template_data["title"] = "Dashboard ECOZONA - 4 elementos Sabaneta"
    garbage = {"RAAE": "raae","TAPAS DE PLÁSTICO":"caps","LUMINARIAS":"luminaires","PILAS Y BATERÍAS":"batteries","MEDICAMENTOS": "medicines","ACEITES": "oils"}
    template_data["garbage"] = garbage
    return render(request, "garbage/index.html", {"template_data": template_data})
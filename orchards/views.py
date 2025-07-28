from django.shortcuts import render
from .models import Orchard
from datetime import datetime, timedelta

def index(request):
    orchards = Orchard.objects.prefetch_related('statistics__type', 'statistics__weekly_values')

    data = {
        "title": "Dashboard de Huertas - CTEI Sabaneta",
        "orchards": []
    }

    for orchard in orchards:
        orchard_data = {
            "name": orchard.name,
            "status": orchard.status,
            "last_updated": orchard.last_updated.strftime("%d/%m/%Y %H:%M:%S"),
            "statistics": []
        }

        for stat in orchard.statistics.all():
            weekly = {val.day: val.value for val in stat.weekly_values.all()}
            
            if stat.type.name == "Temperatura":
                temp_heights = {}
                for day, value in weekly.items():
                    height_transformed = (value / 40) * 100
                    temp_heights[day] = [int(height_transformed), value]
                weekly_heights = temp_heights
            else:
                weekly_heights = weekly
            
            for element in weekly:
                if weekly[element] is None:
                    weekly[element] = 0
                else:
                    weekly[element] = int(weekly[element])

            stat_data = {
                "name": stat.type.name,
                "value": stat.value,
                "unit": stat.type.unit,
                "state": stat.state,
                "message_state": stat.message_state,
                "weekly_values": weekly,
                "weekly_heights": weekly_heights,
                "image": stat.type.image.url if hasattr(stat.type.image, 'url') else stat.type.image
            }

            orchard_data["statistics"].append(stat_data)

        data["orchards"].append(orchard_data)

    return render(request, "orchards/index.html", {"template_data": data})

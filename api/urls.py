from django.urls import path
from .endpoints.garbage import save as save_garbage
from .endpoints.garbage import get as get_garbage
from .endpoints.pets import get as get_pet_machines
from .endpoints.pets import get_by_id as get_pet_machine_by_id
from .endpoints.pets import dispense as dispense_pet_machine
from .endpoints.pets import update as update_pet_machine
from .endpoints.pets import add_schedule_task
from .endpoints.pets import get_scheduled_tasks

urlpatterns = [
    path('garbage/save/', save_garbage, name="api.garbage.save"),
    path('garbage/get/', get_garbage, name="api.garbage.get"),
    path('pets/get/', get_pet_machines, name="api.pets.get"),
    path('api/pets/<int:machine_id>/', get_pet_machine_by_id, name="api.pets.get_by_id"),
    path('pets/dispense/', dispense_pet_machine, name="api.pets.dispense"),
    path('pets/update/', update_pet_machine, name="api.pets.update"),
    path('pets/add_schedule/', add_schedule_task, name="api.pets.add_schedule"),
    path('pets/get_tasks/', get_scheduled_tasks, name="api.pets.get_tasks"),
]
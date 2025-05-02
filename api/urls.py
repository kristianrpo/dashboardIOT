from django.urls import path
from .endpoints.garbage import save as save_garbage
from .endpoints.garbage import get as get_garbage
from .endpoints.pets import get as get_pets
from .endpoints.pets import dispense as dispense_pets
from .endpoints.pets import update as update_pets
urlpatterns = [
    path('garbage/save/', save_garbage, name="api.garbage.save"),
    path('garbage/get/', get_garbage, name="api.garbage.get"),
    path('pets/get/', get_pets, name="api.pets.get"),
    path('pets/dispense/', dispense_pets, name="api.pets.dispense"),
    path('pets/update/', update_pets, name="api.pets.update"),
]
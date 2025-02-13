from django.urls import path
from .endpoints.garbage import save, get

urlpatterns = [
    path('garbage/save/', save, name="api.garbage.save"),
    path('garbage/get/', get, name="api.garbage.get"),
]
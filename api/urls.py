from django.urls import path
from .endpoints.garbage import save_garbage_data,get_garbage_data

urlpatterns = [
    path('save-garbage-data/', save_garbage_data),
    path('get-garbage-data/', get_garbage_data),

]
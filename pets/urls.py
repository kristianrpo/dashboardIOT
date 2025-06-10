from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name="pets.index"),
    path('edit/<int:machine_id>/', views.edit, name="pets.edit"),
]

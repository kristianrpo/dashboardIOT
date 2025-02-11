from rest_framework import serializers
from garbage.models import Garbage
class GarbageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Garbage
        fields = ['raae_distance', 'caps_distance', 'luminaires_distance', 'batteries_distance', 'medicines_distance', 'oil_distance']
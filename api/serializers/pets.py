from rest_framework import serializers
from pets.models import PetMachine

class PetMachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetMachine
        fields = ['id', 'type', 'next_refill', 'last_refill', 'automatic_start_date', 'automatic_end_date', 'dispense_count', 'portion_size', 'no_food']
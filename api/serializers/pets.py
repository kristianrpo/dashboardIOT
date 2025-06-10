from rest_framework import serializers
from pets.models import PetMachine, ScheduledTask
class PetMachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetMachine
        fields = ['id', 'next_refill', 'last_refill', 'dispense_count', 'portion_size', 'no_food']

class ScheduledTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledTask
        fields = '__all__'

class PetMachineDetailSerializer(serializers.ModelSerializer):
    scheduled_tasks = ScheduledTaskSerializer(many=True)

    class Meta:
        model = PetMachine
        fields = ['id', 'next_refill', 'last_refill', 'dispense_count', 'portion_size', 'no_food', 'scheduled_tasks']
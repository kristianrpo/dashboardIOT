from django.db import models

DAYS_OF_WEEK = [
    ('Lunes', 'Lunes'),
    ('Martes', 'Martes'),
    ('Miércoles', 'Miércoles'),
    ('Jueves', 'Jueves'),
    ('Viernes', 'Viernes'),
    ('Sábados', 'Sábados'),
    ('Domingos', 'Domingos'),
]

SCHEDULE_TYPES = [
    ('Una vez', 'Una vez'),
    ('Semanal', 'Semanal'),
    ('Diario', 'Diario'),
]


class PetMachine(models.Model):
    id = models.AutoField(primary_key=True)
    next_refill = models.DateTimeField()
    last_refill = models.DateTimeField()
    dispense_count = models.IntegerField()
    portion_size = models.IntegerField()
    no_food = models.BooleanField(default=False)

class ScheduledTask(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPES, null=True, blank=True)
    day_of_week = models.CharField(max_length=9, choices=DAYS_OF_WEEK, blank=True, null=True)
    hour = models.IntegerField(null=True, blank=True)
    minute = models.IntegerField(null=True, blank=True)
    date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    machine = models.ForeignKey(PetMachine, on_delete=models.CASCADE, related_name='scheduled_tasks')



from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta

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
    next_refill = models.DateTimeField(null=True, blank=True)
    last_refill = models.DateTimeField(null=True, blank=True)
    dispense_count = models.IntegerField()
    portion_size = models.IntegerField()
    no_food = models.BooleanField(default=False)

    def update_next_refill(self):
        now = timezone.localtime(timezone.now())
        next_executions = []
        
        for task in self.scheduled_tasks.all():
            next_exec = task.calculate_next_execution()
            if next_exec and next_exec > now:
                next_executions.append(next_exec)
        
        if next_executions:
            self.next_refill = min(next_executions)
            self.save()
        else:
            self.next_refill = None
            self.save()

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
    last_executed_at = models.DateTimeField(null=True, blank=True)

    def calculate_next_execution(self):
        now = timezone.localtime(timezone.now())
        
        if self.schedule_type == 'Una vez':
            execution_date = datetime.combine(self.date, datetime.min.time()).replace(
                hour=self.hour, 
                minute=self.minute
            )
            execution_date = timezone.make_aware(execution_date)
            return execution_date if execution_date > now else None
        
        elif self.schedule_type == 'Diario':
            today_execution = now.replace(hour=self.hour, minute=self.minute, second=0, microsecond=0)
            return today_execution if today_execution > now else today_execution + timedelta(days=1)
        
        elif self.schedule_type == 'Semanal':
            days_map = {'Lunes': 0, 'Martes': 1, 'Miércoles': 2, 'Jueves': 3,
                       'Viernes': 4, 'Sábados': 5, 'Domingos': 6}
            target_weekday = days_map[self.day_of_week]
            today_execution = now.replace(hour=self.hour, minute=self.minute, second=0, microsecond=0)
            current_weekday = now.weekday()
            
            if target_weekday > current_weekday:
                delta = target_weekday - current_weekday
            elif target_weekday == current_weekday:
                delta = 0 if today_execution > now else 7
            else:
                delta = 7 - (current_weekday - target_weekday)
            
            return today_execution + timedelta(days=delta)
        
        return None


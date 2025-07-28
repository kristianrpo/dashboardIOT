from django.db import models

class Orchard(models.Model):
    name = models.CharField(max_length=100)
    status = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class StatisticType(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=10)
    image = models.ImageField(upload_to='statistics_images/')
    def __str__(self):
        return self.name

class Statistic(models.Model):
    STATE_CHOICES = [
        ('optimal', 'Óptima'),
        ('warning', 'Baja'),
        ('critical', 'Crítica'),
    ]

    orchard = models.ForeignKey(Orchard, on_delete=models.CASCADE, related_name='statistics')
    type = models.ForeignKey(StatisticType, on_delete=models.CASCADE)
    value = models.FloatField()
    state = models.CharField(max_length=10, choices=STATE_CHOICES)
    message_state = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.type.name} - {self.orchard.name}"

class WeeklyValue(models.Model):
    statistic = models.ForeignKey(Statistic, on_delete=models.CASCADE, related_name='weekly_values')
    day = models.CharField(max_length=10)
    value = models.FloatField()

    def __str__(self):
        return f"{self.day}: {self.value}"

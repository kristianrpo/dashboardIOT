from django.db import models

class Garbage(models.Model):
    id = models.AutoField(primary_key=True)
    raae_distance = models.FloatField()
    caps_distance = models.FloatField()
    luminaires_distance = models.FloatField()
    batteries_distance = models.FloatField()
    medicines_distance = models.FloatField()
    oils_distance = models.FloatField()

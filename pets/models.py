from django.db import models

class PetMachine(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=50)
    next_refill = models.DateTimeField()
    last_refill = models.DateTimeField()
    automatic_start_date = models.DateTimeField()
    automatic_end_date = models.DateTimeField()
    dispense_count = models.IntegerField()
    portion_size = models.IntegerField()
    no_food = models.BooleanField(default=False)


# Create your models here.

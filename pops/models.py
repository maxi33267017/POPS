from django.db import models
from decimal import Decimal

# Create your models here.

class SoldEquipment(models.Model):
    serial_number = models.CharField(max_length=50, unique=True)
    model = models.CharField(max_length=50)
    sale_date = models.DateField()

    def __str__(self):
        return f"{self.model} - {self.serial_number}"

class ServiceRecord(models.Model):
    serial_number = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    service_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.model} - {self.serial_number} - {self.service_date}"

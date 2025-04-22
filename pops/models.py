from django.db import models
from decimal import Decimal

# Create your models here.

class SoldEquipment(models.Model):
    serial_number = models.CharField(max_length=100, primary_key=True)
    model = models.CharField(max_length=100)
    sale_date = models.DateField()
    customer = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.model} - {self.serial_number}"

class ServiceRecord(models.Model):
    SERVICE_TYPES = [
        ('preventive', 'Preventivo'),
        ('corrective', 'Correctivo'),
        ('calibration', 'Calibración'),
        ('other', 'Otro')
    ]
    
    serial_number = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    service_date = models.DateField()
    customer = models.CharField(max_length=200, null=True, blank=True)
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES, default='preventive')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.model} - {self.serial_number} - {self.service_date}"

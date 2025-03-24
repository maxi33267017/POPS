from django.db import models

# Create your models here.

class SoldEquipment(models.Model):
    serial_number = models.CharField(max_length=100, unique=True)
    model = models.CharField(max_length=100)
    sale_date = models.DateField()

    def __str__(self):
        return f"{self.serial_number} - {self.model} - {self.sale_date}"

class ServiceRecord(models.Model):
    SERVICE_TYPES = [
        ('servicio', 'Servicio'),
        ('garantia', 'Garantia'),
        ('Pip', 'pip'),
        ('interno', 'Interno'),
    ]

    serial_number = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    service_date = models.DateField()
    invoice_number = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)

    def __str__(self):
        return f"{self.serial_number} - {self.service_date} - {self.invoice_number}"

# Generated by Django 4.2.20 on 2025-03-24 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pops', '0004_remove_servicerecord_invoice_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='soldequipment',
            name='customer',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]

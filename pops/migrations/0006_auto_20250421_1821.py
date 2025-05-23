# Generated by Django 3.2.25 on 2025-04-21 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pops', '0005_soldequipment_customer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='servicerecord',
            name='total_amount',
        ),
        migrations.AddField(
            model_name='servicerecord',
            name='customer',
            field=models.CharField(default='N/A', max_length=200),
        ),
        migrations.AddField(
            model_name='servicerecord',
            name='revenue',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='servicerecord',
            name='service_type',
            field=models.CharField(choices=[('preventive', 'Preventivo'), ('corrective', 'Correctivo'), ('calibration', 'Calibración'), ('other', 'Otro')], default='preventive', max_length=50),
        ),
        migrations.AlterField(
            model_name='servicerecord',
            name='model',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='servicerecord',
            name='serial_number',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='soldequipment',
            name='customer',
            field=models.CharField(default='N/A', max_length=200),
        ),
        migrations.AlterField(
            model_name='soldequipment',
            name='model',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='soldequipment',
            name='serial_number',
            field=models.CharField(max_length=100),
        ),
    ]

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime, timedelta, date
import json
from .models import SoldEquipment, ServiceRecord
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from django.db.models import Count, Sum

def index(request):
    return render(request, 'pops/index.html')

@csrf_exempt
def upload_sold_equipment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            SoldEquipment.objects.all().delete()  # Limpiar registros existentes
            for item in data:
                SoldEquipment.objects.create(
                    serial_number=item['serial_number'],
                    model=item['model'],
                    sale_date=datetime.strptime(item['sale_date'], '%Y-%m-%d').date()
                )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def upload_service_records(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ServiceRecord.objects.all().delete()  # Limpiar registros existentes
            for item in data:
                # Convertir la fecha al formato correcto
                service_date = datetime.strptime(item['service_date'], '%Y-%m-%d').date()
                
                ServiceRecord.objects.create(
                    serial_number=item['serial_number'],
                    model=item['model'],
                    service_date=service_date,
                    total_amount=Decimal(str(item['total_amount']))
                )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def calculate_monthly_pops(request):
    try:
        # Definir rango de fechas para el análisis
        start_date = date(2023, 1, 1)
        end_date = date(2025, 2, 28)
        current_date = start_date
        monthly_results = []

        while current_date <= end_date:
            # Para cada mes, calcular:
            month_end = current_date + relativedelta(months=1, days=-1)
            
            # 1. Ventas de los últimos 10 años hasta ese mes
            sales_start = current_date - relativedelta(years=10)
            sold_equipment = set(SoldEquipment.objects.filter(
                sale_date__range=[sales_start, month_end]
            ).values_list('serial_number', flat=True))

            # Total de equipos vendidos en los últimos 10 años hasta ese mes
            total_equipment_sold = len(sold_equipment)

            # 2. Servicios del período interanual
            service_start = current_date - relativedelta(years=1)
            service_end = current_date + relativedelta(months=1, days=-1)
            
            # Obtener todos los servicios del período interanual
            services = ServiceRecord.objects.filter(
                service_date__range=[service_start, service_end]
            )
            
            # 3. Calcular total de servicios (todos los registros del período interanual)
            total_services = services.count()
            
            # 4. Calcular servicios a equipos recientes (PINs únicos que están en la lista de vendidos)
            valid_pins = set(services.filter(serial_number__in=sold_equipment)
                          .values_list('serial_number', flat=True))
            valid_count = len(valid_pins)
            
            # 5. Calcular servicios a equipos antiguos (PINs únicos que no están en la lista de vendidos)
            older_pins = set(services.exclude(serial_number__in=sold_equipment)
                          .values_list('serial_number', flat=True))
            older_count = len(older_pins)
            
            # 6. Calcular POPS
            # POPS solo con equipos recientes
            if total_equipment_sold > 0:
                pops_recent = (valid_count / total_equipment_sold * 100)
            else:
                pops_recent = 0

            # POPS con equipos recientes y antiguos
            if total_equipment_sold > 0:
                total_service_equipment = valid_count + older_count
                pops_with_older = (total_service_equipment / total_equipment_sold * 100)
            else:
                pops_with_older = 0
            
            # Agregar resultados del mes
            monthly_results.append({
                'month': current_date.strftime('%Y-%m'),
                'total_equipment_sold': total_equipment_sold,
                'total_services': total_services,
                'services_to_recent': valid_count,
                'services_to_older': older_count,
                'pops_recent': round(pops_recent, 2),
                'pops_with_older': round(pops_with_older, 2)
            })
            
            # Avanzar al siguiente mes
            current_date = current_date + relativedelta(months=1)

        # Calcular los 10 modelos con más servicios
        top_serviced_models = ServiceRecord.objects.values('model').annotate(
            total_services=Count('id')
        ).order_by('-total_services')[:10]

        # Calcular los 10 modelos más vendidos en los últimos 10 años
        ten_years_ago = date.today() - relativedelta(years=10)
        top_sold_models = SoldEquipment.objects.filter(
            sale_date__gte=ten_years_ago
        ).values('model').annotate(
            total_sold=Count('id')
        ).order_by('-total_sold')[:10]

        # Calcular los 10 modelos con mayor facturación por servicios
        top_revenue_models = ServiceRecord.objects.values('model').annotate(
            total_revenue=Sum('total_amount')
        ).order_by('-total_revenue')[:10]

        return JsonResponse({
            'status': 'success',
            'monthly_data': monthly_results,
            'top_serviced_models': list(top_serviced_models),
            'top_sold_models': list(top_sold_models),
            'top_revenue_models': list(top_revenue_models)
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

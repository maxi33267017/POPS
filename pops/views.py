from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime, timedelta, date
import json
from .models import SoldEquipment, ServiceRecord
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from django.db.models import Count, Sum
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

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

def export_to_excel(request):
    try:
        # Crear un nuevo libro de Excel
        wb = Workbook()
        
        # Obtener los datos para cada tabla
        # 1. Datos mensuales
        start_date = date(2023, 1, 1)
        end_date = date(2025, 2, 28)
        current_date = start_date
        monthly_results = []

        while current_date <= end_date:
            month_end = current_date + relativedelta(months=1, days=-1)
            sales_start = current_date - relativedelta(years=10)
            sold_equipment = set(SoldEquipment.objects.filter(
                sale_date__range=[sales_start, month_end]
            ).values_list('serial_number', flat=True))
            total_equipment_sold = len(sold_equipment)
            service_start = current_date - relativedelta(years=1)
            service_end = current_date + relativedelta(months=1, days=-1)
            services = ServiceRecord.objects.filter(
                service_date__range=[service_start, service_end]
            )
            total_services = services.count()
            valid_pins = set(services.filter(serial_number__in=sold_equipment)
                          .values_list('serial_number', flat=True))
            valid_count = len(valid_pins)
            older_pins = set(services.exclude(serial_number__in=sold_equipment)
                          .values_list('serial_number', flat=True))
            older_count = len(older_pins)
            
            if total_equipment_sold > 0:
                pops_recent = (valid_count / total_equipment_sold * 100)
                total_service_equipment = valid_count + older_count
                pops_with_older = (total_service_equipment / total_equipment_sold * 100)
            else:
                pops_recent = 0
                pops_with_older = 0
            
            monthly_results.append({
                'month': current_date.strftime('%Y-%m'),
                'total_equipment_sold': total_equipment_sold,
                'total_services': total_services,
                'services_to_recent': valid_count,
                'services_to_older': older_count,
                'pops_recent': round(pops_recent, 2),
                'pops_with_older': round(pops_with_older, 2)
            })
            current_date = current_date + relativedelta(months=1)

        # 2. Top modelos con más servicios
        top_serviced_models = ServiceRecord.objects.values('model').annotate(
            total_services=Count('id')
        ).order_by('-total_services')[:10]

        # 3. Top modelos más vendidos
        ten_years_ago = date.today() - relativedelta(years=10)
        top_sold_models = SoldEquipment.objects.filter(
            sale_date__gte=ten_years_ago
        ).values('model').annotate(
            total_sold=Count('id')
        ).order_by('-total_sold')[:10]

        # 4. Top modelos por facturación
        top_revenue_models = ServiceRecord.objects.values('model').annotate(
            total_revenue=Sum('total_amount')
        ).order_by('-total_revenue')[:10]

        # Estilo para los encabezados
        header_font = Font(bold=True)
        header_fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        center_alignment = Alignment(horizontal='center')

        # 1. Hoja de datos mensuales
        ws_monthly = wb.active
        ws_monthly.title = "Datos Mensuales"
        headers = ['Mes', 'Total Equipos Vendidos', 'Total Servicios', 'Servicios a Equipos Recientes', 
                  'Servicios a Equipos Antiguos', 'POPS Recientes (%)', 'POPS con Antiguos (%)']
        for col, header in enumerate(headers, 1):
            cell = ws_monthly.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_alignment

        for row, data in enumerate(monthly_results, 2):
            ws_monthly.cell(row=row, column=1, value=data['month'])
            ws_monthly.cell(row=row, column=2, value=data['total_equipment_sold'])
            ws_monthly.cell(row=row, column=3, value=data['total_services'])
            ws_monthly.cell(row=row, column=4, value=data['services_to_recent'])
            ws_monthly.cell(row=row, column=5, value=data['services_to_older'])
            ws_monthly.cell(row=row, column=6, value=data['pops_recent'])
            ws_monthly.cell(row=row, column=7, value=data['pops_with_older'])

        # 2. Hoja de modelos con más servicios
        ws_serviced = wb.create_sheet("Modelos con Más Servicios")
        headers = ['Modelo', 'Total Servicios']
        for col, header in enumerate(headers, 1):
            cell = ws_serviced.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_alignment

        for row, model in enumerate(top_serviced_models, 2):
            ws_serviced.cell(row=row, column=1, value=model['model'])
            ws_serviced.cell(row=row, column=2, value=model['total_services'])

        # 3. Hoja de modelos más vendidos
        ws_sold = wb.create_sheet("Modelos Más Vendidos")
        headers = ['Modelo', 'Total Vendido']
        for col, header in enumerate(headers, 1):
            cell = ws_sold.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_alignment

        for row, model in enumerate(top_sold_models, 2):
            ws_sold.cell(row=row, column=1, value=model['model'])
            ws_sold.cell(row=row, column=2, value=model['total_sold'])

        # 4. Hoja de modelos por facturación
        ws_revenue = wb.create_sheet("Modelos por Facturación")
        headers = ['Modelo', 'Total Facturado']
        for col, header in enumerate(headers, 1):
            cell = ws_revenue.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_alignment

        for row, model in enumerate(top_revenue_models, 2):
            ws_revenue.cell(row=row, column=1, value=model['model'])
            ws_revenue.cell(row=row, column=2, value=float(model['total_revenue']))

        # 5. Hoja de equipos sin servicios
        ws_no_services = wb.create_sheet("Equipos sin Servicios")
        headers = ['PIN', 'Modelo', 'Fecha de Venta', 'Meses sin Servicio']
        for col, header in enumerate(headers, 1):
            cell = ws_no_services.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_alignment

        # Obtener datos de equipos sin servicios
        sold_equipment = SoldEquipment.objects.all().values('serial_number', 'model', 'sale_date')
        service_start = date(2023, 1, 1)
        service_end = date(2025, 2, 28)
        serviced_pins = set(ServiceRecord.objects.filter(
            service_date__range=[service_start, service_end]
        ).values_list('serial_number', flat=True))
        
        equipment_without_services = [
            {
                'serial_number': eq['serial_number'],
                'model': eq['model'],
                'sale_date': eq['sale_date'].strftime('%Y-%m-%d'),
                'months_without_service': (date.today() - eq['sale_date']).days / 30.44
            }
            for eq in sold_equipment
            if eq['serial_number'] not in serviced_pins
        ]
        
        equipment_without_services.sort(key=lambda x: x['months_without_service'], reverse=True)

        # Agregar resumen al inicio de la hoja
        ws_no_services.cell(row=2, column=1, value="Total Equipos Vendidos:")
        ws_no_services.cell(row=2, column=2, value=len(sold_equipment))
        ws_no_services.cell(row=3, column=1, value="Equipos sin Servicios:")
        ws_no_services.cell(row=3, column=2, value=len(equipment_without_services))
        ws_no_services.cell(row=4, column=1, value="Período de Servicios:")
        ws_no_services.cell(row=4, column=2, value=f"{service_start.strftime('%Y-%m-%d')} a {service_end.strftime('%Y-%m-%d')}")

        # Agregar los datos de equipos sin servicios
        for row, eq in enumerate(equipment_without_services, 6):  # Empezar desde la fila 6 para dejar espacio para el resumen
            ws_no_services.cell(row=row, column=1, value=eq['serial_number'])
            ws_no_services.cell(row=row, column=2, value=eq['model'])
            ws_no_services.cell(row=row, column=3, value=eq['sale_date'])
            ws_no_services.cell(row=row, column=4, value=round(eq['months_without_service'], 1))

        # Ajustar el ancho de las columnas
        for ws in [ws_monthly, ws_serviced, ws_sold, ws_revenue, ws_no_services]:
            for column in ws.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                ws.column_dimensions[get_column_letter(column[0].column)].width = adjusted_width

        # Crear la respuesta HTTP con el archivo Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=pops_report.xlsx'
        wb.save(response)
        return response

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

def get_equipment_without_services(request):
    try:
        # Obtener la fecha de hace 10 años
        ten_years_ago = date.today() - relativedelta(years=10)
        
        # Obtener todos los equipos vendidos en los últimos 10 años
        sold_equipment = SoldEquipment.objects.filter(
            sale_date__gte=ten_years_ago
        ).values('serial_number', 'model', 'sale_date')
        
        # Obtener los PINs que han recibido servicios entre enero 2023 y febrero 2025
        service_start = date(2023, 1, 1)
        service_end = date(2025, 2, 28)
        serviced_pins = set(ServiceRecord.objects.filter(
            service_date__range=[service_start, service_end]
        ).values_list('serial_number', flat=True))
        
        # Filtrar los equipos vendidos que no han recibido servicios en el período
        equipment_without_services = [
            {
                'serial_number': eq['serial_number'],
                'model': eq['model'],
                'sale_date': eq['sale_date'].strftime('%Y-%m-%d'),
                'months_without_service': (date.today() - eq['sale_date']).days / 30.44  # Promedio de días por mes
            }
            for eq in sold_equipment
            if eq['serial_number'] not in serviced_pins
        ]
        
        # Ordenar por meses sin servicio (descendente)
        equipment_without_services.sort(key=lambda x: x['months_without_service'], reverse=True)
        
        return JsonResponse({
            'status': 'success',
            'equipment': equipment_without_services,
            'total_sold': len(sold_equipment),
            'total_without_service': len(equipment_without_services),
            'period': {
                'sales': f"{ten_years_ago.strftime('%Y-%m-%d')} a {date.today().strftime('%Y-%m-%d')}",
                'services': f"{service_start.strftime('%Y-%m-%d')} a {service_end.strftime('%Y-%m-%d')}"
            }
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

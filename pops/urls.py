from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/sold-equipment/', views.upload_sold_equipment, name='upload_sold_equipment'),
    path('upload/service-records/', views.upload_service_records, name='upload_service_records'),
    path('calculate-monthly-pops/', views.calculate_monthly_pops, name='calculate_monthly_pops'),
    path('export-excel/', views.export_to_excel, name='export_to_excel'),
    path('equipment-without-services/', views.get_equipment_without_services, name='equipment_without_services'),
] 
import pandas as pd
import json
from datetime import datetime

def excel_to_sold_equipment_json(excel_file, sheet_name=0):
    """
    Convierte datos de equipos vendidos desde Excel a JSON
    """
    try:
        # Leer el archivo Excel
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        
        # Asumimos que las columnas son 'serial_number' y 'sale_date'
        # Ajusta estos nombres según las columnas en tu Excel
        df.columns = ['serial_number', 'sale_date']
        
        # Convertir fechas al formato correcto
        df['sale_date'] = pd.to_datetime(df['sale_date']).dt.strftime('%Y-%m-%d')
        
        # Convertir a lista de diccionarios
        records = df.to_dict('records')
        
        # Guardar como JSON
        with open('sold_equipment.json', 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=4)
        
        print("Archivo JSON creado exitosamente: sold_equipment.json")
        
    except Exception as e:
        print(f"Error al procesar el archivo: {str(e)}")

def excel_to_service_records_json(excel_file, sheet_name=0):
    """
    Convierte datos de registros de servicio desde Excel a JSON
    """
    try:
        # Leer el archivo Excel
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        
        # Asumimos que las columnas son todas las necesarias para el servicio
        # Ajusta estos nombres según las columnas en tu Excel
        df.columns = ['serial_number', 'model', 'service_date', 'invoice_number', 'total_amount', 'service_type']
        
        # Convertir fechas al formato correcto
        df['service_date'] = pd.to_datetime(df['service_date']).dt.strftime('%Y-%m-%d')
        
        # Asegurar que total_amount sea numérico
        df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce')
        
        # Convertir a lista de diccionarios
        records = df.to_dict('records')
        
        # Guardar como JSON
        with open('service_records.json', 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=4)
        
        print("Archivo JSON creado exitosamente: service_records.json")
        
    except Exception as e:
        print(f"Error al procesar el archivo: {str(e)}")

if __name__ == "__main__":
    # Ejemplo de uso
    print("Selecciona el tipo de datos a convertir:")
    print("1. Equipos vendidos (serial_number y fecha)")
    print("2. Registros de servicio (todos los datos de servicio)")
    
    opcion = input("Ingresa el número de opción (1 o 2): ")
    archivo_excel = input("Ingresa la ruta del archivo Excel: ")
    
    if opcion == "1":
        excel_to_sold_equipment_json(archivo_excel)
    elif opcion == "2":
        excel_to_service_records_json(archivo_excel)
    else:
        print("Opción no válida") 
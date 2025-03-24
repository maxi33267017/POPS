import pandas as pd
import json
from datetime import datetime
import numpy as np

def clean_value(value):
    if pd.isna(value) or value == 'nan' or value == 'NaN':
        return None
    return value

def convert_excel_to_json(excel_file):
    try:
        # Leer el archivo Excel y mostrar las hojas disponibles
        excel = pd.ExcelFile(excel_file)
        print("\nHojas disponibles en el archivo:")
        for sheet_name in excel.sheet_names:
            print(f"- {sheet_name}")
        
        # Leer la hoja del archivo Excel
        df = pd.read_excel(excel_file, sheet_name="Hoja1")
        
        # Mostrar las columnas disponibles
        print("\nColumnas disponibles en la hoja:")
        for col in df.columns:
            print(f"- {col}")
        
        # Convertir las fechas al formato correcto (YYYY-MM-DD)
        date_columns = df.select_dtypes(include=['datetime64']).columns
        for col in date_columns:
            df[col] = df[col].dt.strftime('%Y-%m-%d')
        
        # Limpiar valores NaN y convertir a string donde sea necesario
        for col in df.columns:
            df[col] = df[col].apply(clean_value)
            if col not in date_columns:  # No convertir fechas a string
                df[col] = df[col].astype(str).replace('None', None)
        
        # Procesar equipos vendidos
        data = df.rename(columns={
            'PIN': 'serial_number',
            'Modelo': 'model',
            'Fecha de venta': 'sale_date',
            'Cliente': 'customer'
        })[['serial_number', 'model', 'sale_date', 'customer']].to_dict('records')
        
        # Validar que no haya valores NaN en los datos
        for record in data:
            for key, value in record.items():
                if pd.isna(value) or value == 'nan' or value == 'NaN':
                    record[key] = None
        
        # Guardar como JSON
        output = f"{excel_file.rsplit('.', 1)[0]}_sold.json"
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Verificar que el JSON es válido
        with open(output, 'r', encoding='utf-8') as f:
            json.load(f)  # Esto lanzará un error si el JSON no es válido
        
        print(f"\nArchivo JSON creado exitosamente:")
        print(f"1. {output}")
        print(f"   - Total de registros: {len(data)}")
        print(f"   - Columnas: serial_number, model, sale_date, customer")
            
        return output
        
    except Exception as e:
        print(f"Error al convertir el archivo: {str(e)}")
        return None

if __name__ == "__main__":
    # Solicitar el archivo Excel al usuario
    excel_file = input("Ingrese la ruta del archivo Excel: ")
    convert_excel_to_json(excel_file) 
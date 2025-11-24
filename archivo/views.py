import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from .models import Archivo
from .serializers import ExcelUploadSerializer, RacSerializer

class ExcelUploadView(APIView):
    serializer_class = ExcelUploadSerializer

    def post(self, request, *args, **kwargs):
        print('request.data:', request.data)
        print('request.FILES:', request.FILES)
        # 1. Validar archivo
        serializer_file = self.serializer_class(data=request.data)
        serializer_file.is_valid(raise_exception=True)
        excel_file = serializer_file.validated_data['excel_file']

        # 2. Leer Excel
        try:
            df = pd.read_excel(excel_file, sheet_name=0)
            # Si existe la columna FECHA DE INGRESO, convertir a solo fecha
            if 'FECHA DE INGRESO' in df.columns:
                df['FECHA DE INGRESO'] = pd.to_datetime(df['FECHA DE INGRESO']).dt.date
            if 'TRABAJADOR' in df.columns:
                df['TRABAJADOR'] = df['TRABAJADOR'].fillna('')
                split_data = df['TRABAJADOR'].str.split(' ', n=1, expand=True)
                df['nombre'] = split_data[0]
                df['apellido'] = split_data[1]
        except Exception as e:
            print('Error al leer el archivo Excel:', str(e))
            return Response({
                "status": "error",
                "message": f"Error al leer el archivo Excel: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        personas_validadas = []
        errores_de_fila = []

        # 3. Iterar (Solo validar, no guardar aún)
        for index, row in df.iterrows():
            fila_data = {
                # Asegúrate que las keys del diccionario coincidan con tu modelo
                'cedula': str(row.get('CEDULA', '')).strip(), # .strip() quita espacios
                'nombre': row.get('nombre', None), # Asegúrate que la columna exista en el Excel
                'apellido': row.get('apellido', None),
                'fecha_ingreso': row.get('FECHA DE INGRESO', None),
                'cargo': row.get('CARGO', ''),
                'grado_cargo': row.get('GRADO     DEL     CARGO', ''),
                'antiguedad': row.get('ANTIGÜEDAD', 0),
                'salario': row.get('SALARIO', 0),
            }
            
            rac_serializer = RacSerializer(data=fila_data)

            if rac_serializer.is_valid():
                personas_validadas.append(rac_serializer.validated_data)
            else:
                errores_de_fila.append({
                    'fila': index + 2, 
                    'errores': rac_serializer.errors
                })

        # 4. Verificar errores FUERA del bucle
        if errores_de_fila:
            print('Errores de validación por fila:', errores_de_fila)
            print('Retornando error 400 por validación')
            return Response(
                {"error": "El archivo contiene errores de validación", "detalles": errores_de_fila}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 5. Guardar masivamente FUERA del bucle
        try:
            with transaction.atomic():
                personas_a_crear = [Archivo(**data) for data in personas_validadas]
                Archivo.objects.bulk_create(personas_a_crear, ignore_conflicts=False)
            print('Guardado exitoso. Total registros:', len(personas_a_crear))
            return Response({
                "mensaje": "Archivo procesado y datos guardados exitosamente.",
                "total_registros": len(personas_validadas),
                "registros_guardados": len(personas_a_crear)
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print('Error al guardar en base de datos:', str(e))
            return Response({
                "status": "error",
                "message": f"Error al guardar los datos en la base de datos: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        print('Fin del método post')
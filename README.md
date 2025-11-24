# Proyecto PANDAS (Django)

Descripción detallada del proyecto, instrucciones de instalación y uso.

**Resumen del proyecto**:
- **Nombre:** PANDAS (proyecto Django)
- **Framework:** Django 5.2.8
- **API:** Django REST Framework
- **Objetivo:** Subir y procesar archivos Excel con datos de trabajadores, validar filas y guardar registros en una base SQLite.

**Tecnologías y dependencias**:
- **Django:** 5.2.8
- **Django REST Framework:** 3.16.1
- **Pandas:** 2.3.3
- **openpyxl:** 3.1.5 (lectura/escritura de Excel)
- **numpy, python-dateutil, pytz, tzdata** (soporte de fechas/array)
- Ver `requirements.txt` para la lista completa.

**Estructura del proyecto (resumen)**
- `manage.py` : script de gestión de Django.
- `db.sqlite3` : base de datos SQLite por defecto.
- `myapp/` : proyecto Django principal (configuración).
  - `settings.py` : configuración del proyecto.
  - `urls.py` : incluye las URLs de la app `archivo`.
- `archivo/` : app principal que procesa los archivos Excel.
  - `models.py` : definición del modelo `Archivo`.
  - `serializers.py` : `RacSerializer` y `ExcelUploadSerializer`.
  - `views.py` : `ExcelUploadView` que procesa y guarda datos desde Excel.
  - `urls.py` : ruta para subir el Excel: `api/productos/upload/`.
  - `migrations/` : migraciones de la base de datos.

**Modelo principal** (`archivo/models.py`)
- Clase `Archivo` con campos:
  - `cedula` : `CharField(max_length=20)`
  - `nombre` : `CharField(max_length=100)`
  - `apellido` : `CharField(max_length=100)`
  - `fecha_ingreso` : `DateField()`
  - `cargo` : `CharField(max_length=100)`
  - `grado_cargo` : `CharField(max_length=50)`
  - `antiguedad` : `IntegerField()`
  - `salario` : `DecimalField(max_digits=10, decimal_places=3)`

**Serializers** (`archivo/serializers.py`)
- `RacSerializer` (ModelSerializer): valida y serializa campos de `Archivo`.
  - Validación: `validate_cedula` asegura que la cédula contenga solo dígitos y tenga entre 4 y 12 caracteres.
- `ExcelUploadSerializer`: usa `FileField` y define parseadores `MultiPartParser` y `FormParser` para recibir archivos.

**Vista principal (flujo)** (`archivo/views.py` — `ExcelUploadView`)
- Método `post` que hace lo siguiente:
  1. Valida que el archivo exista usando `ExcelUploadSerializer`.
  2. Lee el archivo Excel con `pandas.read_excel` (hoja 0 por defecto).
  3. Si existe columna `FECHA DE INGRESO` la convierte a tipo fecha (solo date).
  4. Si existe columna `TRABAJADOR`, intenta separar `nombre` y `apellido` (split en primer espacio).
  5. Construye un diccionario por fila con las claves esperadas por `RacSerializer`.
  6. Valida cada fila con `RacSerializer` acumulando `personas_validadas` o `errores_de_fila`.
  7. Si hay errores de validación devuelve `400` con detalles por fila.
  8. Si todo es válido, realiza un `bulk_create` dentro de `transaction.atomic()` para guardar todos los registros.
  9. Devuelve `201` con resumen (total registros procesados/guardados) o `500` en caso de error de BD.

**Rutas / Endpoints**
- `POST /api/productos/upload/` : subir archivo Excel multipart con campo `excel_file`.
  - Expectativas sobre el Excel:
    - Columnas útiles (según código): `CEDULA`, `TRABAJADOR`, `FECHA DE INGRESO`, `CARGO`, `GRADO     DEL     CARGO`, `ANTIGÜEDAD`, `SALARIO`.
    - El código asigna `nombre` y `apellido` a partir de `TRABAJADOR` (split en primer espacio).

**Comandos básicos (Windows PowerShell)**
```powershell
# Crear y activar entorno virtual (si no existe)
python -m venv venv
; .\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Migraciones y superusuario
python manage.py migrate
python manage.py createsuperuser

# Ejecutar servidor en desarrollo
python manage.py runserver
```

**Ejemplo de subida (curl)**
```bash
curl -X POST "http://127.0.0.1:8000/api/productos/upload/" -F "excel_file=@/ruta/al/archivo.xlsx"
```

O con Python `requests`:
```python
import requests

url = 'http://127.0.0.1:8000/api/productos/upload/'
files = {'excel_file': open('archivo.xlsx', 'rb')}
r = requests.post(url, files=files)
print(r.status_code, r.json())
```

**Notas importantes y sugerencias de mejora**
- Actualmente `DEBUG = True` y `SECRET_KEY` está en `settings.py`: mover variables sensibles a variables de entorno para producción.
- Validaciones adicionales:
  - Normalizar valores de columnas (ej. quitar comas en `SALARIO`, manejar decimales locales).
  - Controlar formatos de fecha más robustamente.
  - Manejar nombres compuestos al separar `TRABAJADOR` (hoy separa en primer espacio solamente).
- Performance: para archivos muy grandes considerar procesamiento por lotes y/o tareas asíncronas (Celery/RQ).
- Añadir pruebas unitarias y de integración para garantizar comportamiento en distintos formatos de Excel.

**Archivos clave**
- `archivo/models.py` : modelo `Archivo`.
- `archivo/serializers.py` : `RacSerializer`, `ExcelUploadSerializer`.
- `archivo/views.py` : `ExcelUploadView` (lógica de lectura/validación/guardado).
- `archivo/urls.py` : incluye la ruta `api/productos/upload/`.
- `myapp/settings.py` : configuración principal.

---

Si quieres que escriba el README en otro idioma, que lo guarde en otra ruta, o que añada un ejemplo de prueba unitaria o Postman collection, dime y lo hago.

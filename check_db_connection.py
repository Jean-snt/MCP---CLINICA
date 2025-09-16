import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Reflexo.settings')
django.setup()

from django.db import connection
from django.conf import settings

print("=== VERIFICACIÓN DE CONEXIÓN A BASE DE DATOS ===")
print(f"Base de datos configurada: {settings.DATABASES['default']['NAME']}")
print(f"Host: {settings.DATABASES['default']['HOST']}")
print(f"Puerto: {settings.DATABASES['default']['PORT']}")
print(f"Usuario: {settings.DATABASES['default']['USER']}")

# Verificar conexión Django
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]
        print(f"✓ Django conectado a la base de datos: {db_name}")
        
        # Listar todas las tablas
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"✓ Tablas en la base de datos ({len(tables)}):")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Verificar si existe la tabla therapists (no clinica_therapist)
        cursor.execute("SHOW TABLES LIKE 'therapists'")
        table_exists = cursor.fetchone()
        if table_exists:
            print("✓ Tabla 'therapists' existe")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM therapists")
            count = cursor.fetchone()[0]
            print(f"✓ Registros en therapists: {count}")
            
            # Mostrar algunos registros
            cursor.execute("SELECT id, document_number, first_name, last_name_paternal FROM therapists LIMIT 5")
            records = cursor.fetchall()
            print("✓ Registros encontrados:")
            for record in records:
                print(f"  ID: {record[0]}, Doc: {record[1]}, Nombre: {record[2]} {record[3]}")
        else:
            print("✗ Tabla 'therapists' NO existe")
            
except Exception as e:
    print(f"✗ Error de conexión Django: {e}")
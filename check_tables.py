import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Reflexo.settings')
django.setup()

from django.db import connection

def check_existing_tables():
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("Tablas existentes en la base de datos:")
        for table in tables:
            print(f"- {table[0]}")
        
        # Verificar si existen las tablas de referencia
        reference_tables = ['document_types', 'districts', 'provinces', 'regions']
        print("\nVerificando tablas de referencia:")
        for table in reference_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✓ {table}: {count} registros")
            except Exception as e:
                print(f"✗ {table}: No existe - {e}")

if __name__ == "__main__":
    check_existing_tables()
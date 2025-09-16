import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Reflexo.settings')
django.setup()

from django.db import connection

def check_table_structure(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f'DESCRIBE {table_name}')
        columns = cursor.fetchall()
        print(f"\nEstructura de la tabla '{table_name}':")
        print("Campo | Tipo | Null | Key | Default | Extra")
        print("-" * 50)
        for column in columns:
            print(f"{column[0]} | {column[1]} | {column[2]} | {column[3]} | {column[4]} | {column[5]}")

if __name__ == "__main__":
    try:
        check_table_structure('therapists')
    except Exception as e:
        print(f"Error: {e}")
#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Reflexo.settings')
django.setup()

from clinica.models import Therapist

print("=== Verificando Terapeutas en la Base de Datos ===")
print()

try:
    therapists = Therapist.objects.all()
    print(f"Total de terapeutas encontrados: {therapists.count()}")
    print()
    
    if therapists.exists():
        for t in therapists:
            print(f"ID: {t.id}")
            print(f"Nombre: {t.first_name} {t.last_name_paternal} {t.last_name_maternal}")
            print(f"Email: {t.email}")
            print(f"Document Number: {t.document_number}")
            print(f"Teléfono: {t.phone}")
            print(f"Creado: {t.created_at}")
            print("-" * 50)
    else:
        print("No se encontraron terapeutas en la base de datos.")
        
except Exception as e:
    print(f"Error al consultar terapeutas: {e}")
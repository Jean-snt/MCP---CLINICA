import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration
from google.oauth2 import service_account
from .models import Therapist, Patient, Appointment, MedicalRecord, Ticket
import random

@csrf_exempt
def chatbot_api_view(request):
    if request.method == 'POST':
        try:
            print("=== INICIO CHATBOT API ===")
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            print(f"Credentials path: {credentials_path}")
            
            if not credentials_path:
                error_msg = "La variable GOOGLE_APPLICATION_CREDENTIALS no está configurada."
                print(f"ERROR: {error_msg}")
                raise ValueError(error_msg)
            
            # Verificar que el archivo existe
            if not os.path.exists(credentials_path.strip()):
                error_msg = f"El archivo de credenciales no existe: {credentials_path}"
                print(f"ERROR: {error_msg}")
                raise FileNotFoundError(error_msg)
            
            print("Configurando credenciales...")
            creds = service_account.Credentials.from_service_account_file(credentials_path.strip())
            genai.configure(credentials=creds)
            print("Credenciales configuradas exitosamente")

            # Funciones para interactuar con la base de datos

            def create_therapist_function(name: str, email: str, document_number: str = None) -> str:
                try:
                    from .models import DocumentType, District, Province, Region
                    
                    # Separar el nombre completo en partes
                    name_parts = name.strip().split()
                    if len(name_parts) >= 2:
                        first_name = name_parts[0]
                        last_name_paternal = name_parts[1]
                        last_name_maternal = name_parts[2] if len(name_parts) > 2 else ""
                    else:
                        first_name = name
                        last_name_paternal = "Sin apellido"
                        last_name_maternal = ""
                    
                    # Generar un document_number si no se proporciona
                    if not document_number:
                        import random
                        document_number = f"DOC{random.randint(10000, 99999)}"
                    
                    # Obtener valores por defecto para todos los campos requeridos
                    default_document_type = DocumentType.objects.first()
                    default_district = District.objects.first()
                    default_province = Province.objects.first()
                    default_region = Region.objects.first()
                    
                    new_therapist = Therapist.objects.create(
                        document_number=document_number,
                        first_name=first_name,
                        last_name_paternal=last_name_paternal,
                        last_name_maternal=last_name_maternal,
                        email=email,
                        document_type=default_document_type,
                        district=default_district,
                        province=default_province,
                        region=default_region
                    )
                    return f"Terapeuta '{new_therapist.first_name} {new_therapist.last_name_paternal}' con email '{new_therapist.email}' creado exitosamente."
                except Exception as e:
                    return f"Error al crear terapeuta: {e}"

            def create_patient_function(name: str, email: str, phone_number: str) -> str:
                try:
                    from .models import DocumentType, District, Province, Region
                    import random
                    import string
                    
                    # Generar un document_number único
                    while True:
                        # Generar un número aleatorio de 6 dígitos
                        random_number = ''.join(random.choices(string.digits, k=6))
                        document_number = f"PAT{random_number}"
                        
                        # Verificar que no exista ya en la base de datos
                        if not Patient.objects.filter(document_number=document_number).exists():
                            break
                    
                    # Obtener valores por defecto para todos los campos requeridos
                    default_document_type = DocumentType.objects.first()
                    default_district = District.objects.first()
                    default_province = Province.objects.first()
                    default_region = Region.objects.first()
                    
                    new_patient = Patient.objects.create(
                        name=name, 
                        email=email, 
                        phone_number=phone_number,
                        document_number=document_number,
                        document_type=default_document_type,
                        district=default_district,
                        province=default_province,
                        region=default_region
                    )
                    return f"Paciente '{new_patient.name}' creado exitosamente."
                except Exception as e:
                    return f"Error al crear paciente: {e}"

            def modify_therapist_function(id: int, new_name: str = None, new_email: str = None, new_phone_number: str = None) -> str:
                try:
                    therapist_to_modify = Therapist.objects.get(id=id)
                    if new_name:
                        # Separar el nombre completo en partes
                        name_parts = new_name.strip().split()
                        if len(name_parts) >= 2:
                            therapist_to_modify.first_name = name_parts[0]
                            therapist_to_modify.last_name_paternal = name_parts[1]
                            therapist_to_modify.last_name_maternal = name_parts[2] if len(name_parts) > 2 else ""
                        else:
                            therapist_to_modify.first_name = new_name
                    if new_email:
                        therapist_to_modify.email = new_email
                    if new_phone_number:
                        therapist_to_modify.phone = new_phone_number  # Cambiado de phone_number a phone
                    therapist_to_modify.save()
                    return f"Terapeuta con ID {id} modificado exitosamente."
                except Therapist.DoesNotExist:
                    return f"Error: No se encontró un terapeuta con el ID {id}."
                except Exception as e:
                    return f"Error al modificar terapeuta: {e}"

            def modify_patient_function(id: int, new_name: str = None, new_email: str = None, new_phone_number: str = None) -> str:
                try:
                    patient_to_modify = Patient.objects.get(id=id)
                    if new_name:
                        patient_to_modify.name = new_name
                    if new_email:
                        patient_to_modify.email = new_email
                    if new_phone_number:
                        patient_to_modify.phone_number = new_phone_number
                    patient_to_modify.save()
                    return f"Paciente con ID {id} modificado exitosamente."
                except Patient.DoesNotExist:
                    return f"Error: No se encontró un paciente con el ID {id}."
                except Exception as e:
                    return f"Error al modificar paciente: {e}"

            # Importar las nuevas funciones
            from .views import create_appointment_function, get_today_patients_function, get_today_therapists_function, get_today_appointments_function

            # Declaraciones de herramientas para la IA de Gemini

            tool_declarations = [
                FunctionDeclaration(
                    name='create_therapist',
                    description='Crea un nuevo terapeuta en la base de datos.',
                    parameters={'type': 'object', 'properties': {'name': {'type': 'string'}, 'email': {'type': 'string'}, 'document_number': {'type': 'string'}}, 'required': ['name', 'email', 'document_number']}
                ),
                FunctionDeclaration(
                    name='create_patient',
                    description='Crea un nuevo paciente en la base de datos.',
                    parameters={'type': 'object', 'properties': {'name': {'type': 'string'}, 'email': {'type': 'string'}, 'phone_number': {'type': 'string'}}, 'required': ['name', 'email', 'phone_number']}
                ),
                FunctionDeclaration(
                    name='modify_therapist',
                    description='Modifica el nombre, email o número de teléfono de un terapeuta existente usando su ID.',
                    parameters={'type': 'object', 'properties': {'id': {'type': 'number'}, 'new_name': {'type': 'string'}, 'new_email': {'type': 'string'}, 'new_phone_number': {'type': 'string'}}, 'required': ['id']}
                ),
                FunctionDeclaration(
                    name='modify_patient',
                    description='Modifica el nombre, email o número de teléfono de un paciente existente usando su ID.',
                    parameters={'type': 'object', 'properties': {'id': {'type': 'number'}, 'new_name': {'type': 'string'}, 'new_email': {'type': 'string'}, 'new_phone_number': {'type': 'string'}}, 'required': ['id']}
                ),
                FunctionDeclaration(
                    name='create_appointment',
                    description='Crea una nueva cita médica entre un paciente y un terapeuta.',
                    parameters={'type': 'object', 'properties': {'patient_name': {'type': 'string'}, 'therapist_name': {'type': 'string'}, 'date': {'type': 'string'}, 'time': {'type': 'string'}, 'price': {'type': 'number'}}, 'required': ['patient_name', 'therapist_name', 'date', 'time']}
                ),
                FunctionDeclaration(
                    name='get_today_patients',
                    description='Obtiene la lista de pacientes creados hoy.',
                    parameters={'type': 'object', 'properties': {}}
                ),
                FunctionDeclaration(
                    name='get_today_therapists',
                    description='Obtiene la lista de terapeutas creados hoy.',
                    parameters={'type': 'object', 'properties': {}}
                ),
                FunctionDeclaration(
                    name='get_today_appointments',
                    description='Obtiene la lista de citas programadas para hoy.',
                    parameters={'type': 'object', 'properties': {}}
                )
            ]

            print("Creando modelo Gemini...")
            model = genai.GenerativeModel(
                model_name='gemini-1.5-pro',
                tools=tool_declarations,
                system_instruction="""
                Eres un asistente inteligente para una clínica médica. Tu función es ayudar con la gestión de pacientes, terapeutas y citas.

                IMPORTANTE: Cuando tengas TODA la información necesaria, DEBES usar las funciones disponibles para crear o modificar registros.

                Funciones disponibles:
                1. create_therapist(name, email, document_number) - Crear nuevos terapeutas
                2. create_patient(name, email, phone_number) - Crear nuevos pacientes  
                3. modify_therapist(id, new_name, new_email, new_phone_number) - Modificar terapeutas
                4. modify_patient(id, new_name, new_email, new_phone_number) - Modificar pacientes
                5. create_appointment(patient_name, therapist_name, date, time, price) - Crear citas médicas
                6. get_today_patients() - Ver pacientes creados hoy
                7. get_today_therapists() - Ver terapeutas creados hoy
                8. get_today_appointments() - Ver citas programadas para hoy

                REGLAS IMPORTANTES:
                - Si el usuario proporciona nombre, email y documento/teléfono en un solo mensaje, USA LA FUNCIÓN INMEDIATAMENTE
                - Si falta información, pregunta por ella
                - SIEMPRE usa las funciones cuando tengas los datos completos
                - NO respondas solo con texto cuando puedes ejecutar una acción

                Para PACIENTES necesitas: nombre completo, email, número de teléfono
                Para TERAPEUTAS necesitas: nombre completo, email, número de documento
                Para CITAS necesitas: nombre del paciente, nombre del terapeuta, fecha (YYYY-MM-DD), hora (HH:MM)

                Ejemplos:
                - Usuario: "Crear terapeuta Dr. Juan Pérez, email juan@test.com, DNI 12345678"
                  → USA create_therapist("Dr. Juan Pérez", "juan@test.com", "12345678")
                
                - Usuario: "Crear paciente María García, email maria@test.com, teléfono 987654321"  
                  → USA create_patient("María García", "maria@test.com", "987654321")

                - Usuario: "Programar cita para Ana Lopez con Dr. Juan el 2025-01-20 a las 14:30"
                  → USA create_appointment("Ana Lopez", "Dr. Juan", "2025-01-20", "14:30")

                - Usuario: "¿Cuántos pacientes he creado hoy?"
                  → USA get_today_patients()

                - Usuario: "¿Qué citas tengo programadas para hoy?"
                  → USA get_today_appointments()

                Mantén el contexto de la conversación y usa las funciones cuando corresponda.
                """
            )
            print("Modelo creado exitosamente")
            
            # Obtener historial de chat de la sesión
            print("Obteniendo historial de chat...")
            chat_history = request.session.get('chat_history', [])
            print(f"Historial obtenido: {len(chat_history)} mensajes")
            
            # Convertir historial serializable de vuelta a objetos Content
            history = []
            for msg in chat_history:
                if isinstance(msg, dict) and 'role' in msg and 'parts' in msg:
                    # Reconstruir las partes correctamente
                    parts = []
                    for part in msg['parts']:
                        if 'function_call' in part:
                            # Crear Part con function_call
                            from google.generativeai.types import Part
                            func_call_part = Part(function_call={
                                'name': part['function_call']['name'],
                                'args': part['function_call']['args']
                            })
                            parts.append(func_call_part)
                        elif 'function_response' in part:
                            # Crear Part con function_response
                            from google.generativeai.types import Part
                            func_response_part = Part(function_response={
                                'name': part['function_response']['name'],
                                'response': part['function_response']['response']
                            })
                            parts.append(func_response_part)
                        else:
                            # Texto normal
                            from google.generativeai.types import Part
                            text_part = Part(text=part.get('text', ''))
                            parts.append(text_part)
                    
                    # Crear Content con las partes reconstruidas
                    from google.generativeai.types import Content
                    content = Content(role=msg['role'], parts=parts)
                    history.append(content)
                else:
                    # Si ya es un objeto Content, usarlo directamente
                    history.append(msg)
            
            print("Iniciando chat...")
            chat = model.start_chat(history=history)
            
            print("Procesando mensaje del usuario...")
            try:
                # Intentar decodificar con UTF-8 primero
                body_str = request.body.decode('utf-8')
            except UnicodeDecodeError:
                # Si falla, intentar con latin-1
                body_str = request.body.decode('latin-1')
            
            data = json.loads(body_str)
            user_message = data.get("message", "")
            print(f"Mensaje del usuario: {user_message}")

            print("Enviando mensaje a Gemini...")
            response = chat.send_message(user_message)
            print("Respuesta recibida de Gemini")
            
            # Convertir historial a formato serializable y guardarlo
            print("Guardando historial de chat...")
            serializable_history = []
            for content in chat.history:
                parts = []
                for part in content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        # Preservar function_call
                        parts.append({
                            'function_call': {
                                'name': part.function_call.name,
                                'args': dict(part.function_call.args)
                            }
                        })
                    elif hasattr(part, 'function_response') and part.function_response:
                        # Preservar function_response
                        parts.append({
                            'function_response': {
                                'name': part.function_response.name,
                                'response': part.function_response.response
                            }
                        })
                    else:
                        # Texto normal
                        parts.append({'text': part.text})
                
                serializable_content = {
                    'role': content.role,
                    'parts': parts
                }
                serializable_history.append(serializable_content)
            
            request.session['chat_history'] = serializable_history
            request.session.modified = True
            
            if response.candidates and response.candidates[0].content.parts[0].function_call:
                function_call = response.candidates[0].content.parts[0].function_call
                function_name = function_call.name
                tool_args = function_call.args

                # Ejecutar la función correspondiente
                if function_name == 'create_therapist':
                    tool_response = create_therapist_function(**tool_args)
                elif function_name == 'create_patient':
                    tool_response = create_patient_function(**tool_args)
                elif function_name == 'modify_therapist':
                    tool_response = modify_therapist_function(**tool_args)
                elif function_name == 'modify_patient':
                    tool_response = modify_patient_function(**tool_args)
                elif function_name == 'create_appointment':
                    tool_response = create_appointment_function(**tool_args)
                elif function_name == 'get_today_patients':
                    tool_response = get_today_patients_function()
                elif function_name == 'get_today_therapists':
                    tool_response = get_today_therapists_function()
                elif function_name == 'get_today_appointments':
                    tool_response = get_today_appointments_function()
                else:
                    return JsonResponse({"success": False, "message": f"Función '{function_name}' no implementada."}, status=400)
                
                return JsonResponse({"success": True, "response": tool_response})

            if response.candidates:
                return JsonResponse({"success": True, "response": response.text})

            return JsonResponse({"success": False, "message": "No se recibió una respuesta válida de la IA."}, status=500)

        except Exception as e:
            print(f"ERROR EN CHATBOT: {str(e)}")
            print(f"Tipo de error: {type(e).__name__}")
            import traceback
            print(f"Traceback completo: {traceback.format_exc()}")
            return JsonResponse({"success": False, "message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Método no permitido"}, status=405)

@csrf_exempt
def create_therapist_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            document_number = data.get('document_number')
            
            if not name or not email:
                return JsonResponse({"status": "error", "message": "Name and email are required"}, status=400)
            
            # Usar la función create_therapist_function que ya existe
            result = create_therapist_function_standalone(name, email, document_number)
            return JsonResponse({"status": "success", "response": result})
            
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Método no permitido"}, status=405)

def create_therapist_function_standalone(name: str, email: str, document_number: str = None) -> str:
    try:
        from .models import DocumentType, District, Province, Region
        import random
        
        # Separar el nombre completo en partes
        name_parts = name.strip().split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name_paternal = name_parts[1]
            last_name_maternal = name_parts[2] if len(name_parts) > 2 else ''
        else:
            first_name = name
            last_name_paternal = 'Sin apellido'
            last_name_maternal = ''
        
        # Generar document_number si no se proporciona
        if not document_number:
            document_number = f"DOC{random.randint(10000, 99999)}"
        
        # Obtener valores por defecto para las claves foráneas
        document_type = DocumentType.objects.first()
        district = District.objects.first()
        province = Province.objects.first()
        region = Region.objects.first()
        
        # Crear el terapeuta
        therapist = Therapist.objects.create(
            document_number=document_number,
            first_name=first_name,
            last_name_paternal=last_name_paternal,
            last_name_maternal=last_name_maternal,
            email=email,
            document_type=document_type,
            district=district,
            province=province,
            region=region
        )
        
        return f"Terapeuta '{first_name}' con email '{email}' creado exitosamente"
        
    except Exception as e:
        return f"Error al crear paciente: {str(e)}"

def dashboard_view(request):
    """Vista para servir el dashboard principal"""
    return render(request, 'clinica/dashboard.html')

@csrf_exempt
def get_patients_api(request):
    """API endpoint para obtener todos los pacientes"""
    if request.method == 'GET':
        try:
            patients = Patient.objects.all().order_by('-created_at')
            patients_data = []
            for patient in patients:
                patients_data.append({
                    'id': patient.id,
                    'name': patient.name,
                    'email': patient.email,
                    'phone_number': patient.phone_number,
                    'created_at': patient.created_at.strftime('%Y-%m-%d') if patient.created_at else 'N/A'
                })
            return JsonResponse({'success': True, 'patients': patients_data})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

# Nuevas funciones para Gemini AI

def create_appointment_function(patient_name: str, therapist_name: str, date: str, time: str, price: float = 100.0) -> str:
    """
    Función para crear una nueva cita médica
    Args:
        patient_name: Nombre del paciente
        therapist_name: Nombre del terapeuta
        date: Fecha de la cita (formato YYYY-MM-DD)
        time: Hora de la cita (formato HH:MM)
        price: Precio de la cita (opcional, por defecto 100.0)
    """
    try:
        from datetime import datetime
        
        # Buscar el paciente por nombre
        patient = Patient.objects.filter(name__icontains=patient_name).first()
        if not patient:
            return f"Error: No se encontró un paciente con el nombre '{patient_name}'"
        
        # Buscar el terapeuta por nombre
        therapist = Therapist.objects.filter(
            first_name__icontains=therapist_name.split()[0] if therapist_name.split() else therapist_name
        ).first()
        if not therapist:
            return f"Error: No se encontró un terapeuta con el nombre '{therapist_name}'"
        
        # Combinar fecha y hora para appointment_date
        try:
            appointment_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        except ValueError:
            return f"Error: Formato de fecha u hora inválido. Use YYYY-MM-DD para fecha y HH:MM para hora"
        
        # Crear la cita usando los campos correctos de la base de datos
        from django.db import connection
        cursor = connection.cursor()
        
        cursor.execute("""
            INSERT INTO appointments (
                patient_id, therapist_id, appointment_date, payment, 
                appointment_status, created_at, updated_at, social_benefit
            ) VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), %s)
        """, [
            patient.id,
            therapist.id, 
            appointment_datetime,
            price,
            'scheduled',
            False
        ])
        
        appointment_id = cursor.lastrowid
        
        return f"Cita creada exitosamente: {patient.name} con {therapist.first_name} {therapist.last_name_paternal} el {appointment_datetime.strftime('%d/%m/%Y a las %H:%M')}. ID de cita: {appointment_id}"
        
    except Exception as e:
        return f"Error al crear la cita: {str(e)}"

def get_today_patients_function() -> str:
    """
    Función para obtener la lista de pacientes creados hoy
    """
    try:
        from datetime import date
        
        today = date.today()
        patients_today = Patient.objects.filter(created_at__date=today).order_by('created_at')
        
        if not patients_today.exists():
            return "No se han creado pacientes hoy."
        
        count = patients_today.count()
        
        result = f"📋 Hoy se han creado {count} paciente(s):\n"
        result += "=" * 50 + "\n\n"
        
        for i, patient in enumerate(patients_today, 1):
            result += f"🔹 {i}. PACIENTE: {patient.name}\n"
            result += f"    📧 Email: {patient.email}\n"
            result += f"    📞 Teléfono: {patient.phone_number or 'No especificado'}\n"
            result += f"    🕐 Creado: {patient.created_at.strftime('%H:%M')}\n"
            result += "-" * 40 + "\n"
            result += "\n"  # Salto de línea adicional después de cada paciente
        
        return result
        
    except Exception as e:
        return f"Error al consultar pacientes de hoy: {str(e)}"

def get_today_therapists_function() -> str:
    """
    Función para obtener la lista de terapeutas creados hoy
    """
    try:
        from datetime import date
        
        today = date.today()
        therapists_today = Therapist.objects.filter(created_at__date=today).order_by('created_at')
        
        if not therapists_today.exists():
            return "No se han creado terapeutas hoy."
        
        count = therapists_today.count()
        
        result = f"👨‍⚕️ Hoy se han creado {count} terapeuta(s):\n"
        result += "=" * 50 + "\n\n"
        
        for i, therapist in enumerate(therapists_today, 1):
            full_name = f"{therapist.first_name} {therapist.last_name_paternal} {therapist.last_name_maternal}".strip()
            result += f"🔹 {i}. TERAPEUTA: {full_name}\n"
            result += f"    📧 Email: {therapist.email}\n"
            result += f"    🆔 Documento: {therapist.document_number or 'No especificado'}\n"
            result += f"    📱 Teléfono: {getattr(therapist, 'phone', 'No especificado')}\n"
            result += f"    🕐 Creado: {therapist.created_at.strftime('%H:%M')}\n"
            result += "-" * 40 + "\n"
            result += "\n"  # Salto de línea adicional después de cada terapeuta
        
        return result
        
    except Exception as e:
        return f"Error al consultar terapeutas de hoy: {str(e)}"

def get_today_appointments_function() -> str:
    """
    Función para obtener la lista de citas programadas para hoy
    """
    try:
        from datetime import date
        
        today = date.today()
        # Buscar citas cuya fecha de la cita sea hoy (usando appointment_date)
        from django.db import connection
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT a.id, p.name as patient_name, t.first_name, t.last_name_paternal, 
                   a.appointment_date, a.appointment_status, a.payment
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN therapists t ON a.therapist_id = t.id
            WHERE DATE(a.appointment_date) = %s
            ORDER BY a.appointment_date
        """, [today])
        
        appointments = cursor.fetchall()
        
        if not appointments:
            return "No hay citas programadas para hoy."
        
        count = len(appointments)
        
        result = f"📅 Hay {count} cita(s) programada(s) para hoy:\n"
        result += "=" * 50 + "\n\n"
        
        for i, appointment in enumerate(appointments, 1):
            appointment_id, patient_name, therapist_first, therapist_last, appointment_date, status, payment = appointment
            therapist_name = f"{therapist_first} {therapist_last}".strip()
            time_str = appointment_date.strftime('%H:%M') if appointment_date else 'N/A'
            date_str = appointment_date.strftime('%d/%m/%Y') if appointment_date else 'N/A'
            
            result += f"🔹 {i}. CITA #{appointment_id}\n"
            result += f"    👤 Paciente: {patient_name}\n"
            result += f"    👨‍⚕️ Terapeuta: {therapist_name}\n"
            result += f"    📅 Fecha: {date_str}\n"
            result += f"    🕐 Hora: {time_str}\n"
            result += f"    📊 Estado: {status}\n"
            result += f"    💰 Precio: ${payment}\n"
            result += "-" * 40 + "\n"
            result += "\n"  # Salto de línea adicional después de cada cita
        
        return result
        
    except Exception as e:
        return f"Error al consultar citas de hoy: {str(e)}"

@csrf_exempt
def create_appointment(request):
    """API endpoint para crear una nueva cita"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validar campos requeridos
            required_fields = ['patient_id', 'therapist_id', 'appointment_date', 'payment']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'success': False, 'error': f'Campo requerido: {field}'})
            
            # Verificar que el paciente existe
            try:
                patient = Patient.objects.get(id=data['patient_id'])
            except Patient.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Paciente no encontrado'})
            
            # Verificar que el terapeuta existe
            try:
                therapist = Therapist.objects.get(id=data['therapist_id'])
            except Therapist.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Terapeuta no encontrado'})
            
            # Crear la cita usando los campos correctos de la base de datos
            from django.db import connection
            cursor = connection.cursor()
            
            cursor.execute("""
                INSERT INTO appointments (
                    patient_id, therapist_id, appointment_date, payment, 
                    appointment_status, created_at, updated_at, social_benefit
                ) VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), %s)
            """, [
                data['patient_id'],
                data['therapist_id'], 
                data['appointment_date'],
                data['payment'],
                data.get('appointment_status', 'scheduled'),
                data.get('social_benefit', False)
            ])
            
            appointment_id = cursor.lastrowid
            
            return JsonResponse({
                'success': True, 
                'message': 'Cita creada exitosamente',
                'appointment_id': appointment_id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'JSON inválido'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@csrf_exempt
def get_therapists_api(request):
    """API endpoint para obtener todos los terapeutas"""
    if request.method == 'GET':
        try:
            therapists = Therapist.objects.all().order_by('-created_at')
            therapists_data = []
            for therapist in therapists:
                therapists_data.append({
                    'id': therapist.id,
                    'name': f"{therapist.first_name} {therapist.last_name_paternal} {therapist.last_name_maternal}".strip(),
                    'email': therapist.email,
                    'document_number': therapist.document_number,
                    'phone': therapist.phone or 'N/A',
                    'is_active': therapist.is_active,
                    'created_at': therapist.created_at.strftime('%Y-%m-%d') if therapist.created_at else 'N/A'
                })
            return JsonResponse({'success': True, 'therapists': therapists_data})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@csrf_exempt
def get_appointments_api(request):
    """API endpoint para obtener todas las citas"""
    if request.method == 'GET':
        try:
            appointments = Appointment.objects.all().order_by('-appointment_date')
            appointments_data = []
            for appointment in appointments:
                appointments_data.append({
                    'id': appointment.id,
                    'patient_name': appointment.patient.name,
                    'therapist_name': f"{appointment.therapist.first_name} {appointment.therapist.last_name_paternal}".strip() if appointment.therapist else "Sin asignar",
                    'date_time': appointment.appointment_date.strftime('%Y-%m-%d %H:%M') if appointment.appointment_date else "Sin fecha",
                    'status': appointment.appointment_status,
                    'payment_status': getattr(appointment.payment_status, 'name', 'Pendiente') if hasattr(appointment, 'payment_status') and appointment.payment_status else 'Pendiente',
                    'price': str(appointment.payment) if appointment.payment else "0.00"
                })
            return JsonResponse({'success': True, 'appointments': appointments_data})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})
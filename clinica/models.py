from django.db import models

# Modelos de referencia básicos
class DocumentType(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'document_types'
        managed = False  # Django no manejará esta tabla

class Region(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'regions'
        managed = False

class Province(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'provinces'
        managed = False

class District(models.Model):
    name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'districts'
        managed = False

class Therapist(models.Model):
    document_number = models.CharField(max_length=20, unique=True, default='TEMP000')
    last_name_paternal = models.CharField(max_length=150, default='Sin apellido')
    last_name_maternal = models.CharField(max_length=150, default='')
    first_name = models.CharField(max_length=150, default='Sin nombre')
    birth_date = models.DateTimeField(null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    personal_reference = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=254)
    address = models.TextField(null=True, blank=True)
    profile_picture = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Foreign keys - ahora con los modelos definidos
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, null=True, blank=True)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name_paternal} {self.last_name_maternal}"

    class Meta:
        db_table = 'therapists'
        managed = False  # Django no manejará esta tabla

class Patient(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, default='')
    document_number = models.CharField(max_length=20, default='TEMP000')
    ocupation = models.CharField(max_length=100, default='Sin especificar')
    health_condition = models.TextField(default='Sin especificar')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    document_type = models.ForeignKey('DocumentType', on_delete=models.CASCADE, default=1)
    district = models.ForeignKey('District', on_delete=models.CASCADE, default=1)
    province = models.ForeignKey('Province', on_delete=models.CASCADE, default=1)
    region = models.ForeignKey('Region', on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'patients'

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Programada'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('cancelled', 'Cancelado'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, null=True, blank=True)
    appointment_date = models.DateTimeField(null=True, blank=True)
    payment = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    appointment_status = models.CharField(max_length=20, default='scheduled')
    payment_status_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient.name} - {self.therapist.first_name if self.therapist else 'Sin terapeuta'} - {self.appointment_date}"

    class Meta:
        managed = False
        db_table = 'appointments'

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    diagnosis = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Registro médico de {self.patient.name}"

    class Meta:
        db_table = 'medical_records'

class Ticket(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    ticket_number = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField()

    def __str__(self):
        return f"Ticket {self.ticket_number} para cita {self.appointment.id}"

    class Meta:
        db_table = 'tickets'
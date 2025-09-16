from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('chatbot/', views.chatbot_api_view, name='chatbot'),
    path('create_therapist/', views.create_therapist_view, name='create_therapist'),
    path('api/patients/', views.get_patients_api, name='get_patients_api'),
    path('api/therapists/', views.get_therapists_api, name='get_therapists_api'),
    path('api/appointments/', views.get_appointments_api, name='get_appointments_api'),
    path('api/appointments/create/', views.create_appointment, name='create_appointment'),
]
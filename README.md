# MCP---CLINICA

Sistema de Gestión Clínica  
MCP---CLINICA es una plataforma desarrollada con Django para la gestión integral de clínicas y centros de salud, orientada a digitalizar procesos administrativos y médicos.

## 🗂️ Repositorio y Ramas

- **Repositorio:** https://github.com/Jean-snt/MCP---CLINICA
- **Ramas principales:**
  - `main`: Rama principal y estable
  - `cesar`: Rama de desarrollo
  - `rep_main`: Rama de respaldo/pruebas
  - `final_de_verdad`: Rama actual de trabajo

## 🚀 Características Principales

- **Gestión de Pacientes, Consultas y Terapeutas**: Modelos y vistas para registrar y administrar pacientes, consultas, terapeutas y personal médico.
- **Panel de administración**: Interfaz de Django Admin para gestión rápida y segura de datos.
- **Configuración lista para producción**: Separación clara de módulos y archivos para facilitar el despliegue.
- **Base de datos MySQL**: Integración nativa, fácilmente adaptable a otros motores.
- **Sistema de migraciones**: Control de cambios en la base de datos mediante migraciones Django.
- **Frontend básico**: Plantillas HTML y archivos estáticos (CSS/JS) para el dashboard.

## 🏗️ Arquitectura del Sistema

### Componentes Principales

- `manage.py`: Punto de entrada principal del sistema Django.
- `Reflexo/`: Configuración central del proyecto (ajustes, URLs, WSGI, ASGI).
- `clinica/`: App principal con modelos, vistas, URLs, migraciones y recursos estáticos.

### Estructura del Proyecto

```text
MCP---CLINICA/
├── manage.py                         # Comando principal de Django
├── requirements.txt                  # Dependencias del proyecto
├── check_db_connection.py            # Script para verificar conexión a la BD
├── check_db.py                       # Script para chequeo general de la BD
├── check_tables.py                   # Script para verificar tablas en la BD
├── check_therapists.py               # Script para verificar terapeutas
├── models.txt                        # Referencia de modelos usados
├── Reflexo/                          # Configuración global del proyecto
│   ├── __init__.py                   # Inicializador del módulo
│   ├── asgi.py                       # Configuración ASGI
│   ├── settings.py                   # Configuración principal de Django
│   ├── urls.py                       # Rutas globales del proyecto
│   ├── wsgi.py                       # Configuración WSGI
│   └── __pycache__/                  # Archivos temporales de Python
├── clinica/                          # App principal de la clínica
│   ├── __init__.py                   # Inicializador de la app
│   ├── admin.py                      # Configuración del admin de Django
│   ├── apps.py                       # Configuración de la app
│   ├── models.py                     # Modelos de datos
│   ├── tests.py                      # Pruebas unitarias
│   ├── urls.py                       # Rutas de la app
│   ├── views.py                      # Vistas de la app
│   ├── migrations/                   # Migraciones de la base de datos
│   ├── static/                       # Archivos estáticos (CSS/JS)
│   │   └── clinica/
│   │       ├── css/
│   │       │   └── dashboard.css     # Estilos del dashboard
│   │       └── js/
│   │           └── dashboard.js      # Scripts JS del dashboard
│   └── templates/                    # Plantillas HTML
│       └── clinica/
│           └── dashboard.html        # Dashboard principal
```

## 🛠️ Tecnologías y Herramientas

- **Backend**: Django 5.x, Python 3.11
- **Base de datos**: MySQL (configurable en settings)
- **Frontend**: HTML, CSS, JavaScript (dashboard básico)
- **Panel de administración**: Django Admin

## 📋 Funcionalidades Detalladas

1. **Gestión de Pacientes, Terapeutas y Consultas**: Modelos y migraciones para entidades clínicas.
2. **Panel de administración**: Gestión de datos desde la interfaz de Django.
3. **Dashboard básico**: Plantilla y recursos estáticos para visualización.
4. **Scripts de chequeo**: Archivos Python para verificar conexión y estado de la base de datos y tablas.
5. **Configuración modular**: Fácil de extender con nuevas apps y funcionalidades.

## 🚀 Instalación y Configuración

### Requisitos Previos

- Python 3.11 o superior
- pip (gestor de paquetes de Python)
- MySQL (o motor compatible)

### Pasos de Instalación

1. Clonar el repositorio:
    ```powershell
    git clone https://github.com/Jean-snt/MCP---CLINICA.git
    cd MCP---CLINICA
    ```
2. Instalar dependencias:
    ```powershell
    pip install -r requirements.txt
    ```
3. Configurar la base de datos en `Reflexo/settings.py`.
4. Ejecutar migraciones:
    ```powershell
    python manage.py migrate
    ```
5. Iniciar el servidor:
    ```powershell
    python manage.py runserver
    ```
6. Acceder al sistema en [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## 📁 Estructura Detallada del Proyecto

- **Reflexo/**: Configuración global del proyecto Django.
- **clinica/**: App principal con modelos, vistas, migraciones, archivos estáticos y plantillas.
- **scripts de chequeo**: Archivos para verificar la conexión y estado de la base de datos (`check_db_connection.py`, `check_db.py`, `check_tables.py`, `check_therapists.py`).

## 🔧 Comandos Útiles

```powershell
# Iniciar servidor de desarrollo
python manage.py runserver

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

## 📄 Licencia

Este proyecto es solo para fines educativos y de desarrollo.
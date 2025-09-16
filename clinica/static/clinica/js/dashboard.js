// Dashboard JavaScript - Funcionalidad completa
class Dashboard {
    constructor() {
        this.currentSection = 'overview';
        this.chatMessages = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadInitialData();
        this.initializeChatbot();
    }

    setupEventListeners() {
        // Navegación del sidebar
        document.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.getAttribute('data-section');
                this.switchSection(section);
            });
        });

        // Toggle sidebar en móvil
        const sidebarToggle = document.querySelector('.sidebar-toggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                document.querySelector('.sidebar').classList.toggle('active');
            });
        }

        // Botones de acción
        document.getElementById('add-patient-btn')?.addEventListener('click', () => {
            this.openModal('patient-modal');
        });

        document.getElementById('add-therapist-btn')?.addEventListener('click', () => {
            this.openModal('therapist-modal');
        });

        // Cerrar modales
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.closeModal(e.target.closest('.modal-overlay').id);
            });
        });

        // Cerrar modal al hacer clic fuera
        document.querySelectorAll('.modal-overlay').forEach(overlay => {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    this.closeModal(overlay.id);
                }
            });
        });

        // Formularios
        document.getElementById('patient-form')?.addEventListener('submit', (e) => {
            this.handlePatientForm(e);
        });

        document.getElementById('therapist-form')?.addEventListener('submit', (e) => {
            this.handleTherapistForm(e);
        });

        // Chatbot
        document.getElementById('send-button')?.addEventListener('click', () => {
            this.sendMessage();
        });

        document.getElementById('chat-input')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        // Botones rápidos del chat
        document.querySelectorAll('.quick-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.getAttribute('data-action');
                this.handleQuickAction(action);
            });
        });
    }

    switchSection(section) {
        // Actualizar navegación activa
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // Mostrar sección correspondiente
        document.querySelectorAll('.content-section').forEach(sec => {
            sec.classList.remove('active');
        });
        
        // Mapear las secciones a sus IDs correctos
        const sectionId = section === 'overview' ? 'overview' : section;
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // Actualizar título
        const titles = {
            'overview': 'Dashboard General',
            'patients': 'Gestión de Pacientes',
            'therapists': 'Gestión de Terapeutas',
            'appointments': 'Citas y Horarios',
            'chatbot': 'Asistente Virtual'
        };
        document.querySelector('.page-title').textContent = titles[section] || 'Dashboard';

        this.currentSection = section;

        // Cargar datos específicos de la sección
        this.loadSectionData(section);
    }

    async loadInitialData() {
        try {
            // Cargar estadísticas generales
            await this.loadStats();
            
            // Cargar actividad reciente
            await this.loadRecentActivity();
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showNotification('Error al cargar los datos iniciales', 'error');
        }
    }

    async loadStats() {
        try {
            // Cargar datos reales de la base de datos
            const [patientsResponse, therapistsResponse, appointmentsResponse] = await Promise.all([
                fetch('/api/patients/'),
                fetch('/api/therapists/'),
                fetch('/api/appointments/')
            ]);

            const patientsData = await patientsResponse.json();
            const therapistsData = await therapistsResponse.json();
            const appointmentsData = await appointmentsResponse.json();

            // Calcular estadísticas reales
            const stats = {
                patients: patientsData.success ? patientsData.patients.length : 0,
                therapists: therapistsData.success ? therapistsData.therapists.length : 0,
                appointments: appointmentsData.success ? appointmentsData.appointments.length : 0,
                revenue: appointmentsData.success ? 
                    appointmentsData.appointments.reduce((total, apt) => total + parseFloat(apt.price || 0), 0) : 0
            };

            // Actualizar las tarjetas de estadísticas
            document.querySelector('.stat-card.patients h3').textContent = stats.patients;
            document.querySelector('.stat-card.therapists h3').textContent = stats.therapists;
            document.querySelector('.stat-card.appointments h3').textContent = stats.appointments;
            document.querySelector('.stat-card.revenue h3').textContent = `$${stats.revenue.toLocaleString()}`;

        } catch (error) {
            console.error('Error loading stats:', error);
            // En caso de error, mostrar 0 en lugar de números aleatorios
            document.querySelector('.stat-card.patients h3').textContent = '0';
            document.querySelector('.stat-card.therapists h3').textContent = '0';
            document.querySelector('.stat-card.appointments h3').textContent = '0';
            document.querySelector('.stat-card.revenue h3').textContent = '$0';
        }
    }

    async loadRecentActivity() {
        const activities = [
            { icon: 'fas fa-user-plus', text: 'Nuevo paciente registrado: María González', time: 'Hace 5 min' },
            { icon: 'fas fa-calendar-check', text: 'Cita completada con Dr. Rodríguez', time: 'Hace 15 min' },
            { icon: 'fas fa-user-md', text: 'Nuevo terapeuta: Dr. Carlos Martínez', time: 'Hace 1 hora' },
            { icon: 'fas fa-comments', text: 'Consulta por chatbot respondida', time: 'Hace 2 horas' }
        ];

        const activityList = document.querySelector('.activity-list');
        if (activityList) {
            activityList.innerHTML = activities.map(activity => `
                <div class="activity-item">
                    <i class="${activity.icon}"></i>
                    <span>${activity.text}</span>
                    <small>${activity.time}</small>
                </div>
            `).join('');
        }
    }

    async loadSectionData(section) {
        switch (section) {
            case 'patients':
                await this.loadPatients();
                break;
            case 'therapists':
                await this.loadTherapists();
                break;
            case 'appointments':
                await this.loadAppointments();
                break;
        }
    }

    async loadPatients() {
        try {
            const response = await fetch('/api/patients/');
            const data = await response.json();
            
            if (data.success) {
                const patients = data.patients;
                const tableBody = document.querySelector('#patients-table');
                if (tableBody) {
                    tableBody.innerHTML = patients.map(patient => `
                        <tr>
                            <td>${patient.name}</td>
                            <td>${patient.email}</td>
                            <td>${patient.phone_number}</td>
                            <td>${patient.created_at}</td>
                            <td>
                                <button class="btn btn-sm btn-primary" onclick="dashboard.editPatient(${patient.id})">
                                    <i class="fas fa-edit"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('');
                }
            } else {
                console.error('Error loading patients:', data.error);
                // Mostrar datos de ejemplo si hay error
                this.loadPatientsExample();
            }
        } catch (error) {
            console.error('Error loading patients:', error);
            // Mostrar datos de ejemplo si hay error
            this.loadPatientsExample();
        }
    }

    loadPatientsExample() {
        const patients = [
            { id: 1, name: 'María González', email: 'maria@email.com', phone_number: '123-456-7890', created_at: '2024-01-15' },
            { id: 2, name: 'Juan Pérez', email: 'juan@email.com', phone_number: '098-765-4321', created_at: '2024-01-14' },
            { id: 3, name: 'Ana Rodríguez', email: 'ana@email.com', phone_number: '555-123-4567', created_at: '2024-01-13' }
        ];

        const tableBody = document.querySelector('#patients-table');
        if (tableBody) {
            tableBody.innerHTML = patients.map(patient => `
                <tr>
                    <td>${patient.name}</td>
                    <td>${patient.email}</td>
                    <td>${patient.phone_number}</td>
                    <td>${patient.created_at}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="dashboard.editPatient(${patient.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        }
    }

    async loadTherapists() {
        try {
            const response = await fetch('/api/therapists/');
            const data = await response.json();
            
            if (data.success) {
                const therapists = data.therapists;
                const tableBody = document.querySelector('#therapists-table');
                if (tableBody) {
                    tableBody.innerHTML = therapists.map(therapist => `
                        <tr>
                            <td>${therapist.name}</td>
                            <td>${therapist.email}</td>
                            <td>${therapist.phone}</td>
                            <td><span class="status ${therapist.is_active ? 'activo' : 'inactivo'}">${therapist.is_active ? 'Activo' : 'Inactivo'}</span></td>
                            <td>
                                <button class="btn btn-sm btn-primary" onclick="dashboard.editTherapist(${therapist.id})">
                                    <i class="fas fa-edit"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('');
                }
            } else {
                console.error('Error loading therapists:', data.error);
                // Mostrar datos de ejemplo si hay error
                this.loadTherapistsExample();
            }
        } catch (error) {
            console.error('Error loading therapists:', error);
            // Mostrar datos de ejemplo si hay error
            this.loadTherapistsExample();
        }
    }

    loadTherapistsExample() {
        const therapists = [
            { id: 1, name: 'Dr. Carlos Martínez', email: 'carlos@test.com', phone: '123-456-7890', is_active: true },
            { id: 2, name: 'Dra. Laura Sánchez', email: 'laura@test.com', phone: '098-765-4321', is_active: true },
            { id: 3, name: 'Dr. Miguel Torres', email: 'miguel@test.com', phone: '555-123-4567', is_active: false }
        ];

        const tableBody = document.querySelector('#therapists-table');
        if (tableBody) {
            tableBody.innerHTML = therapists.map(therapist => `
                <tr>
                    <td>${therapist.name}</td>
                    <td>${therapist.email}</td>
                    <td>${therapist.phone}</td>
                    <td><span class="status ${therapist.is_active ? 'activo' : 'inactivo'}">${therapist.is_active ? 'Activo' : 'Inactivo'}</span></td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="dashboard.editTherapist(${therapist.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        }
    }

    async loadAppointments() {
        try {
            const response = await fetch('/api/appointments/');
            const data = await response.json();
            
            if (data.success) {
                const appointments = data.appointments;
                const appointmentsGrid = document.querySelector('.appointments-grid');
                if (appointmentsGrid) {
                    appointmentsGrid.innerHTML = appointments.map(appointment => `
                        <div class="appointment-card">
                            <div class="appointment-time">${appointment.date_time}</div>
                            <div class="appointment-info">
                                <h4>${appointment.patient_name}</h4>
                                <p>con ${appointment.therapist_name}</p>
                                <small>Precio: $${appointment.price}</small>
                            </div>
                            <span class="appointment-status ${appointment.status}">${appointment.status}</span>
                        </div>
                    `).join('');
                }
            } else {
                console.error('Error loading appointments:', data.error);
                // Mostrar datos de ejemplo si hay error
                this.loadAppointmentsExample();
            }
        } catch (error) {
            console.error('Error loading appointments:', error);
            // Mostrar datos de ejemplo si hay error
            this.loadAppointmentsExample();
        }
    }

    loadAppointmentsExample() {
        const appointments = [
            { id: 1, date_time: '2024-01-15 09:00', patient_name: 'María González', therapist_name: 'Dr. Carlos Martínez', status: 'scheduled', price: '50.00' },
            { id: 2, date_time: '2024-01-15 10:30', patient_name: 'Juan Pérez', therapist_name: 'Dra. Laura Sánchez', status: 'completed', price: '60.00' },
            { id: 3, date_time: '2024-01-15 14:00', patient_name: 'Ana Rodríguez', therapist_name: 'Dr. Miguel Torres', status: 'cancelled', price: '55.00' }
        ];

        const appointmentsGrid = document.querySelector('.appointments-grid');
        if (appointmentsGrid) {
            appointmentsGrid.innerHTML = appointments.map(appointment => `
                <div class="appointment-card">
                    <div class="appointment-time">${appointment.date_time}</div>
                    <div class="appointment-info">
                        <h4>${appointment.patient_name}</h4>
                        <p>con ${appointment.therapist_name}</p>
                        <small>Precio: $${appointment.price}</small>
                    </div>
                    <span class="appointment-status ${appointment.status}">${appointment.status}</span>
                </div>
            `).join('');
        }
    }

    // Funciones del Chatbot
    initializeChatbot() {
        this.addBotMessage('¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?');
    }

    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Agregar mensaje del usuario
        this.addUserMessage(message);
        input.value = '';
        
        // Mostrar indicador de escritura
        this.showTypingIndicator();
        
        try {
            const csrfToken = this.getCSRFToken();
            console.log('CSRF Token:', csrfToken); // Debug
            
            const response = await fetch('/api/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ message: message })
            });
            
            console.log('Response status:', response.status); // Debug
            const data = await response.json();
            console.log('Response data:', data); // Debug
            
            // Ocultar indicador de escritura
            this.hideTypingIndicator();
            
            if (data.success) {
                this.addBotMessage(data.response);
                
                // Manejar acciones especiales del bot
                if (data.actions) {
                    this.handleBotActions(data.actions);
                }
            } else {
                this.addBotMessage('Lo siento, hubo un error al procesar tu mensaje.');
                console.error('Error from server:', data);
            }
        } catch (error) {
            console.error('Network error:', error);
            this.hideTypingIndicator();
            this.addBotMessage('Error de conexión. Por favor, intenta de nuevo.');
        }
    }

    addUserMessage(message) {
        const messagesContainer = document.querySelector('.chat-messages');
        const messageElement = document.createElement('div');
        messageElement.className = 'message user-message';
        messageElement.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-user"></i>
            </div>
            <div class="message-content">${this.escapeHtml(message)}</div>
        `;
        messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    addBotMessage(message) {
        const messagesContainer = document.querySelector('.chat-messages');
        const messageElement = document.createElement('div');
        messageElement.className = 'message bot-message';
        
        // Escapar HTML y luego convertir saltos de línea a <br>
        const escapedMessage = this.escapeHtml(message);
        const formattedMessage = escapedMessage.replace(/\n/g, '<br>');
        
        messageElement.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">${formattedMessage}</div>
        `;
        messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        const messagesContainer = document.querySelector('.chat-messages');
        const typingElement = document.createElement('div');
        typingElement.className = 'message bot-message typing-indicator';
        typingElement.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="loading"></div>
                Escribiendo...
            </div>
        `;
        messagesContainer.appendChild(typingElement);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    scrollToBottom() {
        const messagesContainer = document.querySelector('.chat-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    handleQuickAction(action) {
        const actions = {
            'create-patient': '¿Puedes ayudarme a registrar un nuevo paciente?',
            'create-therapist': '¿Cómo puedo agregar un nuevo terapeuta?',
            'schedule-appointment': '¿Puedes ayudarme a programar una cita?',
            'view-stats': '¿Puedes mostrarme las estadísticas del día?'
        };

        const message = actions[action];
        if (message) {
            document.getElementById('chat-input').value = message;
            this.sendMessage();
        }
    }

    handleBotActions(actions) {
        actions.forEach(action => {
            switch (action.type) {
                case 'switch_section':
                    this.switchSection(action.section);
                    break;
                case 'open_modal':
                    this.openModal(action.modal);
                    break;
                case 'refresh_data':
                    this.loadSectionData(this.currentSection);
                    break;
            }
        });
    }

    // Funciones de Modal
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
            
            // Limpiar formularios
            const form = modal.querySelector('form');
            if (form) {
                form.reset();
            }
        }
    }

    // Manejo de formularios
    async handlePatientForm(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const patientData = Object.fromEntries(formData);

        try {
            const response = await fetch('/api/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    message: `Crear paciente: ${patientData.name}`,
                    action: 'create_patient',
                    data: patientData
                })
            });

            const result = await response.json();
            
            if (result.status === 'success') {
                this.showNotification('Paciente creado exitosamente', 'success');
                this.closeModal('patient-modal');
                this.loadPatients();
            } else {
                this.showNotification('Error al crear paciente', 'error');
            }

        } catch (error) {
            console.error('Error creating patient:', error);
            this.showNotification('Error de conexión', 'error');
        }
    }

    async handleTherapistForm(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const therapistData = Object.fromEntries(formData);

        try {
            const response = await fetch('/api/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    message: `Crear terapeuta: ${therapistData.name}`,
                    action: 'create_therapist',
                    data: therapistData
                })
            });

            const result = await response.json();
            
            if (result.status === 'success') {
                this.showNotification('Terapeuta creado exitosamente', 'success');
                this.closeModal('therapist-modal');
                this.loadTherapists();
            } else {
                this.showNotification('Error al crear terapeuta', 'error');
            }

        } catch (error) {
            console.error('Error creating therapist:', error);
            this.showNotification('Error de conexión', 'error');
        }
    }

    // Funciones de utilidad
    getCSRFToken() {
        // Primero intentar obtener el token del input hidden
        let token = document.querySelector('[name=csrfmiddlewaretoken]');
        if (token) {
            return token.value;
        }
        
        // Si no existe, intentar obtenerlo de las cookies
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        
        // Si no se encuentra, devolver cadena vacía
        console.warn('CSRF token not found');
        return '';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showNotification(message, type = 'info') {
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;

        // Agregar estilos si no existen
        if (!document.querySelector('#notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'notification-styles';
            styles.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    padding: 1rem;
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                    z-index: 3000;
                    min-width: 300px;
                    animation: slideInRight 0.3s ease-out;
                }
                .notification-success { border-left: 4px solid #4ecdc4; }
                .notification-error { border-left: 4px solid #ff6b6b; }
                .notification-info { border-left: 4px solid #667eea; }
                .notification-content { display: flex; align-items: center; gap: 0.5rem; flex: 1; }
                .notification-close { background: none; border: none; cursor: pointer; }
                @keyframes slideInRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(styles);
        }

        // Agregar al DOM
        document.body.appendChild(notification);

        // Manejar cierre
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });

        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    // Funciones de edición (placeholder)
    editPatient(id) {
        console.log('Edit patient:', id);
        this.showNotification('Función de edición en desarrollo', 'info');
    }

    editTherapist(id) {
        console.log('Edit therapist:', id);
        this.showNotification('Función de edición en desarrollo', 'info');
    }
}

// Inicializar dashboard cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});

// Exportar para uso global
window.Dashboard = Dashboard;
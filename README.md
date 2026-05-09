# 🏥 RedCuidado LMS 
### Plataforma de Capacitación Inteligente para ONGs y ELEAM

[![Deploy with Vercel](https://vercel.com/button)](https://red-cuidado.vercel.app/)
[![Django](https://img.shields.io/badge/Framework-Django%205.0-092e20?logo=django)](https://www.djangoproject.com/)
[![Supabase](https://img.shields.io/badge/Database-Supabase%20(PostgreSQL)-3ecf8e?logo=supabase)](https://supabase.com/)

**RedCuidado** es una solución integral de gestión del aprendizaje (LMS) diseñada específicamente para Establecimientos de Larga Estadía para Adultos Mayores (ELEAM). La plataforma optimiza la formación continua del personal de salud y cuidado, garantizando el cumplimiento de estándares y la mejora en la calidad del servicio.

🔗 **Demo en Vivo:** [https://red-cuidado.vercel.app/](https://red-cuidado.vercel.app/)

---

## ✨ Características Principales

### 👨‍💼 Gestión Multi-Rol
- **Administradores:** Control total sobre el personal, áreas de trabajo y métricas globales.
- **Profesores:** Creación de contenido pedagógico, gestión de módulos multimedia y diseño de evaluaciones.
- **Colaboradores:** Acceso intuitivo a cursos, seguimiento de progreso personal y obtención de certificados.

### 📊 Dashboard de Analítica Avanzada
- **Visualización en tiempo real:** Gráficos dinámicos (Chart.js) que muestran la evolución mensual de capacitaciones.
- **Métricas por Sede:** Comparativa de desempeño entre sedes (Hualpén, Coyhaique).
- **Control de Completitud:** Seguimiento detallado por área de trabajo (Enfermería, Kinesiología, Nutrición, etc.).

### 📚 Experiencia de Aprendizaje (LXP)
- **Multimedia:** Soporte para videos, PDF y visor integrado de Microsoft Office Online para presentaciones PPTX.
- **Evaluaciones Inteligentes:** Exámenes con corrección automática y requisitos de puntaje mínimo.
- **Gamificación Ligera:** Sistema de "Pinning" para fijar cursos prioritarios en el inicio del usuario.
- **Calendario Integrado:** Gestión de plazos y fechas de inicio mediante FullCalendar.

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
| --- | --- |
| **Backend** | Python / Django |
| **Base de Datos** | PostgreSQL (vía Supabase) |
| **Almacenamiento (S3)** | Supabase Storage (CORS Optimized) |
| **Frontend** | Tailwind CSS / Lucide Icons |
| **Gráficos** | Chart.js / FullCalendar |
| **Despliegue** | Vercel (Edge Functions / Serverless) |

---

## 📁 Estructura del Proyecto

```text
RedCuidado/
├── RedCuidado/           # Configuración principal de Django
├── lms/                  # Aplicación principal (Vistas, Modelos, Templates)
│   ├── static/           # Activos (CSS, JS, Imágenes)
│   ├── templates/        # Plantillas HTML con Tailwind
│   └── templatetags/     # Filtros personalizados (lms_extras)
├── staticfiles/          # Recopilación de estáticos para producción
├── vercel.json           # Configuración de despliegue Serverless
├── populate_data.py      # Script de generación de datos dinámicos
└── requirements.txt      # Dependencias del proyecto
```

---

## 🚀 Instalación y Configuración Local

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/PapConAbrilar/RedCuidado.git
   cd RedCuidado
   ```

2. **Configurar Entorno Virtual:**
   ```bash
   python -m venv env
   source env/bin/activate  # En Linux/Mac
   pip install -r requirements.txt
   ```

3. **Variables de Entorno (.env):**
   Crea un archivo `.env` en la raíz con las siguientes credenciales:
   ```env
   DB_NAME=postgres
   DB_USER=postgres.xxxx
   DB_PASSWORD=xxxx
   DB_HOST=xxxx.supabase.co
   DB_PORT=5432
   ```

4. **Ejecutar Migraciones y Servidor:**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

---

## 🛡️ Seguridad y Roles

La plataforma implementa un sistema robusto de permisos mediante decoradores personalizados:
- `@admin_required`: Acceso exclusivo para directores y administradores de sistema.
- `@staff_required`: Permisos para creación y edición de material educativo.
- `@login_required`: Acceso restringido para colaboradores autenticados.

---

## 👥 Equipo de Desarrollo

*   **Benjamín Pinto**
*   **Benjamín Levitt**
*   **Ian Spikin**

---
© 2026 RedCuidado - Innovación en el Cuidado del Adulto Mayor.

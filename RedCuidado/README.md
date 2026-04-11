# RedCuidado - Platforma LMS para el Cuidado del Adulto Mayor

Este proyecto es un Sistema de Gestión de Aprendizaje (LMS) dinámico y moderno diseñado para una ONG dedicada al cuidado de personas mayores. Permite la gestión de cursos, módulos y contenidos multimedia con una experiencia de usuario premium.

## 🚀 Arquitectura del Proyecto

El sistema está construido sobre **Django**, siguiendo el patrón Modelo-Vista-Plantilla (MVT), lo que garantiza una separación clara entre la lógica de negocio, los datos y la interfaz de usuario.

### 🧩 Lógica de Datos (Modelos)
Ubicada en `lms/models.py`, la estructura es jerárquica y relacional:
- **Course**: El núcleo del sistema. Soporta imágenes locales y externas (Unsplash).
- **Module**: Organiza el curso en unidades temáticas.
- **Content**: Soporta múltiples tipos de medios:
  - **Video**: Reproducción nativa.
  - **Documentos (PDF/PPT)**: Visor embebido.
  - **Texto**: Lectura directa con formato básico.
- **Progress Tracking**: Modelos `Enrollment` y `ContentProgress` que registran el avance individual de cada empleado de forma automática.
- **Work Areas**: Permite segmentar cursos por áreas de trabajo (ej. Enfermería, Administración).

### 🛠️ Herramientas y Tecnologías Utilizadas

1.  **Django (Python Framework)**: Utilizado por su robustez, sistema de seguridad integrado y administración de base de datos simplificada.
2.  **SortableJS**: Implementado en el panel de gestión para permitir el reordenamiento de módulos y secciones mediante **Drag-and-Drop** (Arrastrar y Soltar), lo que facilita enormemente la edición para administradores.
3.  **Lucide Icons**: Una librería de iconos moderna y ligera que mantiene la consistencia visual en toda la plataforma.
4.  **Vanilla CSS & Utility Classes**: Se utilizó un sistema de diseño basado en clases de utilidad (estilo Tailwind) para garantizar que la interfaz sea rápida, sin dependencias pesadas y con una estética premium de alta fidelidad.
5.  **AJAX / Fetch API**: Utilizado para las actualizaciones de orden en tiempo real y seguimiento de progreso sin recargar la página.

## 📈 Potencial de Expansión

La arquitectura ha sido diseñada para ser modular, lo que permite escalar el proyecto fácilmente:

*   **Evaluaciones y Exámenes**: Los modelos `Test`, `Question` y `Answer` ya existen en la base de datos. El siguiente paso natural es integrarlos en el **Course Player** para permitir certificaciones.
*   **Certificados Automáticos**: Gracias al sistema de `ContentProgress`, se puede implementar la generación de PDFs de certificados en cuanto un usuario complete el 100% de los módulos.
*   **API para App Móvil**: Al estar basado en Django, es trivial añadir *Django Rest Framework* para servir el contenido a una aplicación nativa de Android o iOS.
*   **Analíticas para Administradores**: La base de datos registra cada interacción, lo que permite crear dashboards de rendimiento en el `ReportsDashboard` para ver qué áreas o empleados necesitan más apoyo.

## ⚙️ Instalación y Uso

1.  Asegúrese de tener el entorno virtual activo: `source env/bin/activate`.
2.  Ejecute las migraciones: `python manage.py migrate`.
3.  Inicie el servidor de desarrollo: `python manage.py runserver`.
4.  Utilice los scripts de población (`populate_courses.py`) para cargar datos de prueba iniciales.

---
*Desarrollado para RedCuidado - Innovando en el cuidado humano.*

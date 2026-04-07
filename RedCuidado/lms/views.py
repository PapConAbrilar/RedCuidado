from django.shortcuts import render

# Mock data for courses
COURSES = [
    {
        'id': 1,
        'title': 'Fundamentos del Cuidado del Paciente',
        'courseCode': 'ELD 101',
        'image': 'https://images.unsplash.com/photo-1708461859488-2a0c081ff826?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxlbGRlcmx5JTIwY2FyZSUyMHRyYWluaW5nJTIwbnVyc2V8ZW58MXx8fHwxNzczOTY0MTM2fDA&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
        'id': 2,
        'title': 'Protocolos de Seguridad y Prevención de Caídas',
        'courseCode': 'SAF 205',
        'image': 'https://images.unsplash.com/photo-1758691462413-b07dee2933fe?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzZW5pb3IlMjBwYXRpZW50JTIwc2FmZXR5JTIwbWVkaWNhbHxlbnwxfHx8fDE3NzM5NjQxMzZ8MA&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
        'id': 3,
        'title': 'Cuidado de Demencia y Memoria',
        'courseCode': 'DEM 310',
        'image': 'https://images.unsplash.com/photo-1738454738501-7e6626ccfcd2?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxkZW1lbnRpYSUyMGNhcmUlMjBlbGRlcmx5fGVufDF8fHx8MTc3Mzk2NDEzN3ww&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
        'id': 4,
        'title': 'Nutrición y Planificación de Comidas para Personas Mayores',
        'courseCode': 'NUT 150',
        'image': 'https://images.unsplash.com/photo-1765200231320-987437f4acc5?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxudXRyaXRpb24lMjBoZWFsdGh5JTIwZm9vZCUyMGVsZGVybHl8ZW58MXx8fHwxNzczOTY0MTM3fDA&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
        'id': 5,
        'title': 'Habilidades de Comunicación Efectiva',
        'courseCode': 'COM 180',
        'image': 'https://images.unsplash.com/photo-1758691463331-2ac00e6f676f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb21tdW5pY2F0aW9uJTIwc2tpbGxzJTIwaGVhbHRoY2FyZXxlbnwxfHx8fDE3NzM5NjQxMzd8MA&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
        'id': 6,
        'title': 'Respuesta de Emergencia y Primeros Auxilios',
        'courseCode': 'EMR 220',
        'image': 'https://images.unsplash.com/photo-1766502715616-374da81c2a9c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxlbWVyZ2VuY3klMjByZXNwb25zZSUyMG1lZGljYWwlMjB0cmFpbmluZ3xlbnwxfHx8fDE3NzM5NjQxMzh8MA&ixlib=rb-4.1.0&q=80&w=1080',
    },
]

def login_view(request):
    return render(request, 'lms/login.html')

def home_view(request):
    context = {
        'courses': COURSES,
        'active_menu': 'homepage',
        'active_portal': request.GET.get('portal', 'Portal de Empleados')
    }
    return render(request, 'lms/home.html', context)

def course_detail_view(request, course_id):
    course = next((c for c in COURSES if c['id'] == course_id), COURSES[0])
    context = {
        'course': course,
        'active_menu': 'courses',
        'active_portal': request.GET.get('portal', 'Portal de Empleados')
    }
    return render(request, 'lms/course_detail.html', context)

def reports_view(request):
    context = {
        'active_menu': 'reports',
        'active_portal': request.GET.get('portal', 'Portal de Administrador')
    }
    return render(request, 'lms/reports_dashboard.html', context)

def calendar_view(request):
    context = {
        'active_menu': 'calendar',
        'active_portal': request.GET.get('portal', 'Portal de Empleados')
    }
    return render(request, 'lms/calendar.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Course

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    error = None
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error = "Usuario o contraseña incorrectos."
            
    return render(request, 'lms/login.html', {'error': error})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home_view(request):
    # Fetch actual courses from DB
    courses = Course.objects.all()
    context = {
        'courses': courses,
        'active_menu': 'homepage',
    }
    return render(request, 'lms/home.html', context)

@login_required
def course_detail_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    context = {
        'course': course,
        'active_menu': 'courses',
    }
    return render(request, 'lms/course_detail.html', context)

@login_required
def reports_view(request):
    # Only Admin and Profesor can access
    if not request.user.groups.filter(name__in=['Administrador', 'Profesor']).exists():
        raise PermissionDenied("No tienes permisos para ver esta página.")
        
    context = {
        'active_menu': 'reports',
    }
    return render(request, 'lms/reports_dashboard.html', context)

@login_required
def groups_view(request):
    from django.contrib.auth.models import User
    
    users = User.objects.select_related('profile__work_area').prefetch_related('enrollments__course').all()
    
    context = {
        'users': users,
        'active_menu': 'groups',
    }
    return render(request, 'lms/groups.html', context)

@login_required
def calendar_view(request):
    context = {
        'active_menu': 'calendar',
    }
    return render(request, 'lms/calendar.html', context)

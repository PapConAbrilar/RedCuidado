from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from functools import wraps
from .models import Course, Module, Content, ContentProgress, Enrollment
from .forms import CourseForm, ModuleForm, ContentForm

def staff_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or request.user.groups.filter(name__in=['Administrador', 'Profesor']).exists():
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

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
    modules = course.modules.all().prefetch_related('contents')
    context = {
        'course': course,
        'modules': modules,
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

# --------- COURSE MANAGEMENT ---------

@staff_required
def course_create_view(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save()
            return redirect('course_manage', course_id=course.id)
    else:
        form = CourseForm()
    return render(request, 'lms/course_form.html', {'form': form, 'title': 'Crear Nuevo Curso'})

@staff_required
def course_edit_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_manage', course_id=course.id)
    else:
        form = CourseForm(instance=course)
    return render(request, 'lms/course_form.html', {'form': form, 'title': f'Editar {course.title}'})

@staff_required
def course_manage_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    modules = course.modules.all().prefetch_related('contents')
    context = {
        'course': course,
        'modules': modules,
        'active_menu': 'courses',
    }
    return render(request, 'lms/course_manage.html', context)

@staff_required
def module_create_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            return redirect('course_manage', course_id=course.id)
    else:
        form = ModuleForm()
    return render(request, 'lms/module_form.html', {'form': form, 'course': course})

@staff_required
def content_create_view(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        form = ContentForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.save(commit=False)
            content.module = module
            content.save()
            return redirect('course_manage', course_id=module.course.id)
    else:
        form = ContentForm()
    return render(request, 'lms/content_form.html', {'form': form, 'module': module})

@staff_required
@require_POST
def reorder_modules(request, course_id):
    order_ids = request.POST.getlist('order[]')
    for i, mid in enumerate(order_ids):
        Module.objects.filter(id=mid, course_id=course_id).update(order=i)
    return JsonResponse({'status': 'ok'})

@staff_required
@require_POST
def reorder_contents(request, module_id):
    order_ids = request.POST.getlist('order[]')
    for i, cid in enumerate(order_ids):
        Content.objects.filter(id=cid, module_id=module_id).update(order=i)
    return JsonResponse({'status': 'ok'})

@login_required
def learning_view(request, course_id, content_id=None):
    course = get_object_or_404(Course, id=course_id)
    modules = course.modules.all().prefetch_related('contents').order_by('order')
    
    # Flatten all content items for navigation
    all_content = []
    for m in modules:
        for c in m.contents.all().order_by('order'):
            all_content.append(c)
            
    if not all_content:
        return redirect('course_detail', course_id=course.id)
        
    if content_id:
        current_content = get_object_or_404(Content, id=content_id)
    else:
        current_content = all_content[0]
        
    # Mark as completed
    ContentProgress.objects.get_or_create(user=request.user, content=current_content, defaults={'is_completed': True})
    
    # Get all completed content IDs for this course
    completed_ids = ContentProgress.objects.filter(
        user=request.user, 
        content__module__course=course, 
        is_completed=True
    ).values_list('content_id', flat=True)
    
    # Navigation
    current_index = -1
    for i, c in enumerate(all_content):
        if c.id == current_content.id:
            current_index = i
            break
            
    prev_content = all_content[current_index - 1] if current_index > 0 else None
    next_content = all_content[current_index + 1] if current_index < len(all_content) - 1 else None
    
    context = {
        'course': course,
        'modules': modules,
        'current_content': current_content,
        'prev_content': prev_content,
        'next_content': next_content,
        'completed_ids': completed_ids,
        'active_menu': 'courses',
    }
    return render(request, 'lms/learning.html', context)

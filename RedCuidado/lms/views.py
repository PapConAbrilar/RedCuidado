from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Max
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from functools import wraps
from .models import Course, Module, Content, ContentProgress, Enrollment, TestResult, WorkArea
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
    from django.db.models import Q
    user = request.user
    
    # Admins and Profs see all courses
    if user.is_superuser or user.groups.filter(name__in=['Administrador', 'Profesor']).exists():
        courses = Course.objects.all()
    else:
        # Standard user sees courses assigned to their area OR courses with no area assigned (common courses)
        if hasattr(user, 'profile') and user.profile.work_area:
            courses = Course.objects.filter(
                Q(assigned_work_areas=user.profile.work_area) | 
                Q(assigned_work_areas__isnull=True)
            ).distinct()
        else:
            # User has no area assigned, only sees common courses
            courses = Course.objects.filter(assigned_work_areas__isnull=True)

    # Progress math for home
    course_list = []
    for course in courses:
        modules_count = Module.objects.filter(course=course).count()
        total_content = Content.objects.filter(module__course=course).count()
        if total_content > 0:
            completed_content = ContentProgress.objects.filter(user=user, content__module__course=course, is_completed=True).count()
            progress = int((completed_content / total_content) * 100)
        else:
            progress = 0
            
        course_list.append({
            'course': course,
            'progress': progress,
            'modules_count': modules_count
        })

    context = {
        'courses': course_list,
        'active_menu': 'homepage',
    }
    return render(request, 'lms/home.html', context)

@login_required
def course_detail_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    modules = course.modules.all().prefetch_related('contents')
    
    # Progress math
    total_content = Content.objects.filter(module__course=course).count()
    completed_content = ContentProgress.objects.filter(user=request.user, content__module__course=course, is_completed=True).count()
    progress_percentage = int((completed_content / total_content * 100)) if total_content > 0 else 0
    
    test_available = (total_content > 0 and completed_content == total_content) or (total_content == 0)
    
    # Check if they have a test passed
    test_passed = False
    test_score = 0
    if hasattr(course, 'test'):
        from .models import TestResult
        last_result = TestResult.objects.filter(user=request.user, test=course.test).order_by('-attempted_at').first()
        if last_result and last_result.passed:
            test_passed = True
            test_score = last_result.score
    
    context = {
        'course': course,
        'modules': modules,
        'progress_percentage': progress_percentage,
        'test_available': test_available,
        'test_passed': test_passed,
        'test_score': test_score,
        'active_menu': 'courses',
    }
    return render(request, 'lms/course_detail.html', context)

@login_required
def reports_view(request):
    # Only Admin and Profesor can access
    if not request.user.groups.filter(name__in=['Administrador', 'Profesor']).exists():
        raise PermissionDenied("No tienes permisos para ver esta página.")
        
    area_id = request.GET.get('area')
    hq = request.GET.get('headquarters')
    
    # We will pass the available areas and headquarters for the filter select
    work_areas = WorkArea.objects.all()
    headquarters = [('Hualpen', 'Hualpén'), ('Coyhaique', 'Coyhaique')]
    
    context = {
        'active_menu': 'reports',
        'work_areas': work_areas,
        'headquarters': headquarters,
        'selected_area': area_id,
        'selected_hq': hq,
    }
    return render(request, 'lms/reports_dashboard.html', context)

@login_required
def groups_view(request):
    from django.contrib.auth.models import User
    
    area_id = request.GET.get('area')
    hq = request.GET.get('headquarters')
    
    users = User.objects.select_related('profile__work_area').prefetch_related('enrollments__course').all()
    
    if area_id:
        users = users.filter(profile__work_area_id=area_id)
    if hq:
        users = users.filter(profile__headquarters=hq)
        
    work_areas = WorkArea.objects.all()
    headquarters = [('Hualpen', 'Hualpén'), ('Coyhaique', 'Coyhaique')]
    
    context = {
        'users': users,
        'work_areas': work_areas,
        'headquarters': headquarters,
        'selected_area': area_id,
        'selected_hq': hq,
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
def course_delete_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        course.delete()
        return redirect('home')
    return render(request, 'lms/course_confirm_delete.html', {'course': course})

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
            # Set order to max + 1
            max_order = course.modules.aggregate(Max('order'))['order__max'] or 0
            module.order = max_order + 1
            module.save()
            return redirect('course_manage', course_id=course.id)
    else:
        form = ModuleForm()
    return render(request, 'lms/module_form.html', {'form': form, 'course': course, 'title': 'Añadir Módulo'})

@staff_required
def module_edit_view(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            return redirect('course_manage', course_id=module.course.id)
    else:
        form = ModuleForm(instance=module)
    return render(request, 'lms/module_form.html', {'form': form, 'course': module.course, 'title': 'Editar Módulo'})

@staff_required
def content_create_view(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        form = ContentForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.save(commit=False)
            content.module = module
            # Set order to max + 1
            max_order = module.contents.aggregate(Max('order'))['order__max'] or 0
            content.order = max_order + 1
            content.save()
            return redirect('course_manage', course_id=module.course.id)
    else:
        form = ContentForm()
    return render(request, 'lms/content_form.html', {'form': form, 'module': module, 'title': 'Añadir Sección'})

@staff_required
def content_edit_view(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    if request.method == 'POST':
        form = ContentForm(request.POST, request.FILES, instance=content)
        if form.is_valid():
            form.save()
            return redirect('course_manage', course_id=content.module.course.id)
    else:
        form = ContentForm(instance=content)
    return render(request, 'lms/content_form.html', {'form': form, 'module': content.module, 'title': 'Editar Sección'})

import json
from django.db import transaction
from .models import Test, Question, Answer

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
        # Update both order and module_id to support cross-module dragging
        Content.objects.filter(id=cid).update(order=i, module_id=module_id)
    return JsonResponse({'status': 'ok'})

@staff_required
@require_POST
def module_delete_view(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    course_id = module.course.id
    module.delete()
    return redirect('course_manage', course_id=course_id)

@staff_required
@require_POST
def content_delete_view(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    course_id = content.module.course.id
    content.delete()
    return redirect('course_manage', course_id=course_id)

@staff_required
def test_builder_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            with transaction.atomic():
                test, _ = Test.objects.get_or_create(course=course)
                test.title = data.get('title', 'Evaluación Final')
                test.passing_score = int(data.get('passing_score', 60))
                test.save()
                
                # Resync questions
                test.questions.all().delete() # Clear old ones
                for q_data in data.get('questions', []):
                    question = Question.objects.create(test=test, text=q_data.get('text', ''))
                    for a_data in q_data.get('answers', []):
                        Answer.objects.create(
                            question=question,
                            text=a_data.get('text', ''),
                            is_correct=bool(a_data.get('is_correct', False))
                        )
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    # GET: Prepare data for frontend
    test = getattr(course, 'test', None)
    context = {
        'course': course,
        'test': test,
        'active_menu': 'lms'
    }
    return render(request, 'lms/test_builder.html', context)

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

@login_required
def take_test_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    test = getattr(course, 'test', None)
    
    if not test:
        return redirect('course_detail', course_id=course.id)
        
    # Check completion
    total_content = Content.objects.filter(module__course=course).count()
    completed_content = ContentProgress.objects.filter(user=request.user, content__module__course=course, is_completed=True).count()
    
    if total_content > 0 and completed_content < total_content:
        # User hasn't finished the course
        return redirect('course_detail', course_id=course.id)

    if request.method == 'POST':
        questions = test.questions.all()
        correct_count = 0
        total_questions = questions.count()
        wrong_questions = []

        if total_questions == 0:
            return redirect('course_detail', course_id=course.id)

        for q in questions:
            selected_answer_id = request.POST.get(f'question_{q.id}')
            if selected_answer_id:
                try:
                    answer = Answer.objects.get(id=selected_answer_id, question=q)
                    if answer.is_correct:
                        correct_count += 1
                    else:
                        wrong_questions.append(q.text)
                except Answer.DoesNotExist:
                    wrong_questions.append(q.text)
            else:
                wrong_questions.append(q.text)

        score = round((correct_count / total_questions) * 100, 1)
        passed = score >= test.passing_score

        # Save result
        TestResult.objects.create(
            user=request.user,
            test=test,
            score=score,
            passed=passed
        )

        if passed:
            Enrollment.objects.update_or_create(
                user=request.user,
                course=course,
                defaults={'is_completed': True}
            )
            request.session[f'wrong_answers_{course.id}'] = wrong_questions
            return redirect('test_result', course_id=course.id)
        else:
            # FAIL PENALTY: WIPE PROGRESS
            ContentProgress.objects.filter(user=request.user, content__module__course=course).delete()
            request.session[f'test_failed_{course.id}'] = True
            return redirect('test_result', course_id=course.id)

    context = {
        'course': course,
        'test': test,
        'questions': test.questions.prefetch_related('answers').all(),
        'active_menu': 'courses'
    }
    return render(request, 'lms/test_take.html', context)

@login_required
def test_result_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    test = getattr(course, 'test', None)
    
    wrong_answers = request.session.pop(f'wrong_answers_{course.id}', [])
    failed = request.session.pop(f'test_failed_{course.id}', False)

    result = TestResult.objects.filter(user=request.user, test=test).order_by('-attempted_at').first()

    context = {
        'course': course,
        'test': test,
        'result': result,
        'failed': failed,
        'wrong_answers': wrong_answers,
        'active_menu': 'courses'
    }
    return render(request, 'lms/test_result.html', context)

@login_required
def profile_view(request):
    user = request.user
    
    # Get completed courses
    completed_enrollments = Enrollment.objects.filter(user=user, is_completed=True).select_related('course')
    
    # Get available courses
    from django.db.models import Q
    if hasattr(user, 'profile') and user.profile.work_area:
        all_courses = Course.objects.filter(
            Q(assigned_work_areas=user.profile.work_area) | Q(assigned_work_areas__isnull=True)
        ).distinct()
    else:
        all_courses = Course.objects.filter(assigned_work_areas__isnull=True)
        
    completed_course_ids = completed_enrollments.values_list('course_id', flat=True)
    available_courses_qs = all_courses.exclude(id__in=completed_course_ids)
    
    # Calculate progress for available courses
    available_courses = []
    for course in available_courses_qs:
        total_content = Content.objects.filter(module__course=course).count()
        if total_content > 0:
            completed_content = ContentProgress.objects.filter(user=user, content__module__course=course, is_completed=True).count()
            progress = int((completed_content / total_content) * 100)
        else:
            progress = 0
            
        available_courses.append({
            'course': course,
            'progress': progress
        })

    context = {
        'completed_enrollments': completed_enrollments,
        'available_courses': available_courses,
        'active_menu': 'profile'
    }
    return render(request, 'lms/profile.html', context)

@login_required
def certificate_view(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, user=request.user, is_completed=True)
    context = {
        'enrollment': enrollment,
        'date': enrollment.enrolled_at, # Alternatively, could be a completion date if model had it. Using enrolled_at or today is fine. 
        # Using timezone.now() for the seal
    }
    return render(request, 'lms/certificate.html', context)

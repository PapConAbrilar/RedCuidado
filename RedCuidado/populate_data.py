import os
import django
import random

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RedCuidado.settings')
django.setup()

from django.contrib.auth.models import User, Group
from lms.models import Course, Module, Content, Enrollment, Test, Question, Answer, TestResult, UserProfile

def populate_tests_and_results():
    print("Starting data population...")
    
    # 1. Ensure Groups exist (just in case)
    groups = ['Administrador', 'Profesor', 'Trabajador']
    for gname in groups:
        Group.objects.get_or_create(name=gname)

    # 2. Get or create test users (Colaboradores)
    users_data = [
        {'username': 'colaborador_1', 'first_name': 'Juan', 'last_name': 'Pérez', 'area': 'Enfermería', 'sede': 'Hualpen'},
        {'username': 'colaborador_2', 'first_name': 'María', 'last_name': 'González', 'area': 'Kinesiología', 'sede': 'Talca'},
        {'username': 'colaborador_3', 'first_name': 'Pedro', 'last_name': 'Soto', 'area': 'Administración', 'sede': 'Chillán'},
    ]
    
    colaborador_group = Group.objects.get(name='Trabajador')
    
    created_users = []
    for ud in users_data:
        user, created = User.objects.get_or_create(
            username=ud['username'],
            defaults={
                'first_name': ud['first_name'],
                'last_name': ud['last_name'],
                'email': f"{ud['username']}@ejemplo.com"
            }
        )
        if created:
            user.set_password('demo123')
            user.save()
            user.groups.add(colaborador_group)
            
            # Create Profile
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.employee_id = f"ID-{ud['username'].upper()}"
            profile.headquarters = ud['sede']
            # Area lookup if exists, else skip
            from lms.models import WorkArea
            wa = WorkArea.objects.filter(name=ud['area']).first()
            if wa:
                profile.work_area = wa
            profile.save()
            print(f"Created user {user.username}")
        created_users.append(user)

    # 3. Add Tests to Courses
    courses = Course.objects.all()
    if not courses:
        print("No courses found. Run populate_courses.py first.")
        return

    test_questions = [
        ("¿Cuál es la primera regla del cuidado?", ["Seguridad ante todo", "Rapidez", "Silencio"], 0),
        ("¿Qué se debe hacer en caso de emergencia?", ["Llamar al supervisor", "Salir corriendo", "Ignorar"], 0),
        ("¿Es importante el lavado de manos?", ["Sí, siempre", "Sólo a veces", "No es necesario"], 0),
    ]

    for course in courses:
        test, created = Test.objects.get_or_create(
            course=course,
            defaults={'title': f'Evaluación Final: {course.title}', 'passing_score': 70}
        )
        
        if created:
            print(f"Created test for {course.code}")
            for q_text, answers, correct_idx in test_questions:
                q = Question.objects.create(test=test, text=q_text)
                for i, a_text in enumerate(answers):
                    Answer.objects.create(question=q, text=a_text, is_correct=(i == correct_idx))
        else:
            print(f"Test already exists for {course.code}")

    # 4. Generate Test Results (Randomized completions)
    for user in created_users:
        # Enroll in 1-2 random courses
        enrolled_courses = random.sample(list(courses), random.randint(1, min(2, len(courses))))
        for course in enrolled_courses:
            enr, _ = Enrollment.objects.get_or_create(user=user, course=course)
            
            # 70% chance they completed it
            if random.random() < 0.7:
                test = getattr(course, 'test', None)
                if test:
                    # Create a passing result
                    score = random.randint(70, 100)
                    TestResult.objects.create(
                        user=user,
                        test=test,
                        score=score,
                        passed=True
                    )
                    enr.is_completed = True
                    enr.save()
                    print(f"User {user.username} completed {course.code} with {score}%")

    print("Data population finished successfully!")

if __name__ == "__main__":
    populate_tests_and_results()

from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('course/<int:course_id>/', views.course_detail_view, name='course_detail'),
    path('reports/', views.reports_view, name='reports'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('groups/', views.groups_view, name='groups'),
    
    # Management
    path('course/create/', views.course_create_view, name='course_create'),
    path('course/<int:course_id>/edit/', views.course_edit_view, name='course_edit'),
    path('course/<int:course_id>/manage/', views.course_manage_view, name='course_manage'),
    path('course/<int:course_id>/module/add/', views.module_create_view, name='module_add'),
    path('module/<int:module_id>/content/add/', views.content_create_view, name='content_add'),
    path('course/<int:course_id>/reorder-modules/', views.reorder_modules, name='reorder_modules'),
    path('module/<int:module_id>/reorder-contents/', views.reorder_contents, name='reorder_contents'),
    
    # Learning / Player
    path('course/<int:course_id>/learn/', views.learning_view, name='course_learn_start'),
    path('course/<int:course_id>/learn/<int:content_id>/', views.learning_view, name='course_learn'),
]

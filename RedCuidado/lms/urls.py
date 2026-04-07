from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('course/<int:course_id>/', views.course_detail_view, name='course_detail'),
    path('reports/', views.reports_view, name='reports'),
    path('calendar/', views.calendar_view, name='calendar'),
]

from django.urls import path
from . import views

app_name = 'timetable'

urlpatterns = [
    path('', views.timetable_list, name='timetable_list'),
    path('add/', views.timetable_create, name='timetable_create'),
    path('<int:pk>/edit/', views.timetable_edit, name='timetable_edit'),
    path('<int:pk>/delete/', views.timetable_delete, name='timetable_delete'),
    path('class/pdf/', views.generate_class_timetable_pdf, name='generate_class_timetable_pdf'),
    path('class/<str:class_name>/pdf/', views.generate_class_timetable_pdf, name='generate_class_timetable_pdf_detail'),
    path('teacher/pdf/', views.generate_teacher_timetable_pdf, name='generate_teacher_timetable_pdf'),
    path('teacher/<int:teacher_id>/pdf/', views.generate_teacher_timetable_pdf, name='generate_teacher_timetable_pdf_detail'),
    path('class/', views.class_timetable, name='class_timetable'),
    path('class/<str:class_name>/', views.class_timetable, name='class_timetable_detail'),
    path('teacher/', views.teacher_timetable, name='teacher_timetable'),
    path('teacher/<int:teacher_id>/', views.teacher_timetable, name='teacher_timetable_detail'),
] 
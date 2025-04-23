from django.urls import path
from . import views

app_name = 'school_teachers'

urlpatterns = [
    path('', views.teacher_list, name='teacher_list'),
    path('add/', views.teacher_create, name='teacher_create'),
    path('<int:pk>/', views.teacher_detail, name='teacher_detail'),
    path('<int:pk>/edit/', views.teacher_update, name='teacher_update'),
    path('<int:pk>/delete/', views.teacher_delete, name='teacher_delete'),
    path('<int:pk>/generate-pdf/', views.generate_teacher_pdf, name='generate_teacher_pdf'),
    path('generate-all-pdf/', views.generate_all_teachers_pdf, name='generate_all_teachers_pdf'),
] 
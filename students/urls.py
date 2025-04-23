from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('add/', views.student_create, name='student_create'),
    path('<int:pk>/', views.student_detail, name='student_detail'),
    path('<int:pk>/edit/', views.student_update, name='student_update'),
    path('<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('<int:pk>/generate-pdf/', views.generate_student_pdf, name='generate_student_pdf'),
    path('generate-all-pdf/', views.generate_all_students_pdf, name='generate_all_students_pdf'),
] 
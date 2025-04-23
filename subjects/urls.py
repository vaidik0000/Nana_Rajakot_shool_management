from django.urls import path
from . import views

app_name = 'subjects'

urlpatterns = [
    path('', views.subject_list, name='subject_list'),
    path('add/', views.subject_create, name='subject_create'),
    path('<int:pk>/', views.subject_detail, name='subject_detail'),
    path('<int:pk>/edit/', views.subject_update, name='subject_update'),
    path('<int:pk>/delete/', views.subject_delete, name='subject_delete'),
    
    # Student Marks URLs
    path('marks/', views.student_marks, name='student_marks'),
    path('marks/add/', views.add_student_mark, name='add_student_mark'),
    path('marks/<int:pk>/edit/', views.edit_student_mark, name='edit_student_mark'),
    path('marks/<int:pk>/delete/', views.delete_student_mark, name='delete_student_mark'),
] 
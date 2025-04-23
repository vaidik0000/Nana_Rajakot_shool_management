from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Student Attendance Records
    path('create/', views.attendance_create, name='create'),
    path('bulk-create/', views.attendance_bulk_create, name='bulk_create'),
    path('list/', views.attendance_list, name='list'),
    path('record/<int:pk>/', views.attendance_detail, name='detail'),
    path('edit/<int:pk>/', views.attendance_edit, name='edit'),
    path('delete/<int:pk>/', views.attendance_delete, name='delete'),

    # Reports & Downloads
    path('download/all/', views.download_attendance_records, name='download_all'),

    # Teacher Attendance Records
    path('teacher/', views.teacher_attendance_list, name='teacher_attendance_list'),
    path('teacher/create/', views.teacher_attendance_create, name='teacher_attendance_create'),
    path('teacher/bulk-create/', views.teacher_attendance_bulk_create, name='teacher_attendance_bulk_create'),
    path('teacher/edit/<int:pk>/', views.teacher_attendance_edit, name='teacher_attendance_edit'),
    path('teacher/delete/<int:pk>/', views.teacher_attendance_delete, name='teacher_attendance_delete'),
    path('teacher/<int:pk>/', views.teacher_attendance_detail, name='teacher_attendance_detail'),

    # Reports
    path('reports/', views.attendance_report, name='attendance_report'),
    path('teacher-report/', views.teacher_attendance_report, name='teacher_attendance_report'),
    path('student-calendar/', views.attendance_calendar, name='attendance_calendar'),
    path('teacher-calendar/', views.teacher_attendance_calendar, name='teacher_attendance_calendar'),

    # API endpoints
    path('api/attendance/detail/', views.get_attendance_detail, name='attendance_detail'),
] 
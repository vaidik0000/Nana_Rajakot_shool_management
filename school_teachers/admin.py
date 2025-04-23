from django.contrib import admin
from .models import Teacher

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'first_name', 'last_name', 'email', 'phone_number', 'specialization', 'is_active')
    list_filter = ('is_active', 'gender', 'specialization')
    search_fields = ('first_name', 'last_name', 'email', 'employee_id', 'phone_number')
    ordering = ('first_name', 'last_name')

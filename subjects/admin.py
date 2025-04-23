from django.contrib import admin
from .models import Subject

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'teacher', 'credits', 'is_active')
    list_filter = ('is_active', 'credits')
    search_fields = ('name', 'code', 'description')
    ordering = ('name',)

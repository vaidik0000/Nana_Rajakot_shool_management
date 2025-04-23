from django.contrib import admin
from .models import TimeTable

@admin.register(TimeTable)
class TimeTableAdmin(admin.ModelAdmin):
    list_display = ('class_name', 'day', 'period', 'subject', 'teacher', 'start_time', 'end_time', 'room_number')
    list_filter = ('class_name', 'day', 'subject', 'teacher')
    search_fields = ('class_name', 'subject__name', 'teacher__first_name', 'teacher__last_name', 'room_number')
    ordering = ('class_name', 'day', 'period')

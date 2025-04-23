from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'start_date', 'end_date', 'location', 'is_all_day')
    list_filter = ('event_type', 'is_all_day', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'start_date'

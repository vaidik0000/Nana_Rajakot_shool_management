from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'roll_number', 'class_name', 'gender', 'phone_number', 'is_active')
    list_filter = ('class_name', 'gender', 'is_active')
    search_fields = ('first_name', 'last_name', 'roll_number', 'phone_number', 'email')
    list_per_page = 20
    ordering = ('class_name', 'roll_number')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'roll_number', 'class_name', 'gender', 'date_of_birth', 'profile_picture')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_number', 'address')
        }),
        ('Parent Information', {
            'fields': ('parent_name', 'parent_phone', 'parent_email')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ('admission_date', 'created_at', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('roll_number',)
        return self.readonly_fields

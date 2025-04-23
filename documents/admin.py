from django.contrib import admin
from .models import DocumentType, StudentDocument

@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'required', 'active', 'created_at')
    list_filter = ('required', 'active')
    search_fields = ('name', 'description')
    list_editable = ('required', 'active')
    ordering = ('name',)

@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ('student', 'document_type', 'filename', 'uploaded_by', 'created_at')
    list_filter = ('document_type', 'created_at')
    search_fields = ('student__first_name', 'student__last_name', 'document_type__name', 'notes')
    readonly_fields = ('filename', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    raw_id_fields = ('student', 'uploaded_by')

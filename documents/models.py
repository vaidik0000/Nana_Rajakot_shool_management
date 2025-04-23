from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from students.models import Student
import os

def validate_file_size(value):
    """
    Validates that the file size is less than or equal to 250 KB
    """
    filesize = value.size
    if filesize > 250 * 1024:  # 250 KB in bytes
        raise ValidationError("The maximum file size allowed is 250 KB.")
    return value

def validate_file_extension(value):
    """
    Validates that the file is a PDF
    """
    ext = os.path.splitext(value.name)[1]
    if ext.lower() != '.pdf':
        raise ValidationError("Only PDF files are allowed.")
    return value

def document_upload_path(instance, filename):
    """
    Returns the path to upload the document to.
    Format: documents/{student_id}_{student_name}_{doc_type}.pdf
    """
    student_name = f"{instance.student.first_name}_{instance.student.last_name}".lower().replace(' ', '_')
    doc_type = instance.document_type.name.lower().replace(' ', '_')
    file_extension = os.path.splitext(filename)[1]
    
    return f"documents/{instance.student.id}_{student_name}_{doc_type}{file_extension}"

class DocumentType(models.Model):
    """
    Model to store document types that can be uploaded for students
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    required = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Document Type'
        verbose_name_plural = 'Document Types'

class StudentDocument(models.Model):
    """
    Model to store documents uploaded for students
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='documents')
    document_type = models.ForeignKey(DocumentType, on_delete=models.PROTECT)
    file = models.FileField(
        upload_to=document_upload_path,
        validators=[validate_file_size, validate_file_extension]
    )
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.document_type.name}"
    
    def filename(self):
        return os.path.basename(self.file.name)
    
    class Meta:
        unique_together = ['student', 'document_type']
        ordering = ['-updated_at']
        verbose_name = 'Student Document'
        verbose_name_plural = 'Student Documents'

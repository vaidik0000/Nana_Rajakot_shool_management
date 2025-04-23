from django import forms
from .models import DocumentType, StudentDocument

class DocumentTypeForm(forms.ModelForm):
    """
    Form for creating and updating document types
    """
    class Meta:
        model = DocumentType
        fields = ['name', 'description', 'required', 'active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class StudentDocumentForm(forms.ModelForm):
    """
    Form for uploading and updating student documents
    """
    class Meta:
        model = StudentDocument
        fields = ['file', 'notes']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        # Remove the ability to change document_type and student in updates
        # These will be set in the view
        super(StudentDocumentForm, self).__init__(*args, **kwargs)
        
        # Add help text for file field to inform about size limitations
        self.fields['file'].help_text = 'Only PDF files up to 250 KB are allowed.'
        
    def clean_file(self):
        """
        Custom validation for file field.
        The model validators will be called automatically, but we can add additional validation here.
        """
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 250 * 1024:  # 250 KB in bytes
                raise forms.ValidationError("Please reduce your file size to ≤ 250 KB.")
                
            # Get the file extension
            import os
            ext = os.path.splitext(file.name)[1]
            if ext.lower() != '.pdf':
                raise forms.ValidationError("Only PDF files are allowed.")
                
        return file 
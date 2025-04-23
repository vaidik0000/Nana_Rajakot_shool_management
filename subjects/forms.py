from django import forms
from .models import Subject, StudentMark

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'description', 'teacher', 'credits', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subject name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subject code'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter description', 'rows': 3}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'credits': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter credits'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
        }

class StudentMarkForm(forms.ModelForm):
    class Meta:
        model = StudentMark
        fields = ['student', 'subject', 'teacher', 'marks_obtained', 'total_marks', 'date', 'remarks']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'marks_obtained': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter marks obtained'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter total marks'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter remarks', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        marks_obtained = cleaned_data.get('marks_obtained')
        total_marks = cleaned_data.get('total_marks')
        
        if marks_obtained and total_marks:
            if marks_obtained > total_marks:
                raise forms.ValidationError("Marks obtained cannot be greater than total marks.")
            
            # Calculate percentage
            percentage = (marks_obtained / total_marks) * 100
            cleaned_data['percentage'] = round(percentage, 2)
            
            # Determine grade based on percentage
            if percentage >= 90:
                cleaned_data['grade'] = 'A+'
            elif percentage >= 75:
                cleaned_data['grade'] = 'A'
            elif percentage >= 60:
                cleaned_data['grade'] = 'B'
            elif percentage >= 50:
                cleaned_data['grade'] = 'C'
            elif percentage >= 33:
                cleaned_data['grade'] = 'D'
            else:
                cleaned_data['grade'] = 'E'
        else:
            # Set default values if marks are not provided
            cleaned_data['percentage'] = 0
            cleaned_data['grade'] = 'E'
        
        return cleaned_data 
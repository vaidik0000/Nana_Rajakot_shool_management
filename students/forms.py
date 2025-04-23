from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'first_name', 'last_name', 'roll_number', 'class_name',
            'gender', 'date_of_birth', 'address', 'phone_number',
            'email', 'parent_name', 'parent_phone', 'parent_email',
            'profile_picture', 'is_active'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}),
            'roll_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter roll number'}),
            'class_name': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Enter address'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'parent_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter parent name'}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter parent phone'}),
            'parent_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter parent email'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
        } 
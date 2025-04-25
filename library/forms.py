from django import forms
from .models import BookCategory, Book, BookIssue
from students.models import Student
from school_teachers.models import Teacher
from django.utils import timezone

class BookCategoryForm(forms.ModelForm):
    class Meta:
        model = BookCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'author', 'isbn', 'category', 'publisher', 
            'publication_year', 'edition', 'description', 
            'total_copies', 'shelf_location', 'status', 'cover_image'
        ]

class BookIssueForm(forms.ModelForm):
    class Meta:
        model = BookIssue
        fields = ['book', 'student', 'due_date', 'remarks']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-control'}),
            'student': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter active students only
        self.fields['student'].queryset = Student.objects.filter(is_active=True)
        # Add placeholder and help text
        self.fields['student'].widget.attrs.update({'placeholder': 'Select a student'})
        self.fields['book'].widget.attrs.update({'placeholder': 'Select a book'})

class BookReturnForm(forms.ModelForm):
    class Meta:
        model = BookIssue
        fields = ['return_date', 'status', 'fine_amount', 'remarks']
        widgets = {
            'return_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'fine_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial return date to today
        self.fields['return_date'].initial = timezone.now().date()
        # Set initial status to returned
        self.fields['status'].initial = 'returned'
        # Add help text
        self.fields['fine_amount'].help_text = 'Enter 0 if no fine is applicable'
        self.fields['remarks'].help_text = 'Optional remarks about the book condition or return process'

    def clean_return_date(self):
        return_date = self.cleaned_data.get('return_date')
        if return_date and return_date < self.instance.issue_date:
            raise forms.ValidationError('Return date cannot be before issue date')
        return return_date

    def clean_fine_amount(self):
        fine_amount = self.cleaned_data.get('fine_amount')
        if fine_amount and fine_amount < 0:
            raise forms.ValidationError('Fine amount cannot be negative')
        return fine_amount
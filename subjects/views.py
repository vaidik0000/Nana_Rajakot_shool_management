from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Subject, StudentMark
from .forms import SubjectForm, StudentMarkForm
import traceback
from core.decorators import teacher_required, student_required, admin_required

# Create your views here.

@login_required
def subject_list(request):
    subjects = Subject.objects.all()
    # Get user type to control display of action buttons
    is_student = hasattr(request, 'user_type') and request.user_type == 'student'
    is_teacher = hasattr(request, 'user_type') and request.user_type == 'teacher'
    return render(request, 'subjects/list.html', {
        'subjects': subjects, 
        'is_student': is_student,
        'is_teacher': is_teacher
    })

@login_required
def subject_detail(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    # Get user type to control display of action buttons
    is_student = hasattr(request, 'user_type') and request.user_type == 'student'
    is_teacher = hasattr(request, 'user_type') and request.user_type == 'teacher'
    return render(request, 'subjects/detail.html', {
        'subject': subject, 
        'is_student': is_student,
        'is_teacher': is_teacher
    })

@admin_required
def subject_create(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save()
            messages.success(request, 'Subject added successfully.')
            return redirect('subjects:subject_list')
    else:
        form = SubjectForm()
    return render(request, 'subjects/form.html', {'form': form, 'title': 'Add Subject'})

@admin_required
def subject_update(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            subject = form.save()
            messages.success(request, 'Subject updated successfully.')
            return redirect('subjects:subject_detail', pk=subject.pk)
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'subjects/form.html', {'form': form, 'title': 'Edit Subject'})

@admin_required
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Subject deleted successfully.')
        return redirect('subjects:subject_list')
    return render(request, 'subjects/delete.html', {'subject': subject})

# Student Marks Views
@login_required
def student_marks(request):
    # Initialize variables
    student_marks = StudentMark.objects.all()
    is_student = False
    student = None
    
    # If user is a student, only show their marks
    if hasattr(request, 'user_type') and request.user_type == 'student':
        is_student = True
        student = request.student
        
        # Print debug info
        print(f"Student identified: {student.first_name} {student.last_name} (ID: {student.id})")
        
        # Use more specific filter with error handling
        try:
            student_marks = StudentMark.objects.filter(student=student)
            print(f"Found {student_marks.count()} marks for student ID {student.id}")
        except Exception as e:
            print(f"Error filtering marks: {str(e)}")
            messages.error(request, f"Error loading student marks: {str(e)}")
            student_marks = StudentMark.objects.none()  # Empty queryset
    
    return render(request, 'subjects/student_marks.html', {
        'student_marks': student_marks,
        'is_student': is_student,
        'student': student
    })

@teacher_required
def add_student_mark(request):
    if request.method == 'POST':
        form = StudentMarkForm(request.POST)
        if form.is_valid():
            try:
                # Print form data for debugging
                print("Form data:", form.cleaned_data)
                
                student_mark = form.save()
                messages.success(request, 'Student mark added successfully.')
                return redirect('subjects:student_marks')
            except Exception as e:
                # Print detailed error for debugging
                print("Error saving student mark:", str(e))
                print(traceback.format_exc())
                messages.error(request, f'Error saving student mark: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = StudentMarkForm()
    return render(request, 'subjects/student_mark_form.html', {'form': form, 'title': 'Add Student Mark'})

@teacher_required
def edit_student_mark(request, pk):
    student_mark = get_object_or_404(StudentMark, pk=pk)
    if request.method == 'POST':
        form = StudentMarkForm(request.POST, instance=student_mark)
        if form.is_valid():
            try:
                student_mark = form.save()
                messages.success(request, 'Student mark updated successfully.')
                return redirect('subjects:student_marks')
            except Exception as e:
                messages.error(request, f'Error updating student mark: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = StudentMarkForm(instance=student_mark)
    return render(request, 'subjects/student_mark_form.html', {'form': form, 'title': 'Edit Student Mark'})

@teacher_required
def delete_student_mark(request, pk):
    student_mark = get_object_or_404(StudentMark, pk=pk)
    if request.method == 'POST':
        try:
            student_mark.delete()
            messages.success(request, 'Student mark deleted successfully.')
            return redirect('subjects:student_marks')
        except Exception as e:
            messages.error(request, f'Error deleting student mark: {str(e)}')
    return render(request, 'subjects/student_mark_delete.html', {'student_mark': student_mark})

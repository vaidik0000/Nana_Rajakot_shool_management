from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Student
from .forms import StudentForm
from django.urls import reverse
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.utils import timezone
import os
from django.conf import settings
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import ImageReader
import qrcode
from io import BytesIO
from django.db.models import Count, Q
from datetime import date, timedelta, datetime
from core.decorators import teacher_required, student_required, admin_required



from .models import Student  # Adjust the import if needed


# Create your views here.

@login_required
def student_list(request):
    students = Student.objects.all()
    # Get user type to control display of action buttons
    is_student = hasattr(request, 'user_type') and request.user_type == 'student'
    is_teacher = hasattr(request, 'user_type') and request.user_type == 'teacher'
    return render(request, 'students/list.html', {
        'students': students, 
        'is_student': is_student,
        'is_teacher': is_teacher
    })

@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    # Get user type to control display of action buttons
    is_student = hasattr(request, 'user_type') and request.user_type == 'student'
    is_teacher = hasattr(request, 'user_type') and request.user_type == 'teacher'
    return render(request, 'students/detail.html', {
        'student': student, 
        'is_student': is_student,
        'is_teacher': is_teacher
    })

@admin_required
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                student = form.save()
                messages.success(request, f'Student {student.first_name} {student.last_name} added successfully.')
                return redirect('students:student_list')
            except Exception as e:
                messages.error(request, f'Error saving student: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = StudentForm()
    return render(request, 'students/form.html', {'form': form, 'title': 'Add Student'})

@admin_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            try:
                student = form.save()
                messages.success(request, f'Student {student.first_name} {student.last_name} updated successfully.')
                return redirect('students:student_list')
            except Exception as e:
                messages.error(request, f'Error updating student: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/form.html', {'form': form, 'title': 'Edit Student'})

@admin_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        try:
            student.delete()
            messages.success(request, f'Student {student.first_name} {student.last_name} deleted successfully.')
            return redirect('students:student_list')
        except Exception as e:
            messages.error(request, f'Error deleting student: {str(e)}')
    return render(request, 'students/delete.html', {'student': student})

@login_required
def generate_student_pdf(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    # Create a BytesIO buffer for the PDF.
    buffer = BytesIO()
    width, height = A4
    margin = 50
    p = canvas.Canvas(buffer, pagesize=A4)

    # Define color palette
    primary_color = colors.HexColor('#2B579A')    # School blue
    light_gray = colors.HexColor('#F2F2F2')       # Background gray

    # Simple header
    p.setFillColor(primary_color)
    p.setFont("Helvetica-Bold", 24)
    p.drawString(margin, height - 60, "Student Record")
    p.setFont("Helvetica", 14)
    p.drawString(margin, height - 80, f"Generated on: {timezone.now().strftime('%d %B %Y %H:%M')}")

    # Handle student photo
    if student.profile_picture:
        try:
            # Get the absolute path to the media root
            media_root = settings.MEDIA_ROOT
            # Construct the full path to the profile picture
            photo_path = os.path.join(media_root, student.profile_picture.name)
            
            if os.path.exists(photo_path):
                # Draw the image with proper dimensions
                p.drawImage(photo_path, width - margin - 110, height - 255, width=110, height=110, mask='auto')
            else:
                raise Exception("Photo file not found")
        except Exception as e:
            # If there's any error with the photo, show a placeholder
            p.setFillColor(light_gray)
            p.roundRect(width - margin - 110, height - 255, 110, 110, 5, fill=1, stroke=0)
            p.setFillColor(colors.darkgrey)
            p.setFont("Helvetica", 10)
            p.drawCentredString(width - margin - 55, height - 200, "Photo Not Available")
    else:
        # If no profile picture is set
        p.setFillColor(light_gray)
        p.roundRect(width - margin - 110, height - 255, 110, 110, 5, fill=1, stroke=0)
        p.setFillColor(colors.darkgrey)
        p.setFont("Helvetica", 10)
        p.drawCentredString(width - margin - 55, height - 200, "No Photo")

    # Add student basic info
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(margin, height - 290, f"{student.first_name} {student.last_name}")
    
    # Add student details
    current_y = height - 320
    details = [
        ("Roll Number:", student.roll_number),
        ("Class:", student.get_class_name_display()),
        ("Gender:", student.get_gender_display()),
        ("Date of Birth:", student.date_of_birth.strftime('%d %B %Y')),
        ("Email:", student.email or "Not provided"),
        ("Phone:", student.phone_number),
        ("Address:", student.address),
        ("Admission Date:", student.admission_date.strftime('%d %B %Y')),
        ("Status:", "Active" if student.is_active else "Inactive")
    ]
    
    p.setFont("Helvetica", 12)
    for label, value in details:
        p.drawString(margin, current_y, f"{label} {value}")
        current_y -= 20

    # Parent/Guardian details
    current_y -= 20
    p.setFont("Helvetica-Bold", 14)
    p.drawString(margin, current_y, "Parent/Guardian Information")
    current_y -= 20
    
    p.setFont("Helvetica", 12)
    parent_details = [
        ("Parent Name:", student.parent_name),
        ("Parent Phone:", student.parent_phone),
        ("Parent Email:", student.parent_email or "Not provided")
    ]
    
    for label, value in parent_details:
        p.drawString(margin, current_y, f"{label} {value}")
        current_y -= 20

    # Footer
    p.setFont("Helvetica", 8)
    p.drawString(margin, 20, "This is a computer-generated document. For official records only.")
    
    # Finalize and save PDF
    p.showPage()
    p.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create response
    filename = f"student_{student.roll_number}_{student.last_name.lower()}.pdf"
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

@login_required
def generate_all_students_pdf(request):
    students = Student.objects.all().order_by('class_name', 'first_name')
    
    # Create a BytesIO buffer for the PDF
    buffer = BytesIO()
    width, height = A4
    margin = 50
    p = canvas.Canvas(buffer, pagesize=A4)

    # Define color palette
    primary_color = colors.HexColor('#2B579A')    # School blue
    light_gray = colors.HexColor('#F2F2F2')       # Background gray

    # Title and header
    p.setFillColor(primary_color)
    p.setFont("Helvetica-Bold", 24)
    p.drawString(margin, height - 60, "All Students Report")
    p.setFont("Helvetica", 14)
    p.drawString(margin, height - 80, f"Generated on: {timezone.now().strftime('%d %B %Y %H:%M')}")
    p.drawString(margin, height - 100, f"Total Students: {students.count()}")

    # Table data
    data = [["ID", "Name", "Roll Number", "Class", "Gender", "Phone"]]
    
    for student in students:
        data.append([
            str(student.id),
            f"{student.first_name} {student.last_name}",
            student.roll_number,
            student.get_class_name_display(),
            student.get_gender_display(),
            student.phone_number
        ])
    
    # Set up table
    table = Table(data, colWidths=[30, 120, 80, 60, 60, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_gray])
    ]))
    
    # Draw table
    table.wrapOn(p, width - 2*margin, height)
    table.drawOn(p, margin, height - 150)
    
    # Footer
    p.setFont("Helvetica", 8)
    p.drawString(margin, 20, "This is a computer-generated document. For official records only.")
    
    # Finalize and save PDF
    p.showPage()
    p.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create response
    filename = f"all_students_report_{timezone.now().strftime('%Y%m%d')}.pdf"
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

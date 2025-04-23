from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Teacher
from .forms import TeacherForm
from django.urls import reverse
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from django.utils import timezone
import os
from django.conf import settings
from io import BytesIO
from core.decorators import teacher_required, admin_required
from reportlab.platypus import Table, TableStyle

# Create your views here.

@teacher_required
def teacher_list(request):
    teachers = Teacher.objects.all()
    return render(request, 'school_teachers/list.html', {'teachers': teachers})

@teacher_required
def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    return render(request, 'school_teachers/detail.html', {'teacher': teacher})

@admin_required
def teacher_create(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, 'Teacher added successfully.')
            return redirect('school_teachers:teacher_detail', pk=teacher.pk)
    else:
        form = TeacherForm()
    return render(request, 'school_teachers/form.html', {'form': form, 'title': 'Add Teacher'})

@admin_required
def teacher_update(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, 'Teacher updated successfully.')
            return redirect('school_teachers:teacher_detail', pk=teacher.pk)
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'school_teachers/form.html', {'form': form, 'title': 'Edit Teacher'})

@admin_required
def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        teacher.delete()
        messages.success(request, 'Teacher deleted successfully.')
        return redirect('school_teachers:teacher_list')
    return render(request, 'school_teachers/delete.html', {'teacher': teacher})

@teacher_required
def generate_teacher_pdf(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    
    # Create a BytesIO buffer for the PDF
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
    p.drawString(margin, height - 60, "Teacher Record")
    p.setFont("Helvetica", 14)
    p.drawString(margin, height - 80, f"Generated on: {timezone.now().strftime('%d %B %Y %H:%M')}")

    # Handle teacher photo
    if teacher.profile_picture:
        # Get the absolute path to the media root
        media_root = settings.MEDIA_ROOT
        # Construct the full path to the profile picture
        photo_path = os.path.join(media_root, teacher.profile_picture.name)
        
        if os.path.exists(photo_path):
            # Draw the image with proper dimensions
            p.drawImage(photo_path, width - margin - 110, height - 255, width=110, height=110, mask='auto')
        else:
            # If the photo file is not found, show a placeholder
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

    # Add teacher basic info
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(margin, height - 290, f"{teacher.first_name} {teacher.last_name}")
    
    # Add teacher details
    current_y = height - 320
    details = [
        ("Employee ID:", teacher.employee_id),
        ("Specialization:", teacher.specialization),
        ("Gender:", teacher.gender),
        ("Qualification:", teacher.qualification),
        ("Date of Birth:", teacher.date_of_birth.strftime('%d %B %Y')),
        ("Email:", teacher.email or "Not provided"),
        ("Phone:", teacher.phone_number),
        ("Address:", teacher.address),
        ("Joining Date:", teacher.joining_date.strftime('%d %B %Y')),
        ("Status:", "Active" if teacher.is_active else "Inactive")
    ]
    
    p.setFont("Helvetica", 12)
    for label, value in details:
        p.drawString(margin, current_y, f"{label} {value}")
        current_y -= 20

    # Emergency Contact details
    current_y -= 20
    p.setFont("Helvetica-Bold", 14)
    
    current_y -= 20
    
    p.setFont("Helvetica", 12)
    emergency_details = [
        
    ]
    
    for label, value in emergency_details:
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
    filename = f"teacher_{teacher.employee_id}_{teacher.last_name.lower()}.pdf"
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

@login_required
def generate_all_teachers_pdf(request):
    teachers = Teacher.objects.all().order_by('first_name')
    
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
    p.drawString(margin, height - 60, "All Teachers Report")
    p.setFont("Helvetica", 14)
    p.drawString(margin, height - 80, f"Generated on: {timezone.now().strftime('%d %B %Y %H:%M')}")
    p.drawString(margin, height - 100, f"Total Teachers: {teachers.count()}")

    # Table data
    data = [["ID", "Name", "Employee ID", "Specialization", "Email", "Phone"]]
    
    for teacher in teachers:
        data.append([
            str(teacher.id),
            f"{teacher.first_name} {teacher.last_name}",
            teacher.employee_id,
            teacher.specialization,
            teacher.email,
            teacher.phone_number
        ])
    
    # Set up table
    table = Table(data, colWidths=[30, 100, 80, 100, 120, 100])
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
    filename = f"all_teachers_report_{timezone.now().strftime('%Y%m%d')}.pdf"
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

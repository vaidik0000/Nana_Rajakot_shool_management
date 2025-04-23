from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import TimeTable
from .forms import TimeTableForm
from school_teachers.models import Teacher
from core.decorators import teacher_required, student_required, admin_required

@login_required
def timetable_list(request):
    timetables = TimeTable.objects.all().order_by('class_name', 'day', 'period')
    
    # Check if user is a teacher
    is_teacher = hasattr(request, 'user_type') and request.user_type == 'teacher'
    
    context = {
        'timetables': timetables,
        'days': dict(TimeTable.DAY_CHOICES),
        'periods': dict(TimeTable.PERIOD_CHOICES),
        'is_teacher': is_teacher,
    }
    return render(request, 'timetable/timetable_list.html', context)

@admin_required
def timetable_create(request):
    if request.method == 'POST':
        form = TimeTableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Timetable entry created successfully.')
            return redirect('timetable:timetable_list')
    else:
        # Pre-fill form with query parameters if provided
        initial_data = {}
        if 'class' in request.GET:
            initial_data['class_name'] = request.GET.get('class')
        if 'day' in request.GET:
            initial_data['day'] = request.GET.get('day')
        if 'period' in request.GET:
            initial_data['period'] = request.GET.get('period')
        if 'teacher' in request.GET:
            initial_data['teacher'] = request.GET.get('teacher')
        
        form = TimeTableForm(initial=initial_data)
    
    return render(request, 'timetable/timetable_form.html', {
        'form': form,
        'title': 'Add Timetable Entry'
    })

@admin_required
def timetable_edit(request, pk):
    timetable = get_object_or_404(TimeTable, pk=pk)
    
    if request.method == 'POST':
        form = TimeTableForm(request.POST, instance=timetable)
        if form.is_valid():
            form.save()
            messages.success(request, 'Timetable entry updated successfully.')
            return redirect('timetable:timetable_list')
    else:
        form = TimeTableForm(instance=timetable)
    
    return render(request, 'timetable/timetable_form.html', {
        'form': form,
        'title': 'Edit Timetable Entry'
    })

@admin_required
def timetable_delete(request, pk):
    timetable = get_object_or_404(TimeTable, pk=pk)
    
    if request.method == 'POST':
        timetable.delete()
        messages.success(request, 'Timetable entry deleted successfully.')
        return redirect('timetable:timetable_list')
    
    return render(request, 'timetable/timetable_confirm_delete.html', {
        'timetable': timetable
    })

@login_required
def class_timetable(request, class_name=None):
    timetable_entries = TimeTable.objects.all().order_by('class_name', 'day', 'period')
    
    # Get unique class names
    class_values = timetable_entries.values_list('class_name', flat=True).distinct()
    # Convert to dictionary with class_id -> class_name mapping from CLASS_CHOICES
    classes = {class_id: dict(TimeTable.CLASS_CHOICES).get(class_id) for class_id in class_values}
    
    days = dict(TimeTable.DAY_CHOICES)
    periods = dict(TimeTable.PERIOD_CHOICES)
    
    # Organize by class and day
    timetable_by_class = {}
    
    # If class_name is not provided in URL, get it from query parameters
    selected_class = class_name or request.GET.get('class')
    
    if selected_class:
        filtered_entries = timetable_entries.filter(class_name=selected_class)
        if filtered_entries.exists():
            for entry in filtered_entries:
                if entry.class_name not in timetable_by_class:
                    timetable_by_class[entry.class_name] = {}
                    
                if entry.day not in timetable_by_class[entry.class_name]:
                    timetable_by_class[entry.class_name][entry.day] = {}
                    
                timetable_by_class[entry.class_name][entry.day][entry.period] = entry
    
    context = {
        'timetable_by_class': timetable_by_class,
        'days': days,
        'periods': periods,
        'classes': classes,
        'selected_class': selected_class,
    }
    
    return render(request, 'timetable/temp_class_timetable.html', context)

@login_required
def teacher_timetable(request, teacher_id=None):
    # Check if the user is a student
    is_student = hasattr(request, 'user_type') and request.user_type == 'student'
    
    # Check if user is a teacher
    is_teacher = hasattr(request, 'user_type') and request.user_type == 'teacher'
    
    # Only students and teachers can't make changes to timetables
    can_edit = not (is_student or is_teacher)
    
    # If student, redirect away from teacher timetable view
    if is_student:
        messages.error(request, "You don't have permission to view teacher timetables.")
        return redirect('core:home')
    
    # For teachers, force show only their own timetable
    if is_teacher:
        teacher = request.teacher
        teacher_id = teacher.id
        teachers = [teacher]  # Only include their own record in dropdown
    else:
        # For admin users, show all teachers
        teachers = Teacher.objects.all()
    
    # If teacher_id is in both URL path and query params, use the URL path value
    selected_teacher_id = teacher_id
    if not selected_teacher_id and request.GET.get('teacher'):
        selected_teacher_id = request.GET.get('teacher')
    
    teacher = None
    timetable_by_day = {}
    
    if selected_teacher_id:
        try:
            # If teacher is viewing, make sure they can only see their own timetable
            if is_teacher and int(selected_teacher_id) != request.teacher.id:
                messages.warning(request, "You can only view your own timetable.")
                return redirect('timetable:teacher_timetable')
                
            teacher = Teacher.objects.get(id=selected_teacher_id)
            timetable_entries = TimeTable.objects.filter(teacher=teacher).select_related('subject').order_by('day', 'period')
            
            # Organize by day
            for entry in timetable_entries:
                if entry.day not in timetable_by_day:
                    timetable_by_day[entry.day] = {}
                timetable_by_day[entry.day][entry.period] = entry
        except Teacher.DoesNotExist:
            messages.error(request, 'Teacher not found.')
    
    context = {
        'teachers': teachers,
        'selected_teacher': teacher,
        'timetable_by_day': timetable_by_day,
        'days': dict(TimeTable.DAY_CHOICES),
        'periods': dict(TimeTable.PERIOD_CHOICES),
        'can_edit': can_edit,
        'is_teacher': is_teacher,
    }
    
    return render(request, 'timetable/temp_teacher_timetable.html', context)

@login_required
def generate_class_timetable_pdf(request, class_name=None):
    # Check if class_name is provided in the URL or as a GET parameter
    if not class_name and 'class' in request.GET:
        class_name = request.GET.get('class')
    
    if not class_name:
        messages.error(request, "Please select a class to generate PDF")
        return redirect('timetable:class_timetable')
    
    # Get timetable entries for the selected class
    timetables = TimeTable.objects.filter(class_name=class_name).order_by('day', 'period')
    
    # Group timetables by day and period for easy display
    timetable_by_day = {}
    for entry in timetables:
        if entry.day not in timetable_by_day:
            timetable_by_day[entry.day] = {}
        timetable_by_day[entry.day][entry.period] = entry
    
    # Get the class name display value
    class_display = dict(TimeTable.CLASS_CHOICES).get(class_name, class_name)
    
    # Create a BytesIO buffer for the PDF
    from io import BytesIO
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from django.utils import timezone
    
    buffer = BytesIO()
    width, height = landscape(A4)  # Use landscape for timetable
    margin = 50
    p = canvas.Canvas(buffer, pagesize=landscape(A4))
    
    # Define styles for cell content
    styles = getSampleStyleSheet()
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        leading=10  # Line spacing
    )
    
    # Define color palette
    primary_color = colors.HexColor('#2B579A')    # School blue
    light_gray = colors.HexColor('#F2F2F2')       # Background gray
    header_bg = colors.HexColor('#2B579A')        # Header background
    header_text = colors.white                    # Header text color
    
    # Add an eye-catching header at the top of the page
    # Draw a colored rectangle as background for the header
    p.setFillColor(header_bg)
    p.rect(0, height - 100, width, 100, fill=1, stroke=0)
    
    # Add title text on the colored background
    p.setFillColor(header_text)
    p.setFont("Helvetica-Bold", 32)
    p.drawCentredString(width/2, height - 45, f"CLASS TIMETABLE")
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(width/2, height - 75, f"{class_display}")
    
    # Add a thin decorative line under the header
    p.setStrokeColor(colors.HexColor('#FFD700'))  # Gold color line
    p.setLineWidth(3)
    p.line(margin, height - 110, width - margin, height - 110)
    
    # Title and info section with prominent class name
    p.setFillColor(primary_color)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(margin, height - 140, f"Schedule for Class {class_display}")
    
    # Add school name and section
    p.setFont("Helvetica-Bold", 14)
    p.drawString(margin, height - 160, "School Management System")
    
    # Add generation details
    p.setFont("Helvetica", 10)
    p.drawString(margin, height - 180, f"Generated on: {timezone.now().strftime('%d %B %Y %H:%M')}")
    
    # Create table header (period, days)
    data = [["Period"]]
    for day_id, day_name in TimeTable.DAY_CHOICES:
        data[0].append(day_name)
    
    # Fill table data with Paragraph objects for proper text wrapping
    for period_id, period_name in TimeTable.PERIOD_CHOICES:
        row = [period_name]
        for day_id, day_name in TimeTable.DAY_CHOICES:
            entry = timetable_by_day.get(day_id, {}).get(period_id, None)
            if entry:
                cell_text = f"{entry.subject.name}<br/>{entry.teacher.first_name} {entry.teacher.last_name}<br/>Room: {entry.room_number}<br/>{entry.start_time.strftime('%H:%M')} - {entry.end_time.strftime('%H:%M')}"
                row.append(Paragraph(cell_text, cell_style))
            else:
                row.append(Paragraph("-", cell_style))
        data.append(row)
    
    # Set up table with appropriate dimensions
    # Calculate available space
    available_height = height - 200  # Top margin + header
    
    # Calculate row heights and column widths dynamically
    num_rows = len(data)
    row_height = min(50, available_height / (num_rows + 1))  # +1 for header
    
    col_widths = [60]  # Period column
    day_width = (width - 2*margin - 60) / len(TimeTable.DAY_CHOICES)
    col_widths.extend([day_width] * len(TimeTable.DAY_CHOICES))
    
    # Set row heights
    row_heights = [30]  # Header row
    row_heights.extend([row_height] * (len(data) - 1))
    
    # Create the table
    table = Table(data, colWidths=col_widths, rowHeights=row_heights)
    
    # Style the table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('BACKGROUND', (0, 1), (0, -1), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 1), (0, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (0, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.white, light_gray])
    ]))
    
    # Position at the top of the space, leaving room for header
    y_position = height - 200 - (row_height * num_rows)
    y_position = max(y_position, 50)  # Ensure it doesn't go below bottom margin
    
    # Draw table
    table.wrapOn(p, width - 2*margin, height)
    table.drawOn(p, margin, y_position)
    
    # Footer
    p.setFont("Helvetica", 8)
    p.drawString(margin, 30, "This is a computer-generated document. For official records only.")
    p.drawString(width - 150, 30, f"Class {class_display} Timetable")
    
    # Finalize and save PDF
    p.showPage()
    p.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create response
    from django.http import HttpResponse
    filename = f"class_{class_name}_timetable_{timezone.now().strftime('%Y%m%d')}.pdf"
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

@login_required
def generate_teacher_timetable_pdf(request, teacher_id=None):
    # Check if teacher_id is provided in the URL or as a GET parameter
    if not teacher_id and 'teacher' in request.GET:
        teacher_id = request.GET.get('teacher')
    
    if not teacher_id:
        messages.error(request, "Please select a teacher to generate PDF")
        return redirect('timetable:teacher_timetable')
    
    # Get the teacher object
    teacher = get_object_or_404(Teacher, id=teacher_id)
    
    # Get timetable entries for the selected teacher
    timetables = TimeTable.objects.filter(teacher=teacher).order_by('day', 'period')
    
    # Group timetables by day and period for easy display
    timetable_by_day = {}
    for entry in timetables:
        if entry.day not in timetable_by_day:
            timetable_by_day[entry.day] = {}
        timetable_by_day[entry.day][entry.period] = entry
    
    # Create a BytesIO buffer for the PDF
    from io import BytesIO
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from django.utils import timezone
    
    buffer = BytesIO()
    width, height = landscape(A4)  # Use landscape for timetable
    margin = 50
    p = canvas.Canvas(buffer, pagesize=landscape(A4))
    
    # Define styles for cell content
    styles = getSampleStyleSheet()
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        leading=10  # Line spacing
    )
    
    # Define color palette
    primary_color = colors.HexColor('#2B579A')    # School blue
    light_gray = colors.HexColor('#F2F2F2')       # Background gray
    header_bg = colors.HexColor('#2B579A')        # Header background
    header_text = colors.white                    # Header text color
    
    # Add an eye-catching header at the top of the page
    # Draw a colored rectangle as background for the header
    p.setFillColor(header_bg)
    p.rect(0, height - 100, width, 100, fill=1, stroke=0)
    
    # Add title text on the colored background
    p.setFillColor(header_text)
    p.setFont("Helvetica-Bold", 32)
    teacher_name = f"{teacher.first_name} {teacher.last_name}".upper()
    p.drawCentredString(width/2, height - 45, f"TEACHER TIMETABLE")
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(width/2, height - 75, f"{teacher_name}")
    
    # Add a thin decorative line under the header
    p.setStrokeColor(colors.HexColor('#FFD700'))  # Gold color line
    p.setLineWidth(3)
    p.line(margin, height - 110, width - margin, height - 110)
    
    # Title and info section with prominent teacher name
    p.setFillColor(primary_color)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(margin, height - 140, f"Schedule for {teacher.first_name} {teacher.last_name}")
    
    # Add school name and teacher details
    p.setFont("Helvetica-Bold", 14)
    p.drawString(margin, height - 160, "School Management System")
    
    # Add teacher role and ID
    p.setFont("Helvetica", 10)
    p.drawString(margin, height - 180, f"Teacher ID: {teacher.employee_id}")
    p.drawString(margin, height - 195, f"Specialization: {teacher.specialization}")
    p.drawString(margin + 350, height - 180, f"Generated on: {timezone.now().strftime('%d %B %Y %H:%M')}")
    
    # Create table header (period, days)
    data = [["Period"]]
    for day_id, day_name in TimeTable.DAY_CHOICES:
        data[0].append(day_name)
    
    # Fill table data with Paragraph objects for proper text wrapping
    for period_id, period_name in TimeTable.PERIOD_CHOICES:
        row = [period_name]
        for day_id, day_name in TimeTable.DAY_CHOICES:
            entry = timetable_by_day.get(day_id, {}).get(period_id, None)
            if entry:
                cell_text = f"Class: {entry.get_class_name_display()}<br/>{entry.subject.name}<br/>Room: {entry.room_number}<br/>{entry.start_time.strftime('%H:%M')} - {entry.end_time.strftime('%H:%M')}"
                row.append(Paragraph(cell_text, cell_style))
            else:
                row.append(Paragraph("-", cell_style))
        data.append(row)
    
    # Set up table with appropriate dimensions
    # Calculate available space
    available_height = height - 210  # Top margin + header + teacher info
    
    # Calculate row heights and column widths dynamically
    num_rows = len(data)
    row_height = min(50, available_height / (num_rows + 1))  # +1 for header
    
    col_widths = [60]  # Period column
    day_width = (width - 2*margin - 60) / len(TimeTable.DAY_CHOICES)
    col_widths.extend([day_width] * len(TimeTable.DAY_CHOICES))
    
    # Set row heights
    row_heights = [30]  # Header row
    row_heights.extend([row_height] * (len(data) - 1))
    
    # Create the table
    table = Table(data, colWidths=col_widths, rowHeights=row_heights)
    
    # Style the table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('BACKGROUND', (0, 1), (0, -1), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 1), (0, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (0, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.white, light_gray])
    ]))
    
    # Position at the top of the space, leaving room for header and teacher info
    y_position = height - 210 - (row_height * num_rows)
    y_position = max(y_position, 50)  # Ensure it doesn't go below bottom margin
    
    # Draw table
    table.wrapOn(p, width - 2*margin, height)
    table.drawOn(p, margin, y_position)
    
    # Footer
    p.setFont("Helvetica", 8)
    p.drawString(margin, 30, "This is a computer-generated document. For official records only.")
    p.drawString(width - 200, 30, f"{teacher.first_name} {teacher.last_name}'s Timetable")
    
    # Finalize and save PDF
    p.showPage()
    p.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create response
    from django.http import HttpResponse
    filename = f"teacher_{teacher.employee_id}_timetable_{timezone.now().strftime('%Y%m%d')}.pdf"
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

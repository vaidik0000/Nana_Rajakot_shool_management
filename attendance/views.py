from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from students.models import Student
from .models import Attendance, AttendanceReport, TeacherAttendance
from .forms import AttendanceForm
from core.decorators import new_user_restricted, admin_required
from school_teachers.models import Teacher
from django.contrib.auth.models import User
from django.db.models import Q
import calendar
import locale
from datetime import date
from django.http import JsonResponse
from django.db.models import Count
import csv
from django.http import HttpResponse

# Student Attendance Views
@login_required
@new_user_restricted
def attendance_create(request):
    """
    View to create a single attendance record
    """
    # Check if the user is a student (students cannot record attendance)
    if hasattr(request, 'user_type') and request.user_type == 'student':
        messages.error(request, "Students are not allowed to record attendance.")
        return redirect('attendance:list')

    # Get all class choices from Student model
    class_names = Student.CLASS_CHOICES
    selected_class = request.POST.get('class_name', '')
    date_value = request.POST.get('date', timezone.now().strftime('%Y-%m-%d'))
    remarks = request.POST.get('remarks', '')
    students = []
    
    # If a class is selected and not submitting final attendance, load students
    if selected_class and 'submit_attendance' not in request.POST:
        students = Student.objects.filter(class_name=selected_class, is_active=True)
        
    # Process the form for final submission    
    if request.method == 'POST' and 'submit_attendance' in request.POST:
        student_ids = request.POST.getlist('student_ids')
        
        if student_ids and date_value:
            success_count = 0
            for student_id in student_ids:
                status = request.POST.get(f'status_{student_id}')
                if status:
                    student = get_object_or_404(Student, id=student_id)
                    
                    # Check if attendance already exists
                    existing_attendance = Attendance.objects.filter(
                        student=student,
                        date=date_value
                    ).first()
                    
                    if existing_attendance:
                        # Update existing record
                        existing_attendance.status = status
                        existing_attendance.remarks = remarks
                        existing_attendance.recorded_by = request.user
                        existing_attendance.save()
                    else:
                        # Create new record
                        Attendance.objects.create(
                            student=student,
                            date=date_value,
                            status=status,
                            remarks=remarks,
                            recorded_by=request.user
                        )
                    success_count += 1
            
            if success_count > 0:
                messages.success(request, f"Attendance recorded successfully for {success_count} students.")
                return redirect('attendance:list')
            else:
                messages.error(request, "No attendance records were created. Please select status for students.")
    
    # Pass variables needed by the template
    context = {
        'class_names': class_names,
        'selected_class': selected_class,
        'date_value': date_value,
        'remarks': remarks,
        'students': students,
    }
    
    return render(request, 'attendance/take_attendance.html', context)

@login_required
def attendance_list(request):
    """
    View to list all attendance records
    If the user is a student, only show their own records
    """
    # Get all class choices for filtering
    class_choices = Student.CLASS_CHOICES
    
    # Initialize queryset
    attendance_records = Attendance.objects.all().select_related('student', 'recorded_by')
    
    # Check if the user is a student
    is_student = hasattr(request, 'user_type') and request.user_type == 'student'
    
    if is_student:
        # Show only the logged-in student's attendance records
        student = request.student
        attendance_records = attendance_records.filter(student=student)
    
    # Apply filters if provided
    class_name = request.GET.get('class_name')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if class_name:
        attendance_records = attendance_records.filter(student__class_name=class_name)
    
    if status:
        attendance_records = attendance_records.filter(status=status)
    
    if date_from:
        attendance_records = attendance_records.filter(date__gte=date_from)
    
    if date_to:
        attendance_records = attendance_records.filter(date__lte=date_to)
    
    # Order by date (newest first)
    attendance_records = attendance_records.order_by('-date')
    
    return render(request, 'attendance/attendance_list.html', {
        'attendance_records': attendance_records,
        'class_choices': class_choices,
        'is_student': is_student
    })

@login_required
def download_attendance_records(request):
    """
    View to download attendance records as a CSV file
    Supports the same filters as the attendance list view
    """
    # Initialize response for CSV download with BOM for Excel compatibility
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="attendance_records_{timestamp}.csv"'
    
    # Create CSV writer
    writer = csv.writer(response)
    
    # Write title and generation info
    current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    writer.writerow(['Student Attendance Records'])
    writer.writerow([f'Generated on: {current_time}'])
    
    # Add filter information
    class_name = request.GET.get('class_name')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    writer.writerow(['Filter criteria:'])
    if class_name:
        class_display = dict(Student.CLASS_CHOICES).get(class_name, class_name)
        writer.writerow([f'Class: {class_display}'])
    if status:
        status_display = dict(Attendance.STATUS_CHOICES).get(status, status.title())
        writer.writerow([f'Status: {status_display}'])
    if date_from:
        writer.writerow([f'From Date: {date_from}'])
    if date_to:
        writer.writerow([f'To Date: {date_to}'])
    
    writer.writerow([]) # Empty row as separator
    
    # Write headers with clear column names
    writer.writerow([
        'Date', 
        'Student Name', 
        'Roll Number', 
        'Class', 
        'Attendance Status', 
        'Remarks', 
        'Recorded By'
    ])
    
    # Initialize queryset
    attendance_records = Attendance.objects.all().select_related('student', 'recorded_by')
    
    # Check if the user is a student
    is_student = hasattr(request, 'user_type') and request.user_type == 'student'
    
    if is_student:
        # Students can only download their own records
        student = request.student
        attendance_records = attendance_records.filter(student=student)
    
    # Apply filters if provided
    class_name = request.GET.get('class_name')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if class_name:
        attendance_records = attendance_records.filter(student__class_name=class_name)
    
    if status:
        attendance_records = attendance_records.filter(status=status)
    
    if date_from:
        attendance_records = attendance_records.filter(date__gte=date_from)
    
    if date_to:
        attendance_records = attendance_records.filter(date__lte=date_to)
    
    # Order by date (newest first)
    attendance_records = attendance_records.order_by('-date')
    
    # Write data rows
    for record in attendance_records:
        # Format the date as DD/MM/YYYY for better readability in CSV
        formatted_date = record.date.strftime("%d/%m/%Y") if record.date else ""
        
        # Handle the recorded_by field properly
        if record.recorded_by:
            if record.recorded_by.get_full_name().strip():
                recorded_by = record.recorded_by.get_full_name()
            else:
                recorded_by = record.recorded_by.username
        else:
            recorded_by = "System"
            
        writer.writerow([
            formatted_date,
            f"{record.student.first_name} {record.student.last_name}",
            record.student.roll_number,
            record.student.get_class_name_display(),
            record.get_status_display(),
            record.remarks or "",
            recorded_by
        ])
    
    return response

@login_required
def attendance_detail(request, pk):
    """
    View to show details of an attendance record
    """
    attendance = get_object_or_404(Attendance, pk=pk)
    
    # Check if the user is a student and it's not their own attendance
    is_student = hasattr(request, 'user_type') and request.user_type == 'student'
    if is_student and attendance.student != request.student:
        messages.error(request, "You can only view your own attendance records.")
        return redirect('attendance:list')
    
    # Get student's other attendance records for reference
    other_records = Attendance.objects.filter(
        student=attendance.student
    ).exclude(pk=attendance.pk).order_by('-date')[:5]
    
    return render(request, 'attendance/attendance_detail.html', {
        'attendance': attendance,
        'other_records': other_records,
        'is_student': is_student
    })

@login_required
@new_user_restricted
def attendance_edit(request, pk):
    """
    View to edit an attendance record
    """
    # Check if the user is a student (students cannot edit attendance)
    if hasattr(request, 'user_type') and request.user_type == 'student':
        messages.error(request, "Students are not allowed to edit attendance records.")
        return redirect('attendance:list')
        
    attendance = get_object_or_404(Attendance, pk=pk)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        remarks = request.POST.get('remarks', '')
        
        if status:
            try:
                attendance.status = status
                attendance.remarks = remarks
                attendance.save()
                messages.success(request, "Attendance record updated successfully.")
                return redirect('attendance:detail', pk=attendance.pk)
            except Exception as e:
                messages.error(request, f"Error updating attendance record: {str(e)}")
    
    return render(request, 'attendance/edit_attendance.html', {
        'attendance': attendance,
        'status_choices': Attendance.STATUS_CHOICES
    })

@login_required
@new_user_restricted
def attendance_delete(request, pk):
    """
    View to delete an attendance record
    """
    # Check if the user is a student (students cannot delete attendance)
    if hasattr(request, 'user_type') and request.user_type == 'student':
        messages.error(request, "Students are not allowed to delete attendance records.")
        return redirect('attendance:list')
        
    attendance = get_object_or_404(Attendance, pk=pk)
    
    if request.method == 'POST':
        try:
            attendance.delete()
            messages.success(request, "Attendance record deleted successfully.")
            return redirect('attendance:list')
        except Exception as e:
            messages.error(request, f"Error deleting attendance record: {str(e)}")
    
    return render(request, 'attendance/delete_attendance.html', {'attendance': attendance})

@login_required
@new_user_restricted
def attendance_bulk_create(request):
    """
    View to create attendance records in bulk for an entire class
    """
    # Check if the user is a student (students cannot record attendance)
    if hasattr(request, 'user_type') and request.user_type == 'student':
        messages.error(request, "Students are not allowed to record attendance.")
        return redirect('attendance:list')
        
    # Get all class choices from Student model
    class_choices = Student.CLASS_CHOICES
    
    if request.method == 'POST':
        class_name = request.POST.get('class_name')
        date_value = request.POST.get('date')
        status = request.POST.get('status')
        remarks = request.POST.get('remarks', '')
        
        if class_name and date_value and status:
            try:
                # Get all active students in the selected class
                students = Student.objects.filter(class_name=class_name, is_active=True)
                
                if students.exists():
                    success_count = 0
                    error_count = 0
                    
                    # Process attendance for each student
                    for student in students:
                        try:
                            # Check if an attendance record already exists for this student on this date
                            attendance, created = Attendance.objects.update_or_create(
                                student=student,
                                date=date_value,
                                defaults={
                                    'status': status,
                                    'remarks': remarks,
                                    'recorded_by': request.user
                                }
                            )
                            success_count += 1
                        except Exception as e:
                            error_count += 1
                            messages.error(request, f"Error recording attendance for {student.first_name}: {str(e)}")
                    
                    # Show appropriate message based on results
                    if success_count > 0:
                        messages.success(request, f"Successfully recorded attendance for {success_count} student(s) in {dict(class_choices).get(class_name)} class.")
                        if error_count > 0:
                            messages.warning(request, f"Failed to record attendance for {error_count} student(s).")
                    return redirect('attendance:list')
                else:
                    messages.warning(request, f"No active students found in the selected class.")
            except Exception as e:
                messages.error(request, f"Error recording bulk attendance: {str(e)}")
    
    # Render the bulk attendance form
    return render(request, 'attendance/bulk_attendance.html', {
        'class_choices': class_choices,
        'status_choices': Attendance.STATUS_CHOICES,
        'today': timezone.now().date()
    })

# Teacher Attendance Views
@login_required
@admin_required
def teacher_attendance_create(request):
    """View for recording teacher attendance - Admin only"""
    # Get all teachers
    teachers = Teacher.objects.all()
    
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher')
        date_str = request.POST.get('date')
        status = request.POST.get('status')
        remarks = request.POST.get('remarks', '')
        
        if not all([teacher_id, date_str, status]):
            messages.error(request, "Please provide all required fields")
            return render(request, 'attendance/teacher_attendance_create.html', {
                'teachers': teachers,
                'today': timezone.now().date()
            })
        
        try:
            teacher = get_object_or_404(Teacher, id=teacher_id)
            teacher_full_name = f"{teacher.first_name} {teacher.last_name}"
            
            # Check if attendance already exists for this teacher on this date
            existing_attendance = TeacherAttendance.objects.filter(
                teacher=teacher, 
                date=date_str
            ).first()
            
            if existing_attendance:
                messages.warning(request, f"Attendance for {teacher_full_name} on {date_str} already exists. It has been updated.")
                existing_attendance.status = status
                existing_attendance.remarks = remarks
                existing_attendance.recorded_by = request.user
                existing_attendance.save()
            else:
                # Create new attendance record
                TeacherAttendance.objects.create(
                    teacher=teacher,
                    date=date_str,
                    status=status,
                    remarks=remarks,
                    recorded_by=request.user
                )
                messages.success(request, f"Attendance for {teacher_full_name} recorded successfully")
            
            return redirect('attendance:teacher_attendance_list')
        except Exception as e:
            messages.error(request, f"Error recording attendance: {str(e)}")
    
    context = {
        'teachers': teachers,
        'today': timezone.now().date(),
    }
    return render(request, 'attendance/teacher_attendance_create.html', context)

@login_required
@admin_required
def teacher_attendance_list(request):
    """View for listing teacher attendance records - Admin only"""
    # Get filter parameters
    teacher_id = request.GET.get('teacher')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Start with all attendance records
    attendance_records = TeacherAttendance.objects.all()
    
    # Apply filters if provided
    if teacher_id:
        attendance_records = attendance_records.filter(teacher_id=teacher_id)
    
    if status:
        attendance_records = attendance_records.filter(status=status)
    
    if date_from:
        attendance_records = attendance_records.filter(date__gte=date_from)
    
    if date_to:
        attendance_records = attendance_records.filter(date__lte=date_to)
    
    # Get all teachers for the filter dropdown
    teachers = Teacher.objects.all()
    
    context = {
        'attendance_records': attendance_records,
        'teachers': teachers,
        'statuses': TeacherAttendance.STATUS_CHOICES,
        'selected_teacher': teacher_id,
        'selected_status': status,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'attendance/teacher_attendance_list.html', context)

@login_required
@admin_required
def teacher_attendance_detail(request, pk):
    """View for viewing teacher attendance detail - Admin only"""
    attendance = get_object_or_404(TeacherAttendance, pk=pk)
    
    context = {
        'attendance': attendance,
    }
    return render(request, 'attendance/teacher_attendance_detail.html', context)

@login_required
@admin_required
def teacher_attendance_edit(request, pk):
    """View for editing teacher attendance - Admin only"""
    attendance = get_object_or_404(TeacherAttendance, pk=pk)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        remarks = request.POST.get('remarks', '')
        
        if not status:
            messages.error(request, "Please select an attendance status")
            return render(request, 'attendance/teacher_attendance_edit.html', {'attendance': attendance})
        
        attendance.status = status
        attendance.remarks = remarks
        attendance.recorded_by = request.user
        attendance.save()
        
        messages.success(request, "Attendance record updated successfully")
        return redirect('attendance:teacher_attendance_detail', pk=attendance.pk)
    
    context = {
        'attendance': attendance,
    }
    return render(request, 'attendance/teacher_attendance_edit.html', context)

@login_required
@admin_required
def teacher_attendance_delete(request, pk):
    """View for deleting teacher attendance - Admin only"""
    attendance = get_object_or_404(TeacherAttendance, pk=pk)
    
    if request.method == 'POST':
        teacher_name = f"{attendance.teacher.first_name} {attendance.teacher.last_name}"
        attendance.delete()
        messages.success(request, f"Attendance record for {teacher_name} has been deleted")
        return redirect('attendance:teacher_attendance_list')
    
    context = {
        'attendance': attendance,
    }
    return render(request, 'attendance/teacher_attendance_delete.html', context)

@login_required
@admin_required
def teacher_attendance_bulk_create(request):
    """View for recording attendance for multiple teachers at once - Admin only"""
    # Get all teachers
    teachers = Teacher.objects.all()
    
    if request.method == 'POST':
        teacher_ids = request.POST.getlist('teacher_ids')
        date = request.POST.get('date')
        status = request.POST.get('status')
        remarks = request.POST.get('remarks', '')
        
        if not all([teacher_ids, date, status]):
            messages.error(request, "Please provide all required fields")
            return render(request, 'attendance/teacher_bulk_attendance.html', {
                'teachers': teachers,
                'today': timezone.now().date(),
            })
        
        # Process each teacher
        success_count = 0
        update_count = 0
        
        for teacher_id in teacher_ids:
            try:
                teacher = get_object_or_404(Teacher, id=teacher_id)
                
                # Check if attendance already exists for this teacher on this date
                existing_attendance = TeacherAttendance.objects.filter(teacher=teacher, date=date).first()
                
                if existing_attendance:
                    # Update existing record
                    existing_attendance.status = status
                    existing_attendance.remarks = remarks
                    existing_attendance.recorded_by = request.user
                    existing_attendance.save()
                    update_count += 1
                else:
                    # Create new attendance record
                    TeacherAttendance.objects.create(
                        teacher=teacher,
                        date=date,
                        status=status,
                        remarks=remarks,
                        recorded_by=request.user
                    )
                    success_count += 1
            except Exception as e:
                messages.error(request, f"Error recording attendance for teacher ID {teacher_id}: {str(e)}")
        
        if success_count > 0 or update_count > 0:
            message_parts = []
            if success_count > 0:
                message_parts.append(f"{success_count} new attendance records created")
            if update_count > 0:
                message_parts.append(f"{update_count} existing records updated")
            
            messages.success(request, f"Attendance recorded successfully: {', '.join(message_parts)}")
            return redirect('attendance:teacher_attendance_list')
        else:
            messages.error(request, "No attendance records were created or updated")
    
    context = {
        'teachers': teachers,
        'today': timezone.now().date(),
    }
    return render(request, 'attendance/teacher_bulk_attendance.html', context)

@login_required
def attendance_report(request):
    """
    Generate attendance reports based on different criteria
    for both student and teacher attendance
    """
    # Initialize context variables
    context = {
        'students': Student.objects.all(),
        'classes': Student.CLASS_CHOICES,  # Use the class choices from Student model
        'teachers': Teacher.objects.all(),  # Get all teachers for the dropdown
        'report_submitted': False
    }
    
    if request.GET:
        context['report_submitted'] = True
        report_type = request.GET.get('report_type')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # Validate input parameters
        if not report_type or not start_date or not end_date:
            messages.error(request, 'Please provide all required parameters')
            return render(request, 'attendance/attendance_report.html', context)
        
        # Store filter criteria in context
        context['report_type'] = report_type
        context['start_date'] = start_date
        context['end_date'] = end_date
        
        # Initialize query for attendance records
        date_range_query = Q(date__range=[start_date, end_date])
        
        # Check if we're generating a report for teachers or students
        if report_type == 'teacher':
            teacher_id = request.GET.get('teacher_id')
            if not teacher_id:
                messages.error(request, 'Please select a teacher')
                return render(request, 'attendance/attendance_report.html', context)
            
            # Get teacher attendance records
            teacher = get_object_or_404(Teacher, id=teacher_id)
            teacher_query = Q(teacher=teacher) & date_range_query
            attendance_records = TeacherAttendance.objects.filter(teacher_query).order_by('-date')
            
            # Calculate statistics for teacher attendance
            present_count = attendance_records.filter(status='present').count()
            absent_count = attendance_records.filter(status='absent').count()
            late_count = attendance_records.filter(status='late').count()
            half_day_count = attendance_records.filter(status='half_day').count()
            total_records = attendance_records.count()
            
            context.update({
                'teacher_name': f"{teacher.first_name} {teacher.last_name}",
                'teacher_id': teacher_id,
                'attendance_records': attendance_records,
                'present_count': present_count,
                'absent_count': absent_count,
                'late_count': late_count,
                'half_day_count': half_day_count,
                'total_days': total_records,
                'is_teacher_report': True
            })
        else:
            # Student/Class attendance reports
            attendance_query = date_range_query
            
            if report_type == 'student':
                student_id = request.GET.get('student_id')
                if not student_id:
                    messages.error(request, 'Please select a student')
                    return render(request, 'attendance/attendance_report.html', context)
                
                attendance_query &= Q(student_id=student_id)
                student = get_object_or_404(Student, id=student_id)
                context['student_name'] = f"{student.first_name} {student.last_name}"
                context['student_id'] = student_id
                
            elif report_type == 'class':
                class_name = request.GET.get('class_name')  # Using class_name from form
                if not class_name:
                    messages.error(request, 'Please select a class')
                    return render(request, 'attendance/attendance_report.html', context)
                
                attendance_query &= Q(student__class_name=class_name)
                class_display = dict(Student.CLASS_CHOICES).get(class_name, class_name)
                context['class_name'] = class_display
                context['class_id'] = class_name  # Keep for backward compatibility
            
            # Fetch student attendance records based on query
            attendance_records = Attendance.objects.filter(attendance_query).order_by('-date')
            context['attendance_records'] = attendance_records
            context['is_teacher_report'] = False
            
            # Calculate statistics
            present_count = attendance_records.filter(status='present').count()
            absent_count = attendance_records.filter(status='absent').count()
            late_count = attendance_records.filter(status='late').count()
            half_day_count = attendance_records.filter(status='half_day').count()
            total_records = attendance_records.count()
            
            context.update({
                'present_count': present_count,
                'absent_count': absent_count,
                'late_count': late_count,
                'half_day_count': half_day_count,
                'total_days': total_records,
            })
        
        # Calculate attendance percentage (same calculation for both teacher and student)
        if total_records > 0:
            # Consider present and late as attendance
            attendance_percentage = round(((present_count + late_count) / total_records) * 100, 2)
            context['attendance_percentage'] = attendance_percentage
        else:
            context['attendance_percentage'] = 0
            
    return render(request, 'attendance/attendance_report.html', context)

@login_required
@admin_required
def teacher_attendance_report(request):
    """
    View to display attendance reports for teachers - Admin only
    """
    # Get all teachers
    from django.contrib.auth import get_user_model
    User = get_user_model()
    teachers = User.objects.filter(is_staff=True).exclude(is_superuser=True)
    
    # Initialize variables
    attendance_records = []
    selected_teacher = None
    present_count = absent_count = late_count = half_day_count = 0
    attendance_percentage = 0
    start_date = end_date = None
    
    # Process the request if filters are applied
    if request.GET.get('teacher_id') and request.GET.get('start_date') and request.GET.get('end_date'):
        teacher_id = request.GET.get('teacher_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        try:
            # Get the selected teacher
            selected_teacher = User.objects.get(id=teacher_id)
            
            # Query attendance records for the selected teacher and date range
            from attendance.models import TeacherAttendance
            from django.db.models import Q
            
            attendance_records = TeacherAttendance.objects.filter(
                teacher=selected_teacher,
                date__range=[start_date, end_date]
            ).order_by('date')
            
            # Calculate statistics
            total_records = attendance_records.count()
            if total_records > 0:
                present_count = attendance_records.filter(status='present').count()
                absent_count = attendance_records.filter(status='absent').count()
                late_count = attendance_records.filter(status='late').count()
                half_day_count = attendance_records.filter(status='half_day').count()
                
                # Calculate attendance percentage (present + late + half_day) / total
                attendance_percentage = round(((present_count + late_count + (half_day_count * 0.5)) / total_records) * 100, 2)
            
            if not attendance_records:
                messages.info(request, f"No attendance records found for {selected_teacher.get_full_name()} in the selected date range.")
            
        except User.DoesNotExist:
            messages.error(request, "Selected teacher not found.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
    
    context = {
        'teachers': teachers,
        'selected_teacher': selected_teacher,
        'selected_teacher_id': int(teacher_id) if 'teacher_id' in request.GET and request.GET.get('teacher_id') else None,
        'attendance_records': attendance_records,
        'start_date': start_date,
        'end_date': end_date,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'half_day_count': half_day_count,
        'attendance_percentage': attendance_percentage,
    }
    return render(request, 'attendance/teacher_attendance_report.html', context)

@login_required
def attendance_calendar(request):
    """
    View to display a calendar of student attendance
    """
    # Get current date if not specified
    current_date = datetime.now().date()
    
    # Get view parameters from GET request
    view_type = request.GET.get('view_type', 'student')  # Default to student view
    month = int(request.GET.get('month', current_date.month))
    year = int(request.GET.get('year', current_date.year))
    student_id = request.GET.get('student')
    
    # Get the selected student if specified
    selected_student = None
    if student_id:
        selected_student = get_object_or_404(Student, id=student_id)
    elif hasattr(request, 'user_type') and request.user_type == 'student':
        # If user is a student, show their attendance by default
        selected_student = request.student
    
    # Get all students for dropdown (for teachers/admins)
    students = Student.objects.all().order_by('first_name', 'last_name')
    
    # Prepare month and year dropdown data
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    current_year = datetime.now().year
    years = list(range(current_year - 2, current_year + 1))
    
    # Calculate previous and next month for navigation
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
        
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    # Initialize attendance data and statistics
    present_count = 0
    absent_count = 0
    late_count = 0
    half_day_count = 0
    total_days = 0
    
    # Get calendar data for the selected month/year
    cal = calendar.monthcalendar(year, month)
    month_days = max(map(max, cal))
    
    # Initialize the attendance lookup dictionary
    attendance_lookup = {}
    
    # Get attendance data for the selected student or all students
    if selected_student:
        start_date = date(year, month, 1)
        # Find the last day of the month
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
            
        attendance_records = Attendance.objects.filter(
            student=selected_student,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Count statistics
        present_count = attendance_records.filter(status='present').count()
        absent_count = attendance_records.filter(status='absent').count()
        late_count = attendance_records.filter(status='late').count()
        half_day_count = attendance_records.filter(status='half_day').count()
        total_days = present_count + absent_count + late_count + half_day_count
        
        # Create a dictionary for easier lookup of attendance by date
        for record in attendance_records:
            attendance_lookup[record.date.day] = record
    
    # Calculate percentages
    if total_days > 0:
        present_percent = round((present_count / total_days) * 100, 1)
        absent_percent = round((absent_count / total_days) * 100, 1)
        late_percent = round((late_count / total_days) * 100, 1)
        half_day_percent = round((half_day_count / total_days) * 100, 1)
    else:
        present_percent = absent_percent = late_percent = half_day_percent = 0.0
    
    # Build calendar data structure
    calendar_data = []
    today = date.today()
    for week in cal:
        week_data = []
        for day in week:
            if day != 0:
                day_date = date(year, month, day)
                is_today = (day_date == today)
                attendance = attendance_lookup.get(day)
                week_data.append((day, True, is_today, attendance))
            else:
                week_data.append((0, False, False, None))
        calendar_data.append(week_data)
    
    context = {
        'calendar_data': calendar_data,
        'current_month': month,
        'current_month_name': calendar.month_name[month],
        'current_year': year,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'months': months,
        'years': years,
        'students': students,
        'selected_student': selected_student,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'half_day_count': half_day_count,
        'total_days': total_days,
        'present_percent': present_percent,
        'absent_percent': absent_percent,
        'late_percent': late_percent,
        'half_day_percent': half_day_percent,
    }
    
    return render(request, 'attendance/attendance_calendar.html', context)

@login_required
@admin_required
def teacher_attendance_calendar(request):
    """
    View to display a calendar of teacher attendance - Admin only
    """
    # Get current date if not specified
    current_date = datetime.now().date()
    
    # Get view parameters from GET request
    month = int(request.GET.get('month', current_date.month))
    year = int(request.GET.get('year', current_date.year))
    teacher_id = request.GET.get('teacher')
    
    # Get the selected teacher if specified
    selected_teacher = None
    if teacher_id:
        selected_teacher = get_object_or_404(Teacher, id=teacher_id)
    elif hasattr(request, 'user_type') and request.user_type == 'teacher':
        # If user is a teacher, show their attendance by default
        selected_teacher = request.teacher
    
    # Get all teachers for dropdown
    teachers = Teacher.objects.all().order_by('first_name', 'last_name')
    
    # Prepare month and year dropdown data
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    current_year = datetime.now().year
    years = list(range(current_year - 2, current_year + 1))
    
    # Calculate previous and next month for navigation
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
        
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    # Initialize attendance data and statistics
    present_count = 0
    absent_count = 0
    late_count = 0
    half_day_count = 0
    total_days = 0
    
    # Get calendar data for the selected month/year
    cal = calendar.monthcalendar(year, month)
    month_days = max(map(max, cal))
    
    # Initialize the attendance lookup dictionary
    attendance_lookup = {}
    
    # Get attendance data for the selected teacher
    if selected_teacher:
        start_date = date(year, month, 1)
        # Find the last day of the month
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
            
        attendance_records = TeacherAttendance.objects.filter(
            teacher=selected_teacher,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Count statistics
        present_count = attendance_records.filter(status='present').count()
        absent_count = attendance_records.filter(status='absent').count()
        late_count = attendance_records.filter(status='late').count()
        half_day_count = attendance_records.filter(status='half_day').count()
        total_days = present_count + absent_count + late_count + half_day_count
        
        # Create a dictionary for easier lookup of attendance by date
        for record in attendance_records:
            attendance_lookup[record.date.day] = record
    
    # Calculate percentages
    if total_days > 0:
        present_percent = round((present_count / total_days) * 100, 1)
        absent_percent = round((absent_count / total_days) * 100, 1)
        late_percent = round((late_count / total_days) * 100, 1)
        half_day_percent = round((half_day_count / total_days) * 100, 1)
    else:
        present_percent = absent_percent = late_percent = half_day_percent = 0.0
    
    # Build calendar data structure
    calendar_data = []
    today = date.today()
    for week in cal:
        week_data = []
        for day in week:
            if day != 0:
                day_date = date(year, month, day)
                is_today = (day_date == today)
                attendance = attendance_lookup.get(day)
                week_data.append((day, True, is_today, attendance))
            else:
                week_data.append((0, False, False, None))
        calendar_data.append(week_data)
    
    context = {
        'calendar_data': calendar_data,
        'current_month': month,
        'current_month_name': calendar.month_name[month],
        'current_year': year,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'months': months,
        'years': years,
        'teachers': teachers,
        'selected_teacher': selected_teacher,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'half_day_count': half_day_count,
        'total_days': total_days,
        'present_percent': present_percent,
        'absent_percent': absent_percent,
        'late_percent': late_percent,
        'half_day_percent': half_day_percent,
    }
    
    return render(request, 'attendance/teacher_attendance_calendar.html', context)

def get_attendance_detail(request):
    """
    API endpoint to get detailed attendance data with student and teacher names
    for the specified date range.
    """
    try:
        # Get date range from request
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        
        # If no dates provided, use default (last 30 days)
        if not start_date or not end_date:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
        else:
            # Parse dates from string
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Query student attendance for the date range
        student_attendance = Attendance.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).select_related('student').order_by('date', 'student__first_name')
        
        # Query teacher attendance for the date range
        teacher_attendance = TeacherAttendance.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).select_related('teacher').order_by('date', 'teacher__first_name')
        
        # Prepare student attendance data
        student_data = []
        for record in student_attendance:
            student_data.append({
                'date': record.date.strftime('%Y-%m-%d'),
                'student_id': record.student.id,
                'student_first_name': record.student.first_name,
                'student_last_name': record.student.last_name,
                'status': record.status,
                'remarks': record.remarks
            })
        
        # Prepare teacher attendance data
        teacher_data = []
        for record in teacher_attendance:
            teacher_data.append({
                'date': record.date.strftime('%Y-%m-%d'),
                'teacher_id': record.teacher.id,
                'teacher_first_name': record.teacher.first_name,
                'teacher_last_name': record.teacher.last_name,
                'status': record.status,
                'remarks': record.remarks
            })
        
        # Calculate summary statistics
        student_present_count = student_attendance.filter(status='present').count()
        student_absent_count = student_attendance.filter(status='absent').count()
        teacher_present_count = teacher_attendance.filter(status='present').count()
        teacher_absent_count = teacher_attendance.filter(status='absent').count()
        
        # Prepare response data
        response_data = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'students': student_data,
            'teachers': teacher_data,
            'summary': {
                'student_present_count': student_present_count,
                'student_absent_count': student_absent_count,
                'teacher_present_count': teacher_present_count,
                'teacher_absent_count': teacher_absent_count
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

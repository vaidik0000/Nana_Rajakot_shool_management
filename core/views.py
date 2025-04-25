from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from students.models import Student
from school_teachers.models import Teacher
from subjects.models import Subject
from events.models import Event
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from datetime import datetime, timedelta
from .forms import SignUpForm, PasswordResetRequestForm, OTPVerificationForm, SetNewPasswordForm, ProfileForm
from .utils import send_otp_email, send_welcome_email
from django.http import JsonResponse
import json

# Store OTPs temporarily (in production, use Redis or database)
otp_storage = {}

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

@login_required(login_url='core:login')
def home(request):
    from subjects.models import Subject, StudentMark
    from attendance.models import Attendance, TeacherAttendance
    from events.models import Event
    from timetable.models import TimeTable
    from fees.models import FeeTransaction
    from django.db.models import Sum, Count, Avg, Q
    import datetime
    
    context = {
        # Other context data...
        'profile_picture': None,
    }

    if request.user.is_authenticated:
        if hasattr(request.user, 'profile') and request.user.profile.picture:
            context['profile_picture'] = request.user.profile.picture.url

    # Check if the logged-in user is a student
    is_student = hasattr(request, 'user_type') and request.user_type == 'student'
    # Check if the logged-in user is a teacher
    is_teacher = hasattr(request, 'user_type') and request.user_type == 'teacher'
    
    # If this is a student, show the student dashboard
    if is_student:
        student = request.student
        today = timezone.now().date()
        
        # Get student's subjects and their marks
        student_subjects = []
        if hasattr(student, 'marks'):
            subject_marks = student.marks.all().select_related('subject').order_by('subject__name')
            subject_data = {}
            
            for mark in subject_marks:
                if mark.subject_id not in subject_data:
                    subject_data[mark.subject_id] = {
                        'subject': mark.subject,
                        'marks': [],
                        'average': 0,
                    }
                subject_data[mark.subject_id]['marks'].append(mark)
            
            # Calculate averages and prepare data for display
            for subject_id, data in subject_data.items():
                if data['marks']:
                    total_percentage = sum(mark.percentage for mark in data['marks'])
                    data['average'] = total_percentage / len(data['marks'])
                student_subjects.append(data)
        
        # Get student's attendance
        attendance_data = {
            'present': 0,
            'absent': 0,
            'late': 0,
            'half_day': 0,
            'total': 0,
            'percentage': 0,
            'recent_records': [],
        }
        
        # Get attendance records
        attendance_records = Attendance.objects.filter(student=student).order_by('-date')
        recent_attendance = attendance_records[:5]  # Last 5 attendance records
        
        # Calculate attendance stats
        if attendance_records.exists():
            total_attendance = attendance_records.count()
            present_count = attendance_records.filter(status='present').count()
            
            attendance_data.update({
                'present': present_count,
                'absent': attendance_records.filter(status='absent').count(),
                'late': attendance_records.filter(status='late').count(),
                'half_day': attendance_records.filter(status='half_day').count(),
                'total': total_attendance,
                'percentage': (present_count / total_attendance * 100) if total_attendance > 0 else 0,
                'recent_records': recent_attendance,
            })
        
        # Get student's timetable for today
        weekday = today.strftime('%A').lower()
        timetable_entries = TimeTable.objects.filter(
            class_name=student.class_name,
            day=weekday
        ).select_related('subject', 'teacher').order_by('period')
        
        # Get upcoming and ongoing events
        upcoming_events = Event.objects.filter(
            start_date__gt=today
        ).order_by('start_date')[:5]
        
        ongoing_events = Event.objects.filter(
            start_date__lte=today,
            end_date__gte=today
        ).order_by('end_date')[:3]
        
        # Get fee payment info
        fee_data = {
            'total_paid': 0,
            'recent_transactions': [],
        }
        
        fee_transactions = FeeTransaction.objects.filter(student=student)
        if fee_transactions.exists():
            total_paid = fee_transactions.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
            fee_data.update({
                'total_paid': total_paid,
                'recent_transactions': fee_transactions.order_by('-created_at')[:3],
            })
        
        # Prepare the context for the student dashboard template
        context.update({
            'student': student,
            'subjects': student_subjects,
            'attendance': attendance_data,
            'timetable': timetable_entries,
            'upcoming_events': upcoming_events,
            'ongoing_events': ongoing_events,
            'fee_data': fee_data,
            'today': today,
        })
        
        return render(request, 'core/student_dashboard.html', context)
    
    # If this is a teacher, show the teacher dashboard
    elif is_teacher:
        teacher = request.teacher
        today = timezone.now().date()
        
        # Get teacher's timetable for today
        weekday = today.strftime('%A').lower()
        timetable_entries = TimeTable.objects.filter(
            teacher=teacher,
            day=weekday
        ).select_related('subject').order_by('period')
        
        # Get upcoming and ongoing events
        upcoming_events = Event.objects.filter(
            start_date__gt=today
        ).order_by('start_date')[:5]
        
        ongoing_events = Event.objects.filter(
            start_date__lte=today,
            end_date__gte=today
        ).order_by('end_date')[:3]
        
        # Get student marks assigned by this teacher
        student_marks = StudentMark.objects.filter(
            teacher=teacher
        ).select_related('student', 'subject').order_by('-created_at')[:10]
        
        # Get subjects taught by this teacher
        subjects_taught = Subject.objects.filter(teacher=teacher)
        
        # Get class-wise performance data
        class_performance = {}
        for mark in StudentMark.objects.filter(teacher=teacher).select_related('student'):
            class_name = mark.student.class_name
            if class_name not in class_performance:
                class_performance[class_name] = {
                    'total_marks': 0,
                    'count': 0,
                    'average': 0
                }
            class_performance[class_name]['total_marks'] += mark.percentage
            class_performance[class_name]['count'] += 1
        
        # Calculate averages
        for class_name in class_performance:
            if class_performance[class_name]['count'] > 0:
                class_performance[class_name]['average'] = round(
                    class_performance[class_name]['total_marks'] / class_performance[class_name]['count'], 
                    2
                )
        
        # Prepare the context for the teacher dashboard template
        context.update({
            'teacher': teacher,
            'timetable': timetable_entries,
            'upcoming_events': upcoming_events,
            'ongoing_events': ongoing_events,
            'student_marks': student_marks,
            'subjects_taught': subjects_taught,
            'class_performance': class_performance,
            'today': today,
        })
        
        return render(request, 'core/teacher_dashboard.html', context)
    
    # For non-student, non-teacher users, show the regular dashboard
    else:
        # Base context for all users
        context.update({
            'student_count': 0,
            'teacher_count': 0,
            'subject_count': 0,
            'total_revenue': 0,
            'recent_payments': [],
            'upcoming_events': [],
            'ongoing_events': [],
            'class_distribution': [],
        })
        
        # Only fetch detailed data if user is authenticated
        if request.user.is_authenticated:
            from students.models import Student
            from school_teachers.models import Teacher
            from subjects.models import Subject
            from fees.models import FeeTransaction
            
            # First get total count for percentage calculations
            student_count = Student.objects.filter(is_active=True).count()
            
            # Get class distribution with annotated counts
            class_distribution = Student.objects.filter(is_active=True).values('class_name').annotate(
                count=Count('id')
            ).order_by('class_name')
            
            # Calculate total revenue from completed fee transactions
            total_revenue = FeeTransaction.objects.filter(status='completed').aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            # Calculate percentage for each class
            total_students = student_count if student_count > 0 else 1
            
            # Get attendance data for chart
            attendance_chart_data = {
                'labels': [],
                'student_present': [],
                'student_absent': [],
                'teacher_present': [],
                'teacher_absent': [],
                'start_date': None,
                'end_date': None
            }
            
            if request.user.is_staff or request.user.is_superuser:
                # Get last 7 days
                today = timezone.now().date()
                start_date = today - timedelta(days=6)
                
                # Store the actual date range for reference
                attendance_chart_data['start_date'] = start_date.strftime('%Y-%m-%d')
                attendance_chart_data['end_date'] = today.strftime('%Y-%m-%d')
                
                # Create date labels (Apr 1, Apr 2, etc.)
                date_labels = []
                date_values = []
                
                for i in range(7):
                    date_obj = start_date + timedelta(days=i)
                    date_values.append(date_obj)
                    # Format as Apr 1, Apr 2, etc.
                    date_labels.append(date_obj.strftime('%b %d'))
                
                attendance_chart_data['labels'] = date_labels
                
                # Initialize counts for each day
                for _ in range(7):
                    attendance_chart_data['student_present'].append(0)
                    attendance_chart_data['student_absent'].append(0)
                    attendance_chart_data['teacher_present'].append(0)
                    attendance_chart_data['teacher_absent'].append(0)
                
                # Get student attendance data
                student_attendance = Attendance.objects.filter(
                    date__gte=start_date,
                    date__lte=today
                )
                
                # Get teacher attendance data
                teacher_attendance = TeacherAttendance.objects.filter(
                    date__gte=start_date,
                    date__lte=today
                )
                
                # Process student attendance
                for record in student_attendance:
                    # Find index of this date in our list
                    try:
                        idx = date_values.index(record.date)
                        if record.status == 'present':
                            attendance_chart_data['student_present'][idx] += 1
                        elif record.status == 'absent':
                            attendance_chart_data['student_absent'][idx] += 1
                    except ValueError:
                        # Date not in our range
                        pass
                
                # # Process teacher attendance
                # for record in teacher_attendance:
                #     # Find index of this date in our list
                #     try:
                #         idx = date_values.index(record.date)
                #         if record.status == 'present':
                #             attendance_chart_data['teacher_present'][idx] += 1
                #         elif record.status == 'absent':
                #             attendance_chart_data['teacher_absent'][idx] += 1
                #     except ValueError:
                #         # Date not in our range
                #         pass
                
                # Convert Python lists to JSON strings to avoid template issues
                attendance_chart_data['labels'] = json.dumps(attendance_chart_data['labels'])
                attendance_chart_data['student_present'] = json.dumps(attendance_chart_data['student_present'])
                attendance_chart_data['student_absent'] = json.dumps(attendance_chart_data['student_absent'])
                attendance_chart_data['teacher_present'] = json.dumps(attendance_chart_data['teacher_present'])
                attendance_chart_data['teacher_absent'] = json.dumps(attendance_chart_data['teacher_absent'])
            
            context.update({
                'student_count': student_count,
                'teacher_count': Teacher.objects.filter(is_active=True).count(),
                'subject_count': Subject.objects.filter(is_active=True).count(),
                'total_revenue': total_revenue,
                'class_distribution': class_distribution,
                'upcoming_events': Event.objects.filter(
                    start_date__gte=timezone.now().date()
                ).order_by('start_date')[:5],
                'ongoing_events': Event.objects.filter(
                    start_date__lte=timezone.now().date(),
                    end_date__gte=timezone.now().date()
                ).order_by('start_date')[:5],
                'attendance_chart_data': attendance_chart_data,
            })
        
        return render(request, 'core/home.html', context)

@login_required
def dashboard(request):
    # Get total students
    total_students = Student.objects.count()
    
    # Get fee structures
    fee_structures = []
    
    # Calculate total expected amount
    total_expected = 0
    
    # Get upcoming events
    today = timezone.now().date()
    upcoming_events = Event.objects.filter(start_date__gte=today).order_by('start_date')[:5]
    
    # Get ongoing events
    ongoing_events = Event.objects.filter(start_date__lte=today, end_date__gte=today).order_by('start_date')[:5]
    
    context = {
        'total_students': total_students,
        'fee_structures': fee_structures,
        'upcoming_events': upcoming_events,
        'ongoing_events': ongoing_events,
    }
    
    return render(request, 'core/dashboard.html', context)

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
        
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                # Don't save user yet, just get the form data
                user_data = {
                    'username': form.cleaned_data['username'],
                    'email': form.cleaned_data['email'],
                    'password1': form.cleaned_data['password1'],
                    'password2': form.cleaned_data['password2']
                }
                
                # Generate and send OTP
                otp = generate_otp()
                
                # Store user data and OTP
                otp_storage[user_data['email']] = {
                    'otp': otp,
                    'user_data': user_data,
                    'timestamp': datetime.now()
                }
                
                # Store email in session
                request.session['signup_email'] = user_data['email']
                
                # Send OTP email
                send_otp_email(user_data['email'], otp, purpose='registration')
                
                messages.success(request, 'Please check your email for the verification OTP.')
                return redirect('core:verify_signup_otp')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
                return redirect('core:signup')
        else:
            # Log form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = SignUpForm()
    
    return render(request, 'core/signup.html', {'form': form})

def verify_signup_otp(request):
    if request.user.is_authenticated:
        return redirect('core:home')
        
    if request.method == 'POST':
        otp = request.POST.get('otp')
        email = request.POST.get('email')
        
        if email in otp_storage:
            otp_data = otp_storage[email]
            
            # Check if OTP is expired (10 minutes)
            if datetime.now() - otp_data['timestamp'] > timedelta(minutes=10):
                del otp_storage[email]
                messages.error(request, 'OTP has expired. Please register again.')
                return redirect('core:signup')
            
            if otp == otp_data['otp']:
                try:
                    # Create user only after OTP verification
                    user_data = otp_data['user_data']
                    user = User.objects.create_user(
                        username=user_data['username'],
                        email=user_data['email'],
                        password=user_data['password1']
                    )
                    user.is_active = True
                    user.save()
                    
                    # Try to send welcome email, but don't stop the process if it fails
                    try:
                        send_welcome_email(user)
                    except Exception as e:
                        # Log the error but continue with registration
                        print(f"Failed to send welcome email: {str(e)}")
                    
                    del otp_storage[email]
                    messages.success(request, 'Email verified successfully! You can now login.')
                    return redirect('core:login')
                except Exception as e:
                    messages.error(request, f'Error creating user: {str(e)}')
                    return redirect('core:signup')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
        else:
            messages.error(request, 'OTP has expired. Please register again.')
            return redirect('core:signup')
    
    # Get the email from the session or redirect to signup
    email = request.session.get('signup_email')
    if not email:
        messages.error(request, 'Please complete the registration process.')
        return redirect('core:signup')
    
    return render(request, 'core/verify_signup_otp.html', {'email': email})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                login(request, user)
                return redirect('core:home')
            else:
                messages.error(request, 'Invalid username or password.')
        except User.DoesNotExist:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('core:login')

def password_reset_request(request):
    if request.user.is_authenticated:
        return redirect('core:home')
        
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                otp = generate_otp()
                # Store OTP with timestamp
                otp_storage[email] = {
                    'otp': otp,
                    'user_id': user.id,
                    'timestamp': datetime.now()
                }
                send_otp_email(email, otp, purpose='password_reset')
                messages.success(request, 'OTP has been sent to your email.')
                return redirect('core:verify_otp', email=email)
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email.')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'core/password_reset_request.html', {'form': form})

def verify_otp(request, email):
    if request.user.is_authenticated:
        return redirect('core:home')
        
    # Check if OTP exists and is not expired (10 minutes)
    if email not in otp_storage:
        messages.error(request, 'OTP has expired. Please request a new one.')
        return redirect('core:password_reset_request')
        
    otp_data = otp_storage[email]
    if datetime.now() - otp_data['timestamp'] > timedelta(minutes=10):
        del otp_storage[email]
        messages.error(request, 'OTP has expired. Please request a new one.')
        return redirect('core:password_reset_request')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            if otp == otp_data['otp']:
                request.session['reset_email'] = email
                return redirect('core:set_new_password')
            else:
                messages.error(request, 'Invalid OTP')
    else:
        form = OTPVerificationForm()
    
    return render(request, 'core/verify_otp.html', {'form': form, 'email': email})

def set_new_password(request):
    if request.user.is_authenticated:
        return redirect('core:home')
        
    if 'reset_email' not in request.session:
        return redirect('core:password_reset_request')
    
    email = request.session['reset_email']
    if email not in otp_storage:
        messages.error(request, 'Session expired. Please request a new OTP.')
        return redirect('core:password_reset_request')
    
    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            user_id = otp_storage[email]['user_id']
            user = User.objects.get(id=user_id)
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            
            # Clean up
            del otp_storage[email]
            del request.session['reset_email']
            
            messages.success(request, 'Password has been reset successfully. Please login with your new password.')
            return redirect('core:login')
    else:
        form = SetNewPasswordForm()
    
    return render(request, 'core/set_new_password.html', {'form': form})

@login_required
def user_permissions(request):
    """
    View for managing user permissions
    Only accessible to staff and superusers
    """
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('core:home')
    
    # Get all users
    from django.contrib.auth.models import User
    from students.models import Student
    from school_teachers.models import Teacher
    
    users = User.objects.all().order_by('-date_joined')
    
    # Associate users with their roles and permissions
    user_data = []
    for user in users:
        # Default data
        user_info = {
            'user': user,
            'role': 'Regular User',
            'is_student': False,
            'is_teacher': False,
            'student_info': None,
            'teacher_info': None,
            'profile_picture': None,
        }
        
        # Check if user is a student
        try:
            student = Student.objects.get(user=user)
            user_info['is_student'] = True
            user_info['role'] = 'Student'
            user_info['student_info'] = student
            if student.profile_picture:
                user_info['profile_picture'] = student.profile_picture.url
        except Student.DoesNotExist:
            pass
            
        # Check if user is a teacher
        try:
            teacher = Teacher.objects.get(user=user)
            user_info['is_teacher'] = True
            user_info['role'] = 'Teacher'
            user_info['teacher_info'] = teacher
            if not user_info['profile_picture'] and teacher.profile_picture:
                user_info['profile_picture'] = teacher.profile_picture.url
        except Teacher.DoesNotExist:
            pass
            
        # Check if user is staff/admin
        if user.is_staff or user.is_superuser:
            user_info['role'] = 'Administrator'
            
        user_data.append(user_info)
    
    # Prepare permissions matrix
    permissions = [
        {'code': 'attendance_manage', 'name': 'Manage Attendance'},
        {'code': 'library_manage', 'name': 'Manage Library'},
        {'code': 'event_manage', 'name': 'Manage Events'},
        {'code': 'student_manage', 'name': 'Manage Students'},
        {'code': 'teacher_manage', 'name': 'Manage Teachers'},
        {'code': 'subject_manage', 'name': 'Manage Subjects'},
        {'code': 'fee_manage', 'name': 'Manage Fees'},
        {'code': 'admin_access', 'name': 'Admin Access'},
    ]
    
    return render(request, 'core/user_permissions.html', {
        'user_data': user_data,
        'permissions': permissions,
    })

@login_required
def update_user_permissions(request, user_id):
    """
    View for updating user permissions
    Only accessible to staff and superusers
    """
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('core:home')
    
    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('core:user_permissions')
    
    from django.contrib.auth.models import User, Group
    from students.models import Student
    from school_teachers.models import Teacher
    
    try:
        user = User.objects.get(pk=user_id)
        
        # Get role selection
        new_role = request.POST.get('role')
        
        # Process role changes
        if new_role == 'student':
            # Create student profile if it doesn't exist
            if not hasattr(user, 'student'):
                # Since we can't create a full student profile here,
                # we'll just set up a placeholder and redirect to the 
                # full student creation form later
                messages.info(request, f"User {user.username} marked as student. Please complete their student profile.")
                
            # Remove teacher role if exists
            if hasattr(user, 'teacher'):
                teacher = user.teacher
                # Don't delete, just unlink
                teacher.user = None
                teacher.save()
                
            # Add to student group if it exists
            student_group, _ = Group.objects.get_or_create(name='Students')
            user.groups.add(student_group)
            
        elif new_role == 'teacher':
            # Create teacher profile if it doesn't exist
            if not hasattr(user, 'teacher'):
                # Since we can't create a full teacher profile here,
                # we'll just set up a placeholder and redirect to the
                # full teacher creation form later
                messages.info(request, f"User {user.username} marked as teacher. Please complete their teacher profile.")
                
            # Remove student role if exists
            if hasattr(user, 'student'):
                student = user.student
                # Don't delete, just unlink
                student.user = None
                student.save()
                
            # Add to teacher group if it exists
            teacher_group, _ = Group.objects.get_or_create(name='Teachers')
            user.groups.add(teacher_group)
            
        elif new_role == 'admin':
            # Make user staff
            user.is_staff = True
            user.save()
            
        elif new_role == 'regular':
            # Remove special permissions
            user.is_staff = False
            user.is_superuser = False
            
            # Unlink from student/teacher profiles
            if hasattr(user, 'student'):
                student = user.student
                student.user = None
                student.save()
                
            if hasattr(user, 'teacher'):
                teacher = user.teacher
                teacher.user = None
                teacher.save()
                
            # Remove from all groups
            user.groups.clear()
            
        # Process individual permissions
        # In a real implementation, this would update specific permissions
        # but for this demo we'll just show a message
        permissions_updated = []
        for key, value in request.POST.items():
            if key.startswith('perm_') and value == 'on':
                permission_name = key[5:]  # remove 'perm_' prefix
                permissions_updated.append(permission_name)
        
        if permissions_updated:
            messages.success(request, f"Updated permissions for {user.username}: {', '.join(permissions_updated)}")
        else:
            messages.success(request, f"Updated role for {user.username} to {new_role}")
        
        return redirect('core:user_permissions')
        
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('core:user_permissions')
    except Exception as e:
        messages.error(request, f"Error updating permissions: {str(e)}")
        return redirect('core:user_permissions')

@login_required
def attendance_data_api(request):
    """API endpoint to fetch attendance data for specified date ranges"""
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    from attendance.models import Attendance, TeacherAttendance
    from django.db.models import Q
    from datetime import datetime, timedelta
    
    # Get request parameters
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    try:
        if start_date_str and end_date_str:
            # Parse dates from request
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            # Default to last 7 days
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=6)
        
        # Initialize data structure
        attendance_data = {
            'labels': [],
            'student_present': [],
            'student_absent': [],
            'teacher_present': [],
            'teacher_absent': [],
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
        }
        
        # Create date labels and initialize count arrays
        date_values = []
        date_range = (end_date - start_date).days + 1
        
        for i in range(date_range):
            date_obj = start_date + timedelta(days=i)
            date_values.append(date_obj)
            attendance_data['labels'].append(date_obj.strftime('%b %d'))
            attendance_data['student_present'].append(0)
            attendance_data['student_absent'].append(0)
            attendance_data['teacher_present'].append(0)
            attendance_data['teacher_absent'].append(0)
        
        # Get attendance data
        student_attendance = Attendance.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        )
        
        teacher_attendance = TeacherAttendance.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Process student attendance
        for record in student_attendance:
            try:
                idx = date_values.index(record.date)
                if record.status == 'present':
                    attendance_data['student_present'][idx] += 1
                elif record.status == 'absent':
                    attendance_data['student_absent'][idx] += 1
            except ValueError:
                pass
        
        # Process teacher attendance
        for record in teacher_attendance:
            try:
                idx = date_values.index(record.date)
                if record.status == 'present':
                    attendance_data['teacher_present'][idx] += 1
                elif record.status == 'absent':
                    attendance_data['teacher_absent'][idx] += 1
            except ValueError:
                pass
        
        return JsonResponse(attendance_data)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def debug_permissions(request):
    """
    Debug view to show user permissions and context variables
    """
    from django.template import Context
    import pprint
    
    # Create a debug context with the current context
    context = {
        'debug_context': pprint.pformat(request.user.get_all_permissions()),
    }
    
    return render(request, 'debug_permissions.html', context)

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('core:home')
    else:
        form = ProfileForm(instance=request.user.profile)

    return render(request, 'core/update_profile.html', {'form': form})

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from students.models import Student
from school_teachers.models import Teacher
from attendance.models import Attendance, TeacherAttendance
from django.db import transaction
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Generate dummy attendance data for students and teachers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            default=30,
            type=int,
            help='Number of days to generate attendance data for (default: 30)'
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing attendance records in the date range'
        )

    def handle(self, *args, **options):
        days = options['days']
        overwrite = options['overwrite']
        
        # Get admin user for recording attendance
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.WARNING('No admin user found. Creating a default admin...'))
            admin_user = User.objects.create_superuser(
                username="admin", 
                email="admin@example.com", 
                password="adminpass123"
            )
        
        # Get students and teachers
        students = list(Student.objects.all())
        teachers = list(Teacher.objects.all())
        
        if not students:
            self.stdout.write(self.style.ERROR('No students found in the database. Please add students first.'))
            return
            
        if not teachers:
            self.stdout.write(self.style.ERROR('No teachers found in the database. Please add teachers first.'))
            return
        
        # Define date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # If overwrite option is selected, delete existing records in the date range
        if overwrite:
            deleted_student_count = Attendance.objects.filter(date__gte=start_date, date__lte=end_date).delete()[0]
            deleted_teacher_count = TeacherAttendance.objects.filter(date__gte=start_date, date__lte=end_date).delete()[0]
            self.stdout.write(self.style.WARNING(f'Deleted {deleted_student_count} student attendance records and {deleted_teacher_count} teacher attendance records'))
        
        # Generate student attendance
        self.generate_student_attendance(students, start_date, end_date, admin_user)
        
        # Generate teacher attendance
        self.generate_teacher_attendance(teachers, start_date, end_date, admin_user)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully generated attendance data from {start_date} to {end_date}'))
    
    def generate_student_attendance(self, students, start_date, end_date, admin_user):
        """Create random attendance records for students"""
        current_date = start_date
        delta = timedelta(days=1)
        status_choices = ['present', 'absent', 'late', 'half_day']
        status_weights = [0.8, 0.15, 0.03, 0.02]  # Probabilities for each status
        
        # Count for tracking progress
        total_days = (end_date - start_date).days + 1
        day_count = 0
        record_count = 0
        
        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                current_date += delta
                continue
                
            day_count += 1
            self.stdout.write(f'Generating student attendance for day {day_count}/{total_days}: {current_date.strftime("%Y-%m-%d")}')
            
            # Create batch of attendance records
            attendance_records = []
            for student in students:
                # Weighted random choice for status
                status = random.choices(status_choices, weights=status_weights)[0]
                
                try:
                    attendance = Attendance(
                        student=student,
                        date=current_date,
                        status=status,
                        remarks="" if status == 'present' else f"Student {status} on {current_date.strftime('%Y-%m-%d')}",
                        recorded_by=admin_user
                    )
                    attendance_records.append(attendance)
                    record_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating attendance for {student}: {e}'))
            
            # Bulk create attendance records for this date
            try:
                with transaction.atomic():
                    Attendance.objects.bulk_create(attendance_records, ignore_conflicts=True)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error bulk creating attendance records: {e}'))
                
            current_date += delta
        
        self.stdout.write(self.style.SUCCESS(f'Created {record_count} student attendance records across {day_count} days'))
    
    def generate_teacher_attendance(self, teachers, start_date, end_date, admin_user):
        """Create random attendance records for teachers"""
        current_date = start_date
        delta = timedelta(days=1)
        status_choices = ['present', 'absent', 'late', 'half_day']
        status_weights = [0.9, 0.07, 0.02, 0.01]  # Probabilities for each status (teachers more likely to be present)
        
        # Count for tracking progress
        total_days = (end_date - start_date).days + 1
        day_count = 0
        record_count = 0
        
        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                current_date += delta
                continue
                
            day_count += 1
            self.stdout.write(f'Generating teacher attendance for day {day_count}/{total_days}: {current_date.strftime("%Y-%m-%d")}')
            
            # Create batch of attendance records
            attendance_records = []
            for teacher in teachers:
                # Weighted random choice for status
                status = random.choices(status_choices, weights=status_weights)[0]
                
                try:
                    attendance = TeacherAttendance(
                        teacher=teacher,
                        date=current_date,
                        status=status,
                        remarks="" if status == 'present' else f"Teacher {status} on {current_date.strftime('%Y-%m-%d')}",
                        recorded_by=admin_user
                    )
                    attendance_records.append(attendance)
                    record_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating attendance for {teacher}: {e}'))
            
            # Bulk create attendance records for this date
            try:
                with transaction.atomic():
                    TeacherAttendance.objects.bulk_create(attendance_records, ignore_conflicts=True)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error bulk creating teacher attendance records: {e}'))
                
            current_date += delta
        
        self.stdout.write(self.style.SUCCESS(f'Created {record_count} teacher attendance records across {day_count} days')) 
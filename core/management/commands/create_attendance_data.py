from django.core.management.base import BaseCommand
from students.models import Student
from attendance.models import Attendance
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Create demo attendance data for testing'

    def handle(self, *args, **options):
        # Get all students
        students = Student.objects.all()
        
        if not students.exists():
            self.stdout.write(self.style.ERROR('No students found. Please create students first.'))
            return
            
        # Get a user for recorded_by (preferably admin)
        try:
            admin_user = User.objects.get(username='admin')
        except User.DoesNotExist:
            admin_user = User.objects.filter(is_staff=True).first()
            
        if not admin_user:
            self.stdout.write(self.style.ERROR('No admin user found. Using first available user.'))
            admin_user = User.objects.first()
            
        if not admin_user:
            self.stdout.write(self.style.ERROR('No users found. Please create a user first.'))
            return
            
        # Calculate dates for the past 30 days
        today = datetime.now().date()
        start_date = today - timedelta(days=30)
        
        # Status choices for random selection
        status_choices = ['present', 'absent', 'late', 'half_day']
        status_weights = [0.85, 0.1, 0.03, 0.02]  # Higher chance of present
        
        # Track created records
        attendance_count = 0
        skipped_count = 0
        
        # Generate attendance for each student for each day
        for student in students:
            self.stdout.write(f"Creating attendance for {student.first_name} {student.last_name}")
            
            current_date = start_date
            while current_date <= today:
                # Skip weekends (Saturday=5, Sunday=6)
                if current_date.weekday() >= 5:
                    current_date += timedelta(days=1)
                    continue
                    
                # Check if attendance already exists
                if Attendance.objects.filter(student=student, date=current_date).exists():
                    self.stdout.write(f"  Attendance already exists for {current_date}")
                    skipped_count += 1
                    current_date += timedelta(days=1)
                    continue
                
                # Randomly decide if absent on some days (10% chance)
                status = random.choices(status_choices, status_weights)[0]
                
                # Create attendance record
                attendance = Attendance(
                    student=student,
                    date=current_date,
                    status=status,
                    remarks=f"Auto-generated test data",
                    recorded_by=admin_user
                )
                attendance.save()
                attendance_count += 1
                
                current_date += timedelta(days=1)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {attendance_count} attendance records'))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'Skipped {skipped_count} existing records')) 
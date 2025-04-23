from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone
from attendance.models import Attendance
from students.models import Student
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Analyze attendance data'

    def handle(self, *args, **options):
        # Get dates for the past 30 days
        today = timezone.now().date()
        start_date = today - timedelta(days=30)
        
        # Get all classes from students
        class_names = Student.objects.values_list('class_name', flat=True).distinct()
        
        for class_name in class_names:
            self.stdout.write(f"Analyzing attendance for class {class_name}...")
            
            # Get students in this class
            students_in_class = Student.objects.filter(class_name=class_name).count()
            if students_in_class == 0:
                self.stdout.write(self.style.WARNING(f"No students found in class {class_name}, skipping"))
                continue
                
            # Process each day
            current_date = start_date
            while current_date <= today:
                # Skip weekends
                if current_date.weekday() >= 5:
                    current_date += timedelta(days=1)
                    continue
                
                # Get attendance counts for this class and date
                attendance_data = Attendance.objects.filter(
                    student__class_name=class_name,
                    date=current_date
                ).values('status').annotate(count=Count('status'))
                
                # If no attendance data for this day, skip
                if not attendance_data:
                    self.stdout.write(f"  No attendance data for {current_date}, skipping")
                    current_date += timedelta(days=1)
                    continue
                
                # Extract counts by status
                present_count = 0
                absent_count = 0
                late_count = 0
                half_day_count = 0
                
                for item in attendance_data:
                    if item['status'] == 'present':
                        present_count = item['count']
                    elif item['status'] == 'absent':
                        absent_count = item['count']
                    elif item['status'] == 'late':
                        late_count = item['count']
                    elif item['status'] == 'half_day':
                        half_day_count = item['count']
                
                # Print analysis
                total_count = present_count + absent_count + late_count + half_day_count
                present_percentage = round((present_count / total_count) * 100, 2) if total_count > 0 else 0
                
                self.stdout.write(f"  Analysis for {current_date}:")
                self.stdout.write(f"    Total students: {total_count}")
                self.stdout.write(f"    Present: {present_count} ({present_percentage}%)")
                self.stdout.write(f"    Absent: {absent_count}")
                self.stdout.write(f"    Late: {late_count}")
                self.stdout.write(f"    Half day: {half_day_count}")
                
                current_date += timedelta(days=1)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully analyzed attendance data')) 
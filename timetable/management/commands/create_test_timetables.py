from django.core.management.base import BaseCommand
from timetable.models import TimeTable
from school_teachers.models import Teacher
from subjects.models import Subject
from django.utils import timezone
import random
from datetime import time

class Command(BaseCommand):
    help = 'Creates test timetable entries for all classes, days, and periods'
    
    def handle(self, *args, **options):
        # First clear existing timetable entries
        TimeTable.objects.all().delete()
        self.stdout.write("Deleted existing timetable entries")
        
        # Get available teachers and subjects
        teachers = Teacher.objects.filter(is_active=True)
        subjects = Subject.objects.filter(is_active=True)
        
        if not teachers:
            self.stdout.write(self.style.ERROR("No active teachers found. Please create at least one teacher."))
            return
            
        if not subjects:
            self.stdout.write(self.style.ERROR("No active subjects found. Please create at least one subject."))
            return
            
        self.stdout.write(f"Found {teachers.count()} teachers and {subjects.count()} subjects")
        
        # Define classes, days and periods
        classes = ['1', '2', '3', '4', '5']
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        periods = ['1', '2', '3', '4', '5', '6']
        
        # Create timetable entries
        timetable_entries = []
        count = 0
        
        for class_name in classes:
            for day in days:
                for period in periods:
                    teacher = random.choice(teachers)
                    subject = random.choice(subjects)
                    
                    # Calculate period times
                    hour = 8 + int(period)
                    start_time = time(hour, 0)
                    end_time = time(hour, 45)
                    
                    # Create a timetable entry
                    try:
                        timetable = TimeTable(
                            class_name=class_name,
                            day=day,
                            period=period,
                            subject=subject,
                            teacher=teacher,
                            start_time=start_time,
                            end_time=end_time,
                            room_number=f'R-{class_name}{period}'
                        )
                        timetable_entries.append(timetable)
                        count += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error creating timetable for Class {class_name}, {day}, Period {period}: {str(e)}"))
        
        # Bulk create the timetable entries
        TimeTable.objects.bulk_create(timetable_entries)
        
        self.stdout.write(self.style.SUCCESS(f"Successfully created {count} timetable entries")) 
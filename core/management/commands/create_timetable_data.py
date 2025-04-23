from django.core.management.base import BaseCommand
from timetable.models import TimeTable
from school_teachers.models import Teacher
from subjects.models import Subject
from django.utils import timezone
import random
from datetime import time

class Command(BaseCommand):
    help = 'Creates realistic timetable entries with proper teacher-subject relationships'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing timetable entries before creating new ones',
        )
    
    def handle(self, *args, **options):
        clear_existing = options['clear']
        
        # Clear existing entries if requested
        if clear_existing:
            timetable_count = TimeTable.objects.count()
            TimeTable.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"Cleared {timetable_count} existing timetable entries"))
        
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
        
        # Define classes, days, and periods
        classes = ['1', '2', '3', '4', '5']
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        periods = ['1', '2', '3', '4', '5', '6', '7', '8']
        
        # Define period times (8:00 AM to 3:45 PM)
        period_times = {
            '1': (time(8, 0), time(8, 45)),
            '2': (time(8, 50), time(9, 35)),
            '3': (time(9, 40), time(10, 25)),
            '4': (time(10, 40), time(11, 25)),  # Small break after period 3
            '5': (time(11, 30), time(12, 15)),
            '6': (time(13, 0), time(13, 45)),   # Lunch break
            '7': (time(13, 50), time(14, 35)),
            '8': (time(14, 40), time(15, 25)),
        }
        
        # Assign subjects to teachers - each teacher gets 1-3 subjects
        teacher_subjects = {}
        for teacher in teachers:
            # Choose a random number of subjects for this teacher (1-3)
            num_subjects = min(random.randint(1, 3), subjects.count())
            assigned_subjects = random.sample(list(subjects), num_subjects)
            teacher_subjects[teacher.id] = assigned_subjects
        
        # Track teacher availability to avoid scheduling conflicts
        teacher_schedule = {teacher.id: {day: set() for day in days} for teacher in teachers}
        
        # Create timetable entries
        timetable_entries = []
        created_count = 0
        
        for class_name in classes:
            # For each class, create a balanced subject distribution
            class_subjects = {}
            for day in days:
                for period in periods:
                    # Check if there's already an entry for this class, day, and period
                    if TimeTable.objects.filter(class_name=class_name, day=day, period=period).exists():
                        self.stdout.write(f"Entry for Class {class_name}, {day}, Period {period} already exists. Skipping.")
                        continue
                    
                    # Find a teacher who teaches an appropriate subject and is available
                    available_teachers = []
                    for teacher_id, assigned_subjects in teacher_subjects.items():
                        # Check if teacher already has a class this period
                        if period in teacher_schedule[teacher_id][day]:
                            continue
                        
                        # Add this teacher to available options
                        available_teachers.append((teacher_id, assigned_subjects))
                    
                    if not available_teachers:
                        self.stdout.write(self.style.WARNING(
                            f"No available teachers for Class {class_name}, {day}, Period {period}. Skipping."
                        ))
                        continue
                    
                    # Choose random teacher and one of their subjects
                    teacher_id, possible_subjects = random.choice(available_teachers)
                    subject = random.choice(possible_subjects)
                    
                    # Mark teacher as unavailable for this period
                    teacher_schedule[teacher_id][day].add(period)
                    
                    # Get period times
                    start_time, end_time = period_times[period]
                    
                    # Generate room number: Combine class and subject code
                    room_number = f"{class_name}{subject.code[:3].upper()}"
                    
                    # Create timetable entry
                    try:
                        teacher = Teacher.objects.get(id=teacher_id)
                        timetable = TimeTable(
                            class_name=class_name,
                            day=day,
                            period=period,
                            subject=subject,
                            teacher=teacher,
                            start_time=start_time,
                            end_time=end_time,
                            room_number=room_number
                        )
                        timetable_entries.append(timetable)
                        created_count += 1
                        
                        # For debugging/feedback
                        if created_count % 50 == 0:
                            self.stdout.write(f"Created {created_count} timetable entries so far...")
                            
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(
                            f"Error creating timetable for Class {class_name}, {day}, Period {period}: {str(e)}"
                        ))
        
        # Bulk create the timetable entries
        if timetable_entries:
            TimeTable.objects.bulk_create(timetable_entries)
            self.stdout.write(self.style.SUCCESS(f"Successfully created {created_count} timetable entries"))
        else:
            self.stdout.write(self.style.WARNING("No timetable entries were created")) 
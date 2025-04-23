from django.core.management.base import BaseCommand
from django.utils import timezone
from school_teachers.models import Teacher
from subjects.models import Subject
from timetable.models import TimeTable
from datetime import time

class Command(BaseCommand):
    help = 'Setup timetable entries for teacher Ramesh'
    
    def handle(self, *args, **kwargs):
        try:
            # Find Ramesh by email
            teacher = Teacher.objects.get(email='ramesh@gmail.com')
            self.stdout.write(self.style.SUCCESS(f"Found teacher: {teacher.first_name} {teacher.last_name}"))
            
            # Create or get subjects for Ramesh
            react_js, created = Subject.objects.get_or_create(
                code='REACT101',
                defaults={
                    'name': 'React JS',
                    'description': 'Modern frontend development with React',
                    'teacher': teacher,
                    'credits': 4,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created subject: {react_js.name}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Found existing subject: {react_js.name}"))
                
            hubspot, created = Subject.objects.get_or_create(
                code='HUB101',
                defaults={
                    'name': 'Hubspot CRM',
                    'description': 'CRM systems with Hubspot',
                    'teacher': teacher,
                    'credits': 3,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created subject: {hubspot.name}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Found existing subject: {hubspot.name}"))
            
            # Define timetable entries with specific periods to avoid conflicts
            timetable_entries = [
                # React JS classes
                {
                    'class_name': '1', 
                    'day': 'monday', 
                    'period': '1', 
                    'subject': react_js,
                    'start_time': time(9, 0),
                    'end_time': time(10, 0),
                    'room_number': 'CS-101'
                },
                {
                    'class_name': '2', 
                    'day': 'tuesday', 
                    'period': '2', 
                    'subject': react_js,
                    'start_time': time(10, 0),
                    'end_time': time(11, 0),
                    'room_number': 'CS-202'
                },
                {
                    'class_name': '3', 
                    'day': 'wednesday', 
                    'period': '3', 
                    'subject': react_js,
                    'start_time': time(11, 0),
                    'end_time': time(12, 0),
                    'room_number': 'CS-303'
                },
                
                # Hubspot classes
                {
                    'class_name': '1', 
                    'day': 'thursday', 
                    'period': '5', 
                    'subject': hubspot,
                    'start_time': time(14, 0),
                    'end_time': time(15, 0),
                    'room_number': 'CS-105'
                },
                {
                    'class_name': '2', 
                    'day': 'friday', 
                    'period': '6', 
                    'subject': hubspot,
                    'start_time': time(15, 0),
                    'end_time': time(16, 0),
                    'room_number': 'CS-206'
                },
                {
                    'class_name': '3', 
                    'day': 'monday', 
                    'period': '4', 
                    'subject': hubspot,
                    'start_time': time(13, 0),
                    'end_time': time(14, 0),
                    'room_number': 'CS-304'
                },
            ]
            
            # Add entries to timetable using update_or_create to avoid conflicts
            entries_created = 0
            entries_updated = 0
            
            for entry in timetable_entries:
                obj, created = TimeTable.objects.update_or_create(
                    class_name=entry['class_name'],
                    day=entry['day'],
                    period=entry['period'],
                    defaults={
                        'subject': entry['subject'],
                        'teacher': teacher,
                        'start_time': entry['start_time'],
                        'end_time': entry['end_time'],
                        'room_number': entry['room_number']
                    }
                )
                
                if created:
                    entries_created += 1
                else:
                    entries_updated += 1
            
            self.stdout.write(self.style.SUCCESS(f"Created {entries_created} new timetable entries"))
            self.stdout.write(self.style.SUCCESS(f"Updated {entries_updated} existing timetable entries"))
            
        except Teacher.DoesNotExist:
            self.stdout.write(self.style.ERROR("Teacher with email 'ramesh@gmail.com' not found. Please create the teacher first."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error setting up timetable: {str(e)}")) 
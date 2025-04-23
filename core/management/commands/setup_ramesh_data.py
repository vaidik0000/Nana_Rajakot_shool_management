from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from school_teachers.models import Teacher
from subjects.models import Subject, StudentMark
from timetable.models import TimeTable
from students.models import Student, StudentMarks
from django.contrib.auth.models import User
from datetime import timedelta, time
import random

class Command(BaseCommand):
    help = 'Setup sample data for teacher Ramesh, including subjects, timetable, and student marks'
    
    def handle(self, *args, **kwargs):
        # Find or create Ramesh
        try:
            teacher = Teacher.objects.get(email='ramesh@gmail.com')
            self.stdout.write(self.style.SUCCESS(f'Found teacher: {teacher.name}'))
        except Teacher.DoesNotExist:
            teacher = Teacher.objects.create(
                name='Ramesh Chaudhary',
                email='ramesh@gmail.com',
                phone_number='9876543210',
                address='123 Teacher St',
                qualification='PhD in Computer Science',
                date_of_birth='1980-01-01',
                date_of_joining='2010-01-01',
                salary=75000,
            )
            self.stdout.write(self.style.SUCCESS(f'Created teacher: {teacher.name}'))

        # Create subjects for Ramesh if they don't exist
        react_subject, react_created = Subject.objects.update_or_create(
            code='REACT101',
            defaults={
                'name': 'React JS',
                'description': 'Frontend development with React JS',
                'teacher': teacher,
                'credits': 4,
                'is_active': True
            }
        )
        
        if react_created:
            self.stdout.write(self.style.SUCCESS(f'Created subject: {react_subject.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Found subject: {react_subject.name}'))

        hubspot_subject, hubspot_created = Subject.objects.update_or_create(
            code='HUB101',
            defaults={
                'name': 'Hubspot CRM',
                'description': 'CRM systems with Hubspot',
                'teacher': teacher,
                'credits': 3,
                'is_active': True
            }
        )
        
        if hubspot_created:
            self.stdout.write(self.style.SUCCESS(f'Created subject: {hubspot_subject.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Found subject: {hubspot_subject.name}'))

        # Create timetable entries - use update_or_create to avoid conflicts
        timetable_created = 0
        
        # Define class-day-period combinations to use
        timetable_entries = [
            # Class 1 - React JS
            {'class_name': '1', 'day': 'monday', 'period': '1', 'subject': react_subject, 'start_hour': 9},
            {'class_name': '1', 'day': 'wednesday', 'period': '2', 'subject': react_subject, 'start_hour': 10},
            
            # Class 2 - React JS
            {'class_name': '2', 'day': 'tuesday', 'period': '3', 'subject': react_subject, 'start_hour': 11},
            {'class_name': '2', 'day': 'thursday', 'period': '4', 'subject': react_subject, 'start_hour': 12},
            
            # Class 1 - Hubspot
            {'class_name': '1', 'day': 'friday', 'period': '5', 'subject': hubspot_subject, 'start_hour': 13},
            {'class_name': '1', 'day': 'wednesday', 'period': '6', 'subject': hubspot_subject, 'start_hour': 14},
            
            # Class 3 - Hubspot
            {'class_name': '3', 'day': 'monday', 'period': '7', 'subject': hubspot_subject, 'start_hour': 15},
            {'class_name': '3', 'day': 'thursday', 'period': '8', 'subject': hubspot_subject, 'start_hour': 16},
        ]
        
        for entry in timetable_entries:
            start_time = time(entry['start_hour'], 0)
            end_time = time(entry['start_hour'] + 1, 0)
            room_number = f"CS-{entry['class_name']}{entry['period']}"
            
            _, created = TimeTable.objects.update_or_create(
                class_name=entry['class_name'],
                day=entry['day'],
                period=entry['period'],
                defaults={
                    'subject': entry['subject'],
                    'teacher': teacher,
                    'start_time': start_time,
                    'end_time': end_time,
                    'room_number': room_number
                }
            )
            
            if created:
                timetable_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {timetable_created} new timetable entries'))

        # Create marks for students for the new subjects
        students = list(Student.objects.all()[:20])  # Get up to 20 students
        if not students:
            self.stdout.write(self.style.ERROR('No students found. Please create students first.'))
            return
            
        # Clear existing marks for these specific subjects to avoid duplicates
        StudentMarks.objects.filter(subject__in=[react_subject, hubspot_subject]).delete()
        
        # Create new marks
        marks_created = 0
        for student in students:
            # Add marks for React
            marks = random.randint(65, 98)
            StudentMarks.objects.create(
                student=student,
                subject=react_subject,
                marks=marks,
                date=timezone.now()
            )
            marks_created += 1
            
            # Add marks for Hubspot
            marks = random.randint(65, 98)
            StudentMarks.objects.create(
                student=student,
                subject=hubspot_subject,
                marks=marks,
                date=timezone.now()
            )
            marks_created += 1
            
        subjects = []
        for subject_data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                code=subject_data['code'],
                defaults=subject_data
            )
            subjects.append(subject)
            status = "Created" if created else "Found existing"
            self.stdout.write(self.style.SUCCESS(f"{status} subject: {subject.name}"))
        
        # Create timetable entries for React and Hubspot
        today = timezone.now().date()
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        class_names = ['1', '2', '3']  # Classes 1, 2, and 3
        
        # Clear existing timetable entries for these subjects by this teacher
        TimeTable.objects.filter(teacher=teacher, subject__in=subjects).delete()
        self.stdout.write(self.style.SUCCESS("Cleared existing timetable entries"))
        
        # Create new timetable entries
        periods = {
            '1': {'start': time(9, 0), 'end': time(10, 0)},
            '2': {'start': time(10, 0), 'end': time(11, 0)},
            '3': {'start': time(11, 15), 'end': time(12, 15)},
            '4': {'start': time(12, 15), 'end': time(13, 15)},
            '5': {'start': time(14, 0), 'end': time(15, 0)},
            '6': {'start': time(15, 0), 'end': time(16, 0)},
        }
        
        # Keep track of used periods to avoid conflicts
        used_periods = {}  # {(class_name, day): [periods]}
        
        timetable_count = 0
        # Assign React to mornings, Hubspot to afternoons
        for day in weekdays:
            for class_name in class_names:
                key = (class_name, day)
                if key not in used_periods:
                    used_periods[key] = []
                
                # React class in the morning
                morning_periods = [p for p in ['1', '2', '3'] if p not in used_periods[key]]
                if morning_periods:
                    react_period = random.choice(morning_periods)
                    used_periods[key].append(react_period)
                    
                    try:
                        TimeTable.objects.create(
                            class_name=class_name,
                            day=day,
                            period=react_period,
                            subject=subjects[0],  # React
                            teacher=teacher,
                            start_time=periods[react_period]['start'],
                            end_time=periods[react_period]['end'],
                            room_number=f'CS-{class_name}0{react_period}'
                        )
                        timetable_count += 1
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Could not create timetable for React: {str(e)}"))
                
                # Hubspot class in the afternoon
                afternoon_periods = [p for p in ['4', '5', '6'] if p not in used_periods[key]]
                if afternoon_periods:
                    hubspot_period = random.choice(afternoon_periods)
                    used_periods[key].append(hubspot_period)
                    
                    try:
                        TimeTable.objects.create(
                            class_name=class_name,
                            day=day,
                            period=hubspot_period,
                            subject=subjects[1],  # Hubspot
                            teacher=teacher,
                            start_time=periods[hubspot_period]['start'],
                            end_time=periods[hubspot_period]['end'],
                            room_number=f'CS-{class_name}0{hubspot_period}'
                        )
                        timetable_count += 1
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Could not create timetable for Hubspot: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(f"Created {timetable_count} timetable entries"))
        
        # Create student marks for both subjects
        # First, get all students
        students = Student.objects.all()
        if not students:
            self.stdout.write(self.style.WARNING("No students found in the database. Cannot create marks."))
            return
            
        # Delete existing marks for these subjects to avoid duplicates
        StudentMark.objects.filter(subject__in=subjects, teacher=teacher).delete()
        
        # Create marks for both subjects
        marks_created = 0
        for student in students[:25]:  # Take up to 25 students
            for subject in subjects:
                # Create a mark from last week
                last_week = today - timedelta(days=7)
                marks_obtained = random.randint(70, 98)
                total_marks = 100
                
                StudentMark.objects.create(
                    student=student,
                    subject=subject,
                    teacher=teacher,
                    marks_obtained=marks_obtained,
                    total_marks=total_marks,
                    date=last_week,
                    remarks=f"Good performance in {subject.name}"
                )
                marks_created += 1
                
                # Create another mark from yesterday for some students
                if random.choice([True, False]):
                    yesterday = today - timedelta(days=1)
                    marks_obtained = random.randint(75, 100)
                    
                    StudentMark.objects.create(
                        student=student,
                        subject=subject,
                        teacher=teacher,
                        marks_obtained=marks_obtained,
                        total_marks=total_marks,
                        date=yesterday,
                        remarks=f"Recent assessment in {subject.name}"
                    )
                    marks_created += 1
        
        self.stdout.write(self.style.SUCCESS(f"Created {marks_created} student marks across both subjects")) 
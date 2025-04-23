from django.core.management.base import BaseCommand
from django.utils import timezone
from school_teachers.models import Teacher
from subjects.models import Subject
from datetime import date
import random

class Command(BaseCommand):
    help = 'Creates test teachers and subjects for testing'
    
    def handle(self, *args, **options):
        self.stdout.write("Creating test teachers and subjects...")
        
        # Create test teachers
        teachers = [
            {
                'first_name': 'John',
                'last_name': 'Doe',
                'employee_id': 'TECH001',
                'gender': 'M',
                'date_of_birth': date(1980, 1, 15),
                'email': 'john.doe@school.com',
                'phone_number': '9876543210',
                'address': '123 Teacher Street, City',
                'qualification': 'PhD in Mathematics',
                'specialization': 'Mathematics',
                'joining_date': date(2010, 6, 1),
            },
            {
                'first_name': 'Jane',
                'last_name': 'Smith',
                'employee_id': 'TECH002',
                'gender': 'F',
                'date_of_birth': date(1985, 5, 20),
                'email': 'jane.smith@school.com',
                'phone_number': '9876543211',
                'address': '456 Teacher Avenue, City',
                'qualification': 'Masters in English Literature',
                'specialization': 'English',
                'joining_date': date(2012, 7, 15),
            },
            {
                'first_name': 'Robert',
                'last_name': 'Johnson',
                'employee_id': 'TECH003',
                'gender': 'M',
                'date_of_birth': date(1978, 9, 10),
                'email': 'robert.johnson@school.com',
                'phone_number': '9876543212',
                'address': '789 Professor Lane, City',
                'qualification': 'MSc in Physics',
                'specialization': 'Science',
                'joining_date': date(2009, 4, 1),
            },
            {
                'first_name': 'Lisa',
                'last_name': 'Brown',
                'employee_id': 'TECH004',
                'gender': 'F',
                'date_of_birth': date(1982, 11, 25),
                'email': 'lisa.brown@school.com',
                'phone_number': '9876543213',
                'address': '321 Educator Road, City',
                'qualification': 'PhD in History',
                'specialization': 'Social Studies',
                'joining_date': date(2014, 8, 1),
            },
        ]
        
        created_teachers = []
        for teacher_data in teachers:
            # Check if teacher already exists
            if not Teacher.objects.filter(email=teacher_data['email']).exists():
                teacher = Teacher.objects.create(**teacher_data)
                created_teachers.append(teacher)
                self.stdout.write(self.style.SUCCESS(f"Created teacher: {teacher.first_name} {teacher.last_name}"))
            else:
                teacher = Teacher.objects.get(email=teacher_data['email'])
                created_teachers.append(teacher)
                self.stdout.write(f"Teacher {teacher.first_name} {teacher.last_name} already exists")
        
        # Create test subjects
        subjects = [
            {
                'name': 'Mathematics',
                'code': 'MATH101',
                'description': 'Basic mathematics including algebra, geometry, and arithmetic',
                'credits': 5,
            },
            {
                'name': 'English',
                'code': 'ENG101',
                'description': 'English language and literature',
                'credits': 4,
            },
            {
                'name': 'Science',
                'code': 'SCI101',
                'description': 'Basic science concepts including physics, chemistry, and biology',
                'credits': 5,
            },
            {
                'name': 'Social Studies',
                'code': 'SOC101',
                'description': 'History, geography, and civics',
                'credits': 4,
            },
            {
                'name': 'Computer Science',
                'code': 'CS101',
                'description': 'Introduction to computer science and programming',
                'credits': 3,
            },
        ]
        
        for subject_data in subjects:
            # Assign a teacher
            teacher = random.choice(created_teachers)
            
            # Check if subject already exists
            if not Subject.objects.filter(code=subject_data['code']).exists():
                subject = Subject.objects.create(
                    teacher=teacher,
                    **subject_data
                )
                self.stdout.write(self.style.SUCCESS(f"Created subject: {subject.name} (Teacher: {teacher.first_name} {teacher.last_name})"))
            else:
                subject = Subject.objects.get(code=subject_data['code'])
                subject.teacher = teacher
                subject.save()
                self.stdout.write(f"Subject {subject.name} already exists, updated teacher to {teacher.first_name} {teacher.last_name}")
        
        self.stdout.write(self.style.SUCCESS("Successfully created test data")) 
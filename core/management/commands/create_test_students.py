from django.core.management.base import BaseCommand
from django.utils import timezone
from students.models import Student
from datetime import date
import random

class Command(BaseCommand):
    help = 'Creates test students for testing the Razorpay fee payment system'
    
    def handle(self, *args, **options):
        self.stdout.write("Creating test students...")
        
        # Create test students
        students = [
            {
                'first_name': 'Alex',
                'last_name': 'Johnson',
                'roll_number': 'STU001',
                'class_name': '1',
                'gender': 'M',
                'date_of_birth': date(2015, 3, 15),
                'address': '101 Student Lane, City',
                'phone_number': '9876543220',
                'email': 'alex.johnson@student.com',
                'parent_name': 'Michael Johnson',
                'parent_phone': '9876543221',
                'parent_email': 'michael.johnson@parent.com',
            },
            {
                'first_name': 'Emily',
                'last_name': 'Smith',
                'roll_number': 'STU002',
                'class_name': '2',
                'gender': 'F',
                'date_of_birth': date(2014, 7, 25),
                'address': '202 Student Avenue, City',
                'phone_number': '9876543222',
                'email': 'emily.smith@student.com',
                'parent_name': 'Sarah Smith',
                'parent_phone': '9876543223',
                'parent_email': 'sarah.smith@parent.com',
            },
            {
                'first_name': 'Ryan',
                'last_name': 'Williams',
                'roll_number': 'STU003',
                'class_name': '3',
                'gender': 'M',
                'date_of_birth': date(2013, 2, 8),
                'address': '303 Pupil Road, City',
                'phone_number': '9876543224',
                'email': 'ryan.williams@student.com',
                'parent_name': 'Robert Williams',
                'parent_phone': '9876543225',
                'parent_email': 'robert.williams@parent.com',
            },
            {
                'first_name': 'Sophia',
                'last_name': 'Brown',
                'roll_number': 'STU004',
                'class_name': '4',
                'gender': 'F',
                'date_of_birth': date(2012, 9, 18),
                'address': '404 Learner Street, City',
                'phone_number': '9876543226',
                'email': 'sophia.brown@student.com',
                'parent_name': 'Elizabeth Brown',
                'parent_phone': '9876543227',
                'parent_email': 'elizabeth.brown@parent.com',
            },
            {
                'first_name': 'Daniel',
                'last_name': 'Miller',
                'roll_number': 'STU005',
                'class_name': '5',
                'gender': 'M',
                'date_of_birth': date(2011, 5, 12),
                'address': '505 Scholar Boulevard, City',
                'phone_number': '9876543228',
                'email': 'daniel.miller@student.com',
                'parent_name': 'James Miller',
                'parent_phone': '9876543229',
                'parent_email': 'james.miller@parent.com',
            },
        ]
        
        for student_data in students:
            # Check if student already exists
            if not Student.objects.filter(roll_number=student_data['roll_number']).exists():
                student = Student.objects.create(**student_data)
                self.stdout.write(self.style.SUCCESS(f"Created student: {student.first_name} {student.last_name} (Class {student.class_name})"))
            else:
                student = Student.objects.get(roll_number=student_data['roll_number'])
                self.stdout.write(f"Student {student.first_name} {student.last_name} already exists")
        
        self.stdout.write(self.style.SUCCESS("Successfully created test students")) 
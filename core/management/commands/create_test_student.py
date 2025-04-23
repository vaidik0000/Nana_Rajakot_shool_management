from django.core.management.base import BaseCommand
from django.utils import timezone
from students.models import Student
from datetime import date
import random

class Command(BaseCommand):
    help = 'Creates a test student and prints their login credentials'
    
    def handle(self, *args, **options):
        # Check if test student already exists
        email = "test.student@school.com"
        roll_number = "TEST123"
        
        # Delete if already exists
        Student.objects.filter(email=email).delete()
        
        # Create new test student
        student = Student(
            first_name="Test",
            last_name="Student",
            roll_number=roll_number,
            class_name="1",  # Class 1
            gender="M",
            date_of_birth=date(2010, 1, 1),
            address="123 Test Address",
            phone_number="1234567890",
            email=email,
            parent_name="Parent Name",
            parent_phone="0987654321",
            parent_email="parent@email.com",
            is_active=True
        )
        student.save()
        
        # The save method will create a user with username as email
        # and password as "student_" + roll_number
        
        self.stdout.write(self.style.SUCCESS(f"Test student created successfully!"))
        self.stdout.write("\nLogin credentials:")
        self.stdout.write(f"Username: {email}")
        self.stdout.write(f"Password: student_{roll_number}")
        
        # Verify if user was created properly
        if student.user:
            self.stdout.write(self.style.SUCCESS("User account created successfully!"))
        else:
            self.stdout.write(self.style.ERROR("User account was NOT created. Please check the student model save method.")) 
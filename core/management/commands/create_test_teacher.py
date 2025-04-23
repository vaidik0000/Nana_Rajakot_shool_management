from django.core.management.base import BaseCommand
from django.utils import timezone
from school_teachers.models import Teacher
from datetime import date
import random

class Command(BaseCommand):
    help = 'Creates a test teacher and prints their login credentials'
    
    def handle(self, *args, **options):
        # Check if test teacher already exists
        email = "test.teacher@school.com"
        employee_id = "EMP123"
        
        # Delete if already exists
        Teacher.objects.filter(email=email).delete()
        
        # Create new test teacher
        teacher = Teacher(
            first_name="Test",
            last_name="Teacher",
            employee_id=employee_id,
            gender="M",
            date_of_birth=date(1980, 1, 1),
            email=email,
            phone_number="9876543210",
            address="456 Test Teacher Address",
            qualification="Ph.D Education",
            specialization="Mathematics",
            joining_date=date(2020, 1, 1),
            is_active=True
        )
        teacher.save()
        
        # The save method will create a user with username as email
        # and a default password 'secure123'
        
        self.stdout.write(self.style.SUCCESS(f"Test teacher created successfully!"))
        self.stdout.write("\nLogin credentials:")
        self.stdout.write(f"Username: {email}")
        self.stdout.write(f"Password: secure123")
        
        # Verify if user was created properly
        if teacher.user:
            self.stdout.write(self.style.SUCCESS("User account created successfully!"))
        else:
            self.stdout.write(self.style.ERROR("User account was NOT created. Please check the teacher model save method.")) 
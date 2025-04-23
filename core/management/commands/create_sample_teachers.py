from django.core.management.base import BaseCommand
from django.utils import timezone
from school_teachers.models import Teacher
from datetime import date
import random

class Command(BaseCommand):
    help = 'Creates sample teachers for testing'
    
    def handle(self, *args, **options):
        # Sample data
        first_names = [
            'Priya', 'Rahul', 'Neha', 'Aditya', 'Sunita', 'Vikram', 'Anjali', 'Rajesh', 'Pooja', 'Amit',
            'Divya', 'Sanjay', 'Meera', 'Deepak', 'Rekha'
        ]
        
        last_names = [
            'Sharma', 'Patel', 'Singh', 'Verma', 'Gupta', 'Rao', 'Kumar', 'Chopra', 'Joshi', 'Desai',
            'Mukherjee', 'Agarwal', 'Reddy', 'Bose', 'Mathur'
        ]
        
        specializations = [
            'Mathematics', 'Science', 'English', 'Hindi', 'Social Science', 'Physics', 'Chemistry', 
            'Biology', 'Computer Science', 'Physical Education', 'Art', 'Music', 'Geography', 'History'
        ]
        
        qualifications = [
            'B.Ed, M.Sc Mathematics', 'B.Ed, Ph.D in Physics', 'M.A. English, B.Ed', 
            'M.A. Hindi, B.Ed', 'M.A. History, B.Ed', 'M.Sc Biology, B.Ed', 
            'M.Sc Chemistry, B.Ed', 'M.C.A, B.Ed', 'B.P.Ed, M.P.Ed', 
            'B.F.A, M.F.A', 'M.A. Music, B.Ed', 'M.A. Geography, B.Ed'
        ]
        
        addresses = [
            '123 Teachers Colony, Mumbai', '456 Education Street, Delhi', '789 Knowledge Park, Bangalore',
            '101 Learning Avenue, Chennai', '202 Teacher Lane, Hyderabad', '303 Educator Road, Pune',
            '404 Mentor Street, Ahmedabad', '505 Professor Lane, Kolkata', '606 Academic Road, Jaipur',
            '707 School Street, Lucknow'
        ]
        
        # Create teachers
        created_count = 0
        for i in range(min(len(first_names), len(last_names))):
            # Skip if already exists
            employee_id = f"TCH{1000+i}"
            email = f"{first_names[i].lower()}.{last_names[i].lower()}@school.com"
            
            if Teacher.objects.filter(employee_id=employee_id).exists() or Teacher.objects.filter(email=email).exists():
                self.stdout.write(f"Teacher with employee ID {employee_id} or email {email} already exists, skipping")
                continue
                
            # Create teacher
            teacher = Teacher(
                first_name=first_names[i],
                last_name=last_names[i],
                employee_id=employee_id,
                gender='F' if i % 3 != 1 else 'M',  # Mix of genders
                date_of_birth=date(1980 - random.randint(0, 15), random.randint(1, 12), random.randint(1, 28)),
                email=email,
                phone_number=f"98{random.randint(1000000, 9999999)}",
                address=random.choice(addresses),
                qualification=random.choice(qualifications),
                specialization=random.choice(specializations),
                joining_date=date(2018 - random.randint(0, 5), random.randint(1, 12), random.randint(1, 28)),
                is_active=True
            )
            teacher.save()
            created_count += 1
            
        self.stdout.write(self.style.SUCCESS(f"Successfully created {created_count} sample teachers")) 
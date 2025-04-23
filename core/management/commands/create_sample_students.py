from django.core.management.base import BaseCommand
from django.utils import timezone
from students.models import Student
from datetime import date
import random

class Command(BaseCommand):
    help = 'Creates sample students for testing'
    
    def handle(self, *args, **options):
        # Sample data
        first_names = [
            'Arjun', 'Ananya', 'Ishaan', 'Kavya', 'Yash', 'Rohan', 'Kavya', 'Rohan', 'Diya', 'Aarav',
            'Raj', 'Arjun', 'Meera', 'Ishita', 'Simran', 'Nikhil', 'Sneha', 'Neha', 'Vikram', 'Ayaan',
            'Tanya', 'Aditya', 'Pooja', 'Rahul', 'Simran'
        ]
        
        last_names = [
            'Mehta', 'Desai', 'Mehta', 'Singh', 'Gupta', 'Patel', 'Reddy', 'Patel', 'Kapoor', 'Sharma',
            'Chopra', 'Verma', 'Joshi', 'Verma', 'Gupta', 'Reddy', 'Pillai', 'Singh', 'Joshi', 'Khan',
            'Roy', 'Mishra', 'Nair', 'Deshmukh', 'Arora'
        ]
        
        addresses = [
            '123 Main Street, Mumbai', '456 Park Avenue, Delhi', '789 Garden Road, Bangalore',
            '101 Hill View, Chennai', '202 River Side, Hyderabad', '303 Lake View, Pune',
            '404 Mountain View, Ahmedabad', '505 Ocean View, Kolkata', '606 Valley Road, Jaipur',
            '707 Forest Lane, Lucknow'
        ]
        
        # Create students
        created_count = 0
        for i in range(len(first_names)):
            # Skip if already exists
            roll_number = f"ROLL{100+i}"
            if Student.objects.filter(roll_number=roll_number).exists():
                self.stdout.write(f"Student with roll number {roll_number} already exists, skipping")
                continue
                
            # Random class (1-5)
            class_name = str(random.randint(1, 5))
            
            # Create student
            student = Student(
                first_name=first_names[i],
                last_name=last_names[i],
                roll_number=roll_number,
                class_name=class_name,
                gender='M' if i % 3 != 1 else 'F',  # Mix of genders
                date_of_birth=date(2010 - random.randint(0, 5), random.randint(1, 12), random.randint(1, 28)),
                address=random.choice(addresses),
                phone_number=f"99{random.randint(1000000, 9999999)}",
                email=f"{first_names[i].lower()}.{last_names[i].lower()}@student.school.com",
                parent_name=f"{random.choice(['Mr.', 'Mrs.'])} {last_names[i]}",
                parent_phone=f"98{random.randint(1000000, 9999999)}",
                parent_email=f"parent.{last_names[i].lower()}@gmail.com",
                is_active=True
            )
            student.save()
            created_count += 1
            
        self.stdout.write(self.style.SUCCESS(f"Successfully created {created_count} sample students")) 
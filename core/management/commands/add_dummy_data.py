import os
import sys
import django
import random
from datetime import datetime, timedelta
import string

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

# Import models after Django setup
from django.contrib.auth.models import User
from students.models import Student
from school_teachers.models import Teacher
from attendance.models import Attendance, TeacherAttendance
from django.db import transaction

def generate_random_name():
    first_names = [
        "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Lucas", "Isabella", "Mason",
        "Mia", "Logan", "Charlotte", "Elijah", "Amelia", "Oliver", "Harper", "James", "Evelyn", "Benjamin",
        "Abigail", "Jacob", "Emily", "Alexander", "Elizabeth", "Michael", "Sofia", "William", "Madison", "Daniel",
        "Avery", "Matthew", "Ella", "Jackson", "Scarlett", "David", "Chloe", "Joseph", "Victoria", "Samuel",
        "Grace", "Ryan", "Zoey", "Nathan", "Penelope", "Henry", "Lily", "John", "Nora", "Andrew",
        "Arjun", "Rajesh", "Priya", "Ananya", "Amit", "Meera", "Vikram", "Sunita", "Sanjay", "Deepa",
        "Wei", "Mei", "Kai", "Xiu", "Chen", "Ying", "Jian", "Lin", "Hao", "Ming"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
        "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson",
        "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "Hernandez", "King",
        "Wright", "Lopez", "Hill", "Scott", "Green", "Adams", "Baker", "Gonzalez", "Nelson", "Carter",
        "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins",
        "Patel", "Kumar", "Singh", "Sharma", "Agarwal", "Gupta", "Verma", "Chopra", "Kapoor", "Mehta",
        "Wang", "Li", "Zhang", "Liu", "Chen", "Yang", "Huang", "Zhao", "Wu", "Zhou"
    ]
    
    return random.choice(first_names), random.choice(last_names)

def generate_random_email(first_name, last_name):
    # Create an email with first name, last name and a random domain
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "example.com", "school.edu"]
    return f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@{random.choice(domains)}"

def generate_random_phone():
    # Generate a random 10-digit phone number
    return ''.join(random.choices(string.digits, k=10))

def generate_random_address():
    street_names = ["Main", "Park", "Oak", "Pine", "Maple", "Cedar", "Elm", "View", "Washington", "Lake"]
    street_types = ["Street", "Avenue", "Road", "Boulevard", "Lane", "Drive", "Way", "Place", "Court"]
    cities = ["Springfield", "Riverside", "Fairview", "Kingston", "Burlington", "Franklin", "Greenville", "Clinton", "Salem", "Madison"]
    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD"]
    
    street_num = random.randint(1, 9999)
    street_name = random.choice(street_names)
    street_type = random.choice(street_types)
    city = random.choice(cities)
    state = random.choice(states)
    zip_code = random.randint(10000, 99999)
    
    return f"{street_num} {street_name} {street_type}, {city}, {state} {zip_code}"

def create_random_students(num_students=50):
    """Create random student records"""
    classes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    gender_choices = ['male', 'female']
    created_students = []
    
    for _ in range(num_students):
        first_name, last_name = generate_random_name()
        email = generate_random_email(first_name, last_name)
        dob = datetime.now() - timedelta(days=random.randint(5*365, 18*365))  # 5-18 years old
        
        try:
            # Create user for student
            user = User.objects.create_user(
                username=f"student_{first_name.lower()}_{random.randint(1000, 9999)}",
                email=email,
                password="studentpass123"
            )
            
            # Create student with user
            student = Student.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                date_of_birth=dob.date(),
                roll_number=f"S{random.randint(10000, 99999)}",
                gender=random.choice(gender_choices),
                address=generate_random_address(),
                phone_number=generate_random_phone(),
                email=email,
                class_name=random.choice(classes)
            )
            
            print(f"Created student: {first_name} {last_name}")
            created_students.append(student)
        except Exception as e:
            print(f"Error creating student {first_name} {last_name}: {e}")
    
    return created_students

def create_random_teachers(num_teachers=15):
    """Create random teacher records"""
    subjects = ['Mathematics', 'English', 'Science', 'History', 'Geography', 'Physics', 'Chemistry', 'Biology', 'Computer Science', 'Art', 'Music', 'Physical Education']
    gender_choices = ['male', 'female']
    created_teachers = []
    
    for _ in range(num_teachers):
        first_name, last_name = generate_random_name()
        email = generate_random_email(first_name, last_name)
        dob = datetime.now() - timedelta(days=random.randint(25*365, 60*365))  # 25-60 years old
        joining_date = datetime.now() - timedelta(days=random.randint(30, 3650))  # 1 month to 10 years
        
        try:
            # Create user for teacher
            user = User.objects.create_user(
                username=f"teacher_{first_name.lower()}_{random.randint(1000, 9999)}",
                email=email,
                password="teacherpass123"
            )
            
            # Create teacher with user
            teacher = Teacher.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                date_of_birth=dob.date(),
                gender=random.choice(gender_choices),
                address=generate_random_address(),
                phone_number=generate_random_phone(),
                email=email,
                joining_date=joining_date.date(),
                specialization=random.choice(subjects),
                experience=random.randint(1, 20),
                qualification=random.choice(['Bachelor', 'Master', 'PhD', 'B.Ed', 'M.Ed'])
            )
            
            print(f"Created teacher: {first_name} {last_name}")
            created_teachers.append(teacher)
        except Exception as e:
            print(f"Error creating teacher {first_name} {last_name}: {e}")
    
    return created_teachers

def create_random_attendance(students, start_date, end_date, admin_user):
    """Create random attendance records for students"""
    current_date = start_date
    delta = timedelta(days=1)
    status_choices = ['present', 'absent', 'late', 'half_day']
    status_weights = [0.8, 0.15, 0.03, 0.02]  # Probabilities for each status
    
    while current_date <= end_date:
        # Skip weekends
        if current_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
            current_date += delta
            continue
            
        print(f"Creating attendance records for {current_date.strftime('%Y-%m-%d')}")
        
        # Create batch of attendance records
        attendance_records = []
        for student in students:
            # Weighted random choice for status
            status = random.choices(status_choices, weights=status_weights)[0]
            
            try:
                attendance = Attendance(
                    student=student,
                    date=current_date,
                    status=status,
                    remarks="" if status == 'present' else f"Student {status} on {current_date.strftime('%Y-%m-%d')}",
                    recorded_by=admin_user
                )
                attendance_records.append(attendance)
            except Exception as e:
                print(f"Error creating attendance for {student}: {e}")
        
        # Bulk create attendance records for this date
        try:
            with transaction.atomic():
                Attendance.objects.bulk_create(attendance_records, ignore_conflicts=True)
        except Exception as e:
            print(f"Error bulk creating attendance records: {e}")
            
        current_date += delta

def create_random_teacher_attendance(teachers, start_date, end_date, admin_user):
    """Create random attendance records for teachers"""
    current_date = start_date
    delta = timedelta(days=1)
    status_choices = ['present', 'absent', 'late', 'half_day']
    status_weights = [0.9, 0.07, 0.02, 0.01]  # Probabilities for each status (teachers more likely to be present)
    
    while current_date <= end_date:
        # Skip weekends
        if current_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
            current_date += delta
            continue
            
        print(f"Creating teacher attendance records for {current_date.strftime('%Y-%m-%d')}")
        
        # Create batch of attendance records
        attendance_records = []
        for teacher in teachers:
            # Weighted random choice for status
            status = random.choices(status_choices, weights=status_weights)[0]
            
            try:
                attendance = TeacherAttendance(
                    teacher=teacher,
                    date=current_date,
                    status=status,
                    remarks="" if status == 'present' else f"Teacher {status} on {current_date.strftime('%Y-%m-%d')}",
                    recorded_by=admin_user
                )
                attendance_records.append(attendance)
            except Exception as e:
                print(f"Error creating attendance for {teacher}: {e}")
        
        # Bulk create attendance records for this date
        try:
            with transaction.atomic():
                TeacherAttendance.objects.bulk_create(attendance_records, ignore_conflicts=True)
        except Exception as e:
            print(f"Error bulk creating teacher attendance records: {e}")
            
        current_date += delta

def main():
    try:
        # Get admin user for recording attendance
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            print("No admin user found. Creating a default admin...")
            admin_user = User.objects.create_superuser(
                username="admin", 
                email="admin@example.com", 
                password="adminpass123"
            )
        
        # Check if we already have sufficient data
        existing_students = Student.objects.count()
        existing_teachers = Teacher.objects.count()
        
        if existing_students < 10:
            print(f"Creating students... (Current count: {existing_students})")
            students = create_random_students(50)
        else:
            print(f"Using existing {existing_students} students")
            students = list(Student.objects.all())
            
        if existing_teachers < 5:
            print(f"Creating teachers... (Current count: {existing_teachers})")
            teachers = create_random_teachers(15)
        else:
            print(f"Using existing {existing_teachers} teachers")
            teachers = list(Teacher.objects.all())
        
        # Define date range for attendance records
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=60)  # Last 60 days
        
        # Create attendance records
        create_random_attendance(students, start_date, end_date, admin_user)
        create_random_teacher_attendance(teachers, start_date, end_date, admin_user)
        
        print("Dummy data creation completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 
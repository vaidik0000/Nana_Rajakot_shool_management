from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from students.models import Student
from subjects.models import Subject, StudentMark
from django.utils import timezone
import random
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Associate students with user accounts and create sample marks'

    def handle(self, *args, **options):
        self.stdout.write('Starting to fix student-user associations...')
        
        # Associate students with users based on email
        students = Student.objects.all()
        for student in students:
            if not student.user and student.email:
                try:
                    # Check if user exists with this email
                    try:
                        user = User.objects.get(email=student.email)
                        
                        # Check if this user is already assigned to another student
                        existing_student = Student.objects.filter(user=user).first()
                        if existing_student:
                            self.stdout.write(self.style.WARNING(
                                f'User {user.username} is already assigned to student {existing_student.first_name} {existing_student.last_name}'
                            ))
                            continue
                        
                        student.user = user
                        student.save()
                        self.stdout.write(self.style.SUCCESS(
                            f'Associated {student.first_name} {student.last_name} with user {user.username}'
                        ))
                    except User.DoesNotExist:
                        # Create new user if not exists
                        username = student.email
                        user_count = User.objects.filter(username=username).count()
                        if user_count > 0:
                            username = f"{student.email}_{student.roll_number}"
                        
                        # Create simple password based on roll number for testing
                        password = f"student_{student.roll_number}"
                        
                        user = User.objects.create_user(
                            username=username,
                            email=student.email,
                            password=password,
                            first_name=student.first_name,
                            last_name=student.last_name
                        )
                        
                        student.user = user
                        student.save()
                        self.stdout.write(self.style.SUCCESS(
                            f'Created new user for {student.first_name} {student.last_name} - Login: {username} / {password}'
                        ))
                except IntegrityError as e:
                    self.stdout.write(self.style.ERROR(f'IntegrityError for student {student.id}: {str(e)}'))
        
        # Check if we need to create sample marks
        total_marks = StudentMark.objects.count()
        if total_marks == 0:
            self.stdout.write('No marks found. Creating sample student marks...')
            self.create_sample_marks()
        else:
            self.stdout.write(f'Found {total_marks} student marks already in the database.')
        
        self.stdout.write(self.style.SUCCESS('Successfully fixed student-user associations and marks'))
    
    def create_sample_marks(self):
        # Get all active students and subjects
        students = Student.objects.filter(is_active=True)
        subjects = Subject.objects.filter(is_active=True)
        
        if not students:
            self.stdout.write(self.style.WARNING('No active students found.'))
            return
            
        if not subjects:
            self.stdout.write(self.style.WARNING('No active subjects found.'))
            return
            
        # Create marks for each student in each subject
        marks_created = 0
        for student in students:
            for subject in subjects:
                # Random marks between 60-100
                marks_obtained = random.randint(60, 100)
                total_marks = 100
                
                # Create the mark record
                try:
                    StudentMark.objects.create(
                        student=student,
                        subject=subject,
                        teacher=subject.teacher,
                        marks_obtained=marks_obtained,
                        total_marks=total_marks,
                        date=timezone.now().date()
                    )
                    marks_created += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating mark for {student}: {str(e)}'))
                
        self.stdout.write(self.style.SUCCESS(f'Created {marks_created} sample mark records'))

        self.stdout.write(self.style.SUCCESS('Starting student user fix process'))
        
        # Get all students
        students = Student.objects.all()
        self.stdout.write(f"Found {students.count()} students")
        
        fixed_count = 0
        
        for student in students:
            try:
                # Check if student has a user
                if not student.user:
                    self.stdout.write(self.style.WARNING(f"Student {student.admission_number} has no user!"))
                    continue
                
                # Check username format
                if not student.user.username.startswith('S'):
                    self.stdout.write(self.style.WARNING(
                        f"Fixing username for {student.user.username} to S{student.admission_number}"
                    ))
                    student.user.username = f"S{student.admission_number}"
                    student.user.save()
                    fixed_count += 1
                
                # Check email format 
                expected_email = f"student{student.admission_number}@school.edu"
                if student.user.email != expected_email:
                    self.stdout.write(self.style.WARNING(
                        f"Fixing email for {student.user.username} from {student.user.email} to {expected_email}"
                    ))
                    student.user.email = expected_email
                    student.user.save()
                    fixed_count += 1
                
                # Check student's parent
                if student.parent:
                    # Ensure parent has a proper user account
                    if not student.parent.user:
                        self.stdout.write(self.style.WARNING(f"Parent for {student.admission_number} has no user!"))
                        
                        # Create a user for the parent if they don't have one
                        parent_username = f"P{student.admission_number}"
                        parent_email = f"parent{student.admission_number}@school.edu"
                        
                        parent_user, created = User.objects.get_or_create(
                            username=parent_username,
                            defaults={
                                'email': parent_email,
                                'first_name': student.parent.first_name,
                                'last_name': student.parent.last_name
                            }
                        )
                        
                        if created:
                            # Set a default password for the parent
                            parent_user.set_password(f"parent{student.admission_number}")
                            parent_user.save()
                            
                            # Link the user to the parent profile
                            student.parent.user = parent_user
                            student.parent.save()
                            
                            self.stdout.write(self.style.SUCCESS(
                                f"Created user {parent_username} for parent of {student.admission_number}"
                            ))
                            fixed_count += 1
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error fixing student {student.admission_number}: {str(e)}"))
                logger.error(f"Error in fix_student_users for {student.admission_number}: {str(e)}")
        
        self.stdout.write(self.style.SUCCESS(f"Fixed {fixed_count} student/parent user issues")) 
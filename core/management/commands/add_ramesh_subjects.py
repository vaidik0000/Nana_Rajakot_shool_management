from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from school_teachers.models import Teacher
from subjects.models import Subject, StudentMark
from students.models import Student

class Command(BaseCommand):
    help = 'Add student marks for Ramesh\'s subjects (React JS and Hubspot)'
    
    def handle(self, *args, **kwargs):
        try:
            # Find Ramesh
            teacher = Teacher.objects.get(email='ramesh@gmail.com')
            self.stdout.write(self.style.SUCCESS(f"Found teacher: {teacher.first_name} {teacher.last_name}"))
            
            # Find or create subjects
            react_js, _ = Subject.objects.get_or_create(
                code='REACT101',
                defaults={
                    'name': 'React JS',
                    'description': 'Modern frontend development with React',
                    'teacher': teacher,
                    'credits': 4,
                    'is_active': True
                }
            )
            
            hubspot, _ = Subject.objects.get_or_create(
                code='HUB101',
                defaults={
                    'name': 'Hubspot CRM',
                    'description': 'CRM systems with Hubspot',
                    'teacher': teacher,
                    'credits': 3,
                    'is_active': True
                }
            )
            
            subjects = [react_js, hubspot]
            
            # Get all students
            students = Student.objects.all()
            if not students.exists():
                self.stdout.write(self.style.ERROR("No students found. Please add students first."))
                return
                
            # Clear existing marks for these subjects to avoid duplicates
            StudentMark.objects.filter(subject__in=subjects, teacher=teacher).delete()
            
            # Generate dates for marks
            today = timezone.now().date()
            dates = [
                today - timedelta(days=7),  # Last week
                today - timedelta(days=2),  # Two days ago
                today - timedelta(days=20),  # 20 days ago for older marks
            ]
            
            # Add marks for students
            marks_created = 0
            
            for student in students[:25]:  # Limit to 25 students
                for subject in subjects:
                    # Create 2-3 marks per student per subject
                    num_marks = random.randint(2, 3)
                    for _ in range(num_marks):
                        # Random date from our date list
                        mark_date = random.choice(dates)
                        
                        # Random marks between 65-98
                        marks_obtained = random.randint(65, 98)
                        total_marks = 100
                        
                        # Different remarks based on marks
                        if marks_obtained > 90:
                            remarks = f"Excellent work in {subject.name}!"
                        elif marks_obtained > 80:
                            remarks = f"Good understanding of {subject.name}."
                        elif marks_obtained > 70:
                            remarks = f"Satisfactory performance in {subject.name}."
                        else:
                            remarks = f"Needs improvement in {subject.name}."
                        
                        # Create the mark
                        StudentMark.objects.create(
                            student=student,
                            subject=subject,
                            teacher=teacher,
                            marks_obtained=marks_obtained,
                            total_marks=total_marks,
                            date=mark_date,
                            remarks=remarks
                        )
                        marks_created += 1
            
            self.stdout.write(self.style.SUCCESS(f"Created {marks_created} student marks for Ramesh's subjects"))
            
        except Teacher.DoesNotExist:
            self.stdout.write(self.style.ERROR("Teacher Ramesh not found. Please create teacher first."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error adding student marks: {str(e)}")) 
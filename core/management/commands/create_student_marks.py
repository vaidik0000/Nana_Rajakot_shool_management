from django.core.management.base import BaseCommand
from subjects.models import Subject, StudentMark
from students.models import Student
from school_teachers.models import Teacher
import random
from django.utils import timezone

class Command(BaseCommand):
    help = 'Creates sample student marks for all students'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating sample student marks...')
        
        subjects = [
            'Mathematics',
            'English', 
            'Science',
            'Social Studies',
            'Computer Science',
            'Physical Education',
            'Art',
            'Music',
            'Geography',
            'History'
        ]
        
        students = Student.objects.all()
        
        if not students.exists():
            self.stdout.write(self.style.ERROR('No students found. Please create students first.'))
            return
            
        self.stdout.write(f'Found {students.count()} students.')
        
        teachers = list(Teacher.objects.all())
        if not teachers:
            self.stdout.write(self.style.ERROR('No teachers found. Please create teachers first.'))
            return
            
        # Create subjects and marks
        for subject_name in subjects:
            try:
                subject = Subject.objects.get(name=subject_name)
                self.stdout.write(f'Found existing subject: {subject.name}')
            except Subject.DoesNotExist:
                teacher = random.choice(teachers)
                subject = Subject.objects.create(
                    name=subject_name,
                    code=f'{subject_name[:3].upper()}101',
                    description=f'Study of {subject_name}',
                    teacher=teacher,
                    credits=4,
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS(f'Created subject: {subject.name} (Teacher: {teacher.first_name} {teacher.last_name})'))
            
            # Add marks for all students in this subject
            for student in students:
                # Check if student already has marks for this subject
                existing_mark = StudentMark.objects.filter(student=student, subject=subject).first()
                if existing_mark:
                    self.stdout.write(f'Student {student.first_name} already has marks for {subject.name}')
                    continue
                
                # Generate random marks between 65 and 98
                marks_obtained = random.randint(65, 98)
                
                # Create the student mark
                StudentMark.objects.create(
                    student=student,
                    subject=subject,
                    teacher=subject.teacher,
                    marks_obtained=marks_obtained,
                    total_marks=100,
                    date=timezone.now().date()
                )
                
        # Calculate total marks created
        total_marks = StudentMark.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Successfully created {total_marks} student marks across {len(subjects)} subjects')) 
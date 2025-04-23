from django.core.management.base import BaseCommand
from students.models import Student
from subjects.models import Subject, StudentMark
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Create sample student marks for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force creating new marks even if marks already exist',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        # Check if we already have marks
        total_marks = StudentMark.objects.count()
        if total_marks > 0 and not force:
            self.stdout.write(self.style.WARNING(
                f'Found {total_marks} student marks already in the database. Use --force to create more.'
            ))
            return
            
        self.stdout.write('Creating sample student marks...')
        marks_created = self.create_sample_marks()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {marks_created} sample marks'))
    
    def create_sample_marks(self):
        # Get all active students and subjects
        students = Student.objects.filter(is_active=True)
        subjects = Subject.objects.filter(is_active=True)
        
        if not students:
            self.stdout.write(self.style.WARNING('No active students found.'))
            return 0
            
        if not subjects:
            self.stdout.write(self.style.WARNING('No active subjects found.'))
            return 0
        
        self.stdout.write(f'Found {students.count()} students and {subjects.count()} subjects')
            
        # Create marks for each student in each subject
        marks_created = 0
        for student in students:
            student_marks = []
            for subject in subjects:
                # Check if mark already exists
                if StudentMark.objects.filter(student=student, subject=subject).exists():
                    self.stdout.write(f'Mark already exists for {student} in {subject.name}')
                    continue
                    
                # Random marks between 40-100
                marks_obtained = random.randint(40, 100)
                total_marks = 100
                
                try:
                    # Create the mark record
                    mark = StudentMark(
                        student=student,
                        subject=subject,
                        teacher=subject.teacher,
                        marks_obtained=marks_obtained,
                        total_marks=total_marks,
                        date=timezone.now().date()
                    )
                    student_marks.append(mark)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating mark for {student}: {str(e)}'))
            
            # Bulk create the marks for this student
            if student_marks:
                StudentMark.objects.bulk_create(student_marks)
                marks_created += len(student_marks)
                self.stdout.write(f'Created {len(student_marks)} marks for {student}')
        
        return marks_created 
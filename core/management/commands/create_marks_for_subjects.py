from django.core.management.base import BaseCommand
from subjects.models import Subject, StudentMark
from students.models import Student
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Create student marks for all subjects, ensuring every student has marks for each subject'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force creating marks even if they already exist',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        self.stdout.write('Creating student marks for all subjects...')
        
        # Get all active students and subjects
        students = Student.objects.filter(is_active=True)
        subjects = Subject.objects.filter(is_active=True)
        
        # Check if we have data to work with
        if not students:
            self.stdout.write(self.style.ERROR('No active students found. Cannot create marks.'))
            return
            
        if not subjects:
            self.stdout.write(self.style.ERROR('No active subjects found. Cannot create marks.'))
            return
        
        self.stdout.write(f'Found {students.count()} students and {subjects.count()} subjects')
        
        # Create marks for each student in each subject
        total_marks_created = 0
        total_marks_skipped = 0
        
        for student in students:
            student_marks_created = 0
            student_marks_skipped = 0
            
            for subject in subjects:
                # Check if mark already exists for this student and subject
                if not force and StudentMark.objects.filter(student=student, subject=subject).exists():
                    student_marks_skipped += 1
                    continue
                
                # Get the teacher from the subject
                teacher = subject.teacher
                
                # Generate random marks between 40-100 for more realistic distribution
                marks_obtained = random.randint(40, 100)
                total_marks = 100
                
                try:
                    # Create the mark record
                    mark = StudentMark.objects.create(
                        student=student,
                        subject=subject,
                        teacher=teacher,
                        marks_obtained=marks_obtained,
                        total_marks=total_marks,
                        date=timezone.now().date()
                    )
                    student_marks_created += 1
                    total_marks_created += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Error creating mark for {student} in {subject.name}: {str(e)}'
                    ))
            
            if student_marks_created > 0:
                self.stdout.write(
                    f'Created {student_marks_created} marks for {student.first_name} {student.last_name} ' +
                    (f'({student_marks_skipped} skipped)' if student_marks_skipped > 0 else '')
                )
            total_marks_skipped += student_marks_skipped
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully created {total_marks_created} marks ' +
            (f'({total_marks_skipped} skipped)' if total_marks_skipped > 0 else '')
        )) 
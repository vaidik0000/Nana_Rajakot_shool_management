from django.core.management.base import BaseCommand
from subjects.models import StudentMark

class Command(BaseCommand):
    help = 'Fix existing student marks by recalculating percentages and grades'

    def handle(self, *args, **options):
        self.stdout.write('Starting to fix student marks calculations...')
        
        # Get all student marks
        marks = StudentMark.objects.all()
        total_marks = marks.count()
        self.stdout.write(f'Found {total_marks} student marks to fix')
        
        fixed_marks = 0
        for mark in marks:
            old_percentage = mark.percentage
            old_grade = mark.grade
            
            # Recalculate percentage
            if mark.total_marks > 0:
                marks_float = float(mark.marks_obtained)
                total_float = float(mark.total_marks)
                percentage_value = (marks_float / total_float) * 100
                mark.percentage = round(percentage_value, 2)
                
                # Determine grade based on percentage
                if mark.percentage >= 90:
                    mark.grade = 'A+'
                elif mark.percentage >= 75:
                    mark.grade = 'A'
                elif mark.percentage >= 60:
                    mark.grade = 'B'
                elif mark.percentage >= 50:
                    mark.grade = 'C'
                elif mark.percentage >= 33:
                    mark.grade = 'D'
                else:
                    mark.grade = 'E'
            else:
                mark.percentage = 0
                mark.grade = 'E'
            
            # Only save if values actually changed
            if mark.percentage != old_percentage or mark.grade != old_grade:
                # Use update without triggering save method
                StudentMark.objects.filter(id=mark.id).update(
                    percentage=mark.percentage,
                    grade=mark.grade
                )
                
                self.stdout.write(
                    f"Fixed mark for {mark.student} in {mark.subject}: "
                    f"{old_percentage}% ({old_grade}) → {mark.percentage}% ({mark.grade})"
                )
                fixed_marks += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully fixed {fixed_marks} out of {total_marks} student marks')) 
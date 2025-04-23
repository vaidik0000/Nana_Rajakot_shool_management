from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone

class Command(BaseCommand):
    help = 'Generate comprehensive demo data for the entire school management system'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--students',
            type=int,
            default=25,
            help='Number of students to create (default: 25)'
        )
        parser.add_argument(
            '--teachers',
            type=int,
            default=10,
            help='Number of teachers to create (default: 10)'
        )
        parser.add_argument(
            '--clear_timetable',
            action='store_true',
            help='Clear existing timetable before generating new one'
        )
        parser.add_argument(
            '--book_issues',
            type=int,
            default=20,
            help='Number of book issues to create (default: 20)'
        )
    
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('=== Starting School Data Generation ==='))
        self.stdout.write(self.style.SUCCESS(f'Current time: {timezone.now()}'))
        
        # 1. Create sample teachers
        self.stdout.write(self.style.NOTICE('\n[1/8] Creating sample teachers...'))
        try:
            call_command('create_sample_teachers', count=kwargs['teachers'])
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating teachers: {str(e)}"))
        
        # 2. Create sample students
        self.stdout.write(self.style.NOTICE('\n[2/8] Creating sample students...'))
        try:
            call_command('create_sample_students', count=kwargs['students'])
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating students: {str(e)}"))
        
        # 3. Create sample subjects
        self.stdout.write(self.style.NOTICE('\n[3/8] Creating sample subjects...'))
        try:
            call_command('create_sample_subjects')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating subjects: {str(e)}"))
        
        # 4. Create student marks
        self.stdout.write(self.style.NOTICE('\n[4/8] Creating student marks...'))
        try:
            call_command('create_student_marks')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating student marks: {str(e)}"))
        
        # 5. Create attendance data
        self.stdout.write(self.style.NOTICE('\n[5/8] Creating attendance data...'))
        try:
            call_command('create_attendance_data')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating attendance data: {str(e)}"))
        
        # 6. Create timetable
        self.stdout.write(self.style.NOTICE('\n[6/8] Creating timetable data...'))
        try:
            clear_arg = ['--clear'] if kwargs['clear_timetable'] else []
            call_command('create_timetable_data', *clear_arg)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating timetable data: {str(e)}"))
        
        # 7. Create library books and issues
        self.stdout.write(self.style.NOTICE('\n[7/8] Creating library data...'))
        try:
            call_command('seed_library')
            call_command('create_book_issues', count=kwargs['book_issues'])
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating library data: {str(e)}"))
        
        # 8. Create events
        self.stdout.write(self.style.NOTICE('\n[8/8] Creating school events...'))
        try:
            call_command('create_events')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating events: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS('\n=== School Data Generation Complete ==='))
        self.stdout.write(self.style.SUCCESS('You now have a fully populated school management system with demo data!')) 
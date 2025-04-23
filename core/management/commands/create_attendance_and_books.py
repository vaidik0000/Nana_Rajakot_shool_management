from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone

class Command(BaseCommand):
    help = 'Generate demo data for library books and book issues'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--book_issues_count',
            type=int,
            default=20,
            help='Number of book issue records to create'
        )
    
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('=== Starting Library Demo Data Generation ==='))
        self.stdout.write(self.style.SUCCESS(f'Current time: {timezone.now()}'))
        
        # Generate demo library data
        self.stdout.write(self.style.NOTICE('\n[1/2] Generating library book catalog...'))
        call_command('seed_library')
        
        # Create book issues
        self.stdout.write(self.style.NOTICE('\n[2/2] Generating book issue records...'))
        call_command('create_book_issues', count=kwargs['book_issues_count'])
        
        self.stdout.write(self.style.SUCCESS('\n=== Library Demo Data Generation Complete ===')) 
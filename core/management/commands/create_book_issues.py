from django.core.management.base import BaseCommand
from library.models import Book, BookIssue
from students.models import Student
from school_teachers.models import Teacher
from django.contrib.auth.models import User
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Creates sample book issue records for the library'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=15,
            help='Number of book issues to create'
        )
        
    def handle(self, *args, **kwargs):
        count = kwargs['count']
        
        books = Book.objects.all()
        students = Student.objects.all()
        teachers = Teacher.objects.all()
        library_staff = User.objects.filter(is_staff=True).first()
        
        if not books.exists():
            self.stdout.write(self.style.ERROR('No books found. Please add books first using the seed_library command.'))
            return
            
        if not students.exists() and not teachers.exists():
            self.stdout.write(self.style.ERROR('No students or teachers found. Please add some first.'))
            return
            
        if not library_staff:
            self.stdout.write(self.style.WARNING('No staff user found. Using first available user as library staff.'))
            library_staff = User.objects.first()
        
        issues_created = 0
        today = date.today()
        
        # List of possible statuses and their probability weights
        statuses = [
            ('issued', 0.4),  # 40% chance
            ('returned', 0.3), # 30% chance
            ('overdue', 0.2),  # 20% chance
            ('lost', 0.1)      # 10% chance
        ]
        status_choices = [s[0] for s in statuses]
        status_weights = [s[1] for s in statuses]
        
        # Create book issues
        for _ in range(count):
            book = random.choice(books)
            
            # Randomly decide if book is issued to student or teacher
            if random.random() < 0.8 or not teachers.exists():  # 80% chance for student if teachers exist
                borrower_type = 'student'
                borrower = random.choice(students)
            else:
                borrower_type = 'teacher'
                borrower = random.choice(teachers)
            
            # Generate random dates
            # Issue date between 60 days ago and today
            days_ago = random.randint(0, 60)
            issue_date = today - timedelta(days=days_ago)
            
            # Due date between 1 and 30 days after issue date
            due_days = random.randint(7, 30)
            due_date = issue_date + timedelta(days=due_days)
            
            # Select status based on weighted probability
            status = random.choices(status_choices, status_weights)[0]
            
            # Determine return date based on status
            return_date = None
            if status == 'returned':
                return_days = random.randint(1, due_days)
                return_date = issue_date + timedelta(days=return_days)
            elif status == 'overdue':
                # No return date for overdue books
                pass
            elif status == 'lost':
                # No return date for lost books
                pass
            
            # Calculate fine for overdue or lost books
            fine_amount = 0
            if status == 'overdue':
                overdue_days = (today - due_date).days
                fine_amount = overdue_days * 5  # ₹5 per day
            elif status == 'lost':
                fine_amount = random.randint(100, 500)  # Random fine between ₹100 and ₹500
            
            # Create the book issue
            try:
                book_issue = BookIssue()
                book_issue.book = book
                book_issue.issue_date = issue_date
                book_issue.due_date = due_date
                book_issue.return_date = return_date
                book_issue.status = status
                book_issue.fine_amount = fine_amount
                book_issue.issued_by = library_staff
                
                if status == 'returned':
                    book_issue.returned_to = library_staff
                
                if borrower_type == 'student':
                    book_issue.student = borrower
                else:
                    book_issue.teacher = borrower
                
                book_issue.save()
                issues_created += 1
                
                self.stdout.write(f"Created book issue: {book.title} - borrowed by {borrower} - {status}")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating book issue: {str(e)}"))
                
        self.stdout.write(self.style.SUCCESS(f'Successfully created {issues_created} book issues!')) 
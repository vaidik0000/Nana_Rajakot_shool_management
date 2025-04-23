from django.core.management.base import BaseCommand
from library.models import BookCategory, Book
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Seeds the database with demo library books'
    
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating demo library data...'))
        
        # Ensure categories exist
        self.create_categories()
        
        # Add demo books
        books_created = self.create_books()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {books_created} demo books!'))
    
    def create_categories(self):
        """Create book categories if they don't exist"""
        categories = [
            ('romance', 'Romance'),
            ('scifi_fantasy', 'Sci-Fi/Fantasy'),
            ('action_adventure', 'Action Adventure/Thriller'),
            ('mystery', 'Mystery'),
            ('horror', 'Horror/Dystopian'),
            ('children', "Children's"),
        ]
        
        for category_id, category_name in categories:
            category, created = BookCategory.objects.get_or_create(
                name=category_id,
                defaults={'description': f'Books in the {category_name} category'}
            )
            
            if created:
                self.stdout.write(f"Created category: {category_name}")
            else:
                self.stdout.write(f"Category exists: {category_name}")
    
    def create_books(self):
        """Create demo books in the library"""
        # Dictionary mapping category names to a list of books for that category
        books_by_category = {
            'romance': [
                {
                    'title': 'Pride and Prejudice',
                    'author': 'Jane Austen',
                    'isbn': '9780141439518',
                    'publisher': 'Penguin Classics',
                    'publication_year': 1813,
                    'edition': 'Revised',
                    'description': 'The classic tale of Elizabeth Bennet and Mr. Darcy.',
                    'total_copies': 5,
                    'shelf_location': 'R1-A2'
                },
                {
                    'title': 'Jane Eyre',
                    'author': 'Charlotte Brontë',
                    'isbn': '9780141441146',
                    'publisher': 'Penguin Classics',
                    'publication_year': 1847,
                    'edition': 'Revised',
                    'description': 'The story of a passionate young woman\'s search for a wider life.',
                    'total_copies': 3,
                    'shelf_location': 'R1-A3'
                },
            ],
            'scifi_fantasy': [
                {
                    'title': 'The Hobbit',
                    'author': 'J.R.R. Tolkien',
                    'isbn': '9780261102217',
                    'publisher': 'HarperCollins',
                    'publication_year': 1937,
                    'edition': '75th Anniversary',
                    'description': 'The classic adventure of Bilbo Baggins.',
                    'total_copies': 8,
                    'shelf_location': 'SF2-B1'
                },
                {
                    'title': 'Dune',
                    'author': 'Frank Herbert',
                    'isbn': '9780441172719',
                    'publisher': 'Ace Books',
                    'publication_year': 1965,
                    'edition': 'Revised',
                    'description': 'Set on the desert planet Arrakis, the story explores politics, religion, and power.',
                    'total_copies': 4,
                    'shelf_location': 'SF2-B3'
                },
                {
                    'title': 'Foundation',
                    'author': 'Isaac Asimov',
                    'isbn': '9780553293357',
                    'publisher': 'Bantam Spectra',
                    'publication_year': 1951,
                    'edition': 'Reprint',
                    'description': 'The first novel in Isaac Asimov\'s Foundation series.',
                    'total_copies': 3,
                    'shelf_location': 'SF2-C1'
                },
            ],
            'action_adventure': [
                {
                    'title': 'The Da Vinci Code',
                    'author': 'Dan Brown',
                    'isbn': '9780307474278',
                    'publisher': 'Anchor Books',
                    'publication_year': 2003,
                    'edition': 'Special Illustrated',
                    'description': 'A thrilling novel exploring hidden secrets and mysterious symbols.',
                    'total_copies': 7,
                    'shelf_location': 'AA3-A1'
                },
                {
                    'title': 'The Hunt for Red October',
                    'author': 'Tom Clancy',
                    'isbn': '9780425269367',
                    'publisher': 'Berkley',
                    'publication_year': 1984,
                    'edition': 'Reprint',
                    'description': 'A classic military thriller about a Soviet submarine.',
                    'total_copies': 4,
                    'shelf_location': 'AA3-B2'
                },
            ],
            'mystery': [
                {
                    'title': 'Murder on the Orient Express',
                    'author': 'Agatha Christie',
                    'isbn': '9780062693662',
                    'publisher': 'William Morrow Paperbacks',
                    'publication_year': 1934,
                    'edition': 'Reprint',
                    'description': 'Hercule Poirot investigates a murder on a train stuck in a snowdrift.',
                    'total_copies': 6,
                    'shelf_location': 'M4-A1'
                },
                {
                    'title': 'The Hound of the Baskervilles',
                    'author': 'Arthur Conan Doyle',
                    'isbn': '9780141199177',
                    'publisher': 'Penguin Classics',
                    'publication_year': 1902,
                    'edition': 'Revised',
                    'description': 'Sherlock Holmes investigates the case of a supernatural hound.',
                    'total_copies': 5,
                    'shelf_location': 'M4-A4'
                },
                {
                    'title': 'Gone Girl',
                    'author': 'Gillian Flynn',
                    'isbn': '9780307588371',
                    'publisher': 'Broadway Books',
                    'publication_year': 2012,
                    'edition': 'First',
                    'description': 'A woman goes missing on her fifth wedding anniversary.',
                    'total_copies': 4,
                    'shelf_location': 'M4-B2'
                },
            ],
            'horror': [
                {
                    'title': 'The Shining',
                    'author': 'Stephen King',
                    'isbn': '9780307743657',
                    'publisher': 'Anchor',
                    'publication_year': 1977,
                    'edition': 'Reprint',
                    'description': 'A family heads to an isolated hotel for the winter where a sinister presence influences the father.',
                    'total_copies': 5,
                    'shelf_location': 'H5-A1'
                },
                {
                    'title': 'Dracula',
                    'author': 'Bram Stoker',
                    'isbn': '9780141439846',
                    'publisher': 'Penguin Classics',
                    'publication_year': 1897,
                    'edition': 'Revised',
                    'description': 'The classic vampire novel that introduced Count Dracula.',
                    'total_copies': 3,
                    'shelf_location': 'H5-A3'
                },
            ],
            'children': [
                {
                    'title': 'Harry Potter and the Philosopher\'s Stone',
                    'author': 'J.K. Rowling',
                    'isbn': '9781408855652',
                    'publisher': 'Bloomsbury',
                    'publication_year': 1997,
                    'edition': 'New',
                    'description': 'The first book in the Harry Potter series.',
                    'total_copies': 10,
                    'shelf_location': 'C6-A1'
                },
                {
                    'title': 'Charlotte\'s Web',
                    'author': 'E.B. White',
                    'isbn': '9780064410939',
                    'publisher': 'HarperCollins',
                    'publication_year': 1952,
                    'edition': 'Special',
                    'description': 'The story of a pig named Wilbur and his friendship with a barn spider named Charlotte.',
                    'total_copies': 7,
                    'shelf_location': 'C6-B2'
                },
                {
                    'title': 'The Lion, the Witch and the Wardrobe',
                    'author': 'C.S. Lewis',
                    'isbn': '9780007115617',
                    'publisher': 'HarperCollins',
                    'publication_year': 1950,
                    'edition': 'Reprint',
                    'description': 'Four children travel through a wardrobe to the magical land of Narnia.',
                    'total_copies': 6,
                    'shelf_location': 'C6-B4'
                },
            ],
        }
        
        books_created = 0
        
        # For each category, create the books
        for category_name, books in books_by_category.items():
            try:
                category = BookCategory.objects.get(name=category_name)
                
                for book_data in books:
                    # Calculate available copies (randomly between 50-100% of total)
                    total_copies = book_data['total_copies']
                    available_copies = random.randint(max(1, int(total_copies * 0.5)), total_copies)
                    
                    # Determine status based on available copies
                    status = 'available' if available_copies > 0 else 'borrowed'
                    
                    book, created = Book.objects.get_or_create(
                        isbn=book_data['isbn'],
                        defaults={
                            'title': book_data['title'],
                            'author': book_data['author'],
                            'category': category,
                            'publisher': book_data['publisher'],
                            'publication_year': book_data['publication_year'],
                            'edition': book_data['edition'],
                            'description': book_data['description'],
                            'total_copies': total_copies,
                            'available_copies': available_copies,
                            'shelf_location': book_data['shelf_location'],
                            'status': status
                        }
                    )
                    
                    if created:
                        books_created += 1
                        self.stdout.write(f"Created book: {book.title} by {book.author}")
                    else:
                        self.stdout.write(f"Book exists: {book.title} by {book.author}")
                        
            except BookCategory.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Category {category_name} does not exist. Skipping books."))
        
        return books_created 
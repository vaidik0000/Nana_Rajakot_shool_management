from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from library.models import Book
from django.db.models import Q

class BookSearchAPIView(APIView):
    """
    API endpoint for searching books by title or author
    Used by the chatbot to find book details
    """
    def get(self, request):
        query = request.GET.get('query', '')
        
        if not query:
            return Response({
                'found': False,
                'message': 'No search term provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Search in title and author fields
        books = Book.objects.filter(
            Q(title__icontains=query) | 
            Q(author__icontains=query) |
            Q(isbn__icontains=query)
        )
        
        if books.exists():
            # Create a simple serialized output for each book
            books_data = []
            for book in books:
                book_data = {
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'isbn': book.isbn,
                    'category': book.category.get_name_display() if book.category else None,
                    'publisher': book.publisher,
                    'publication_year': book.publication_year,
                    'edition': book.edition,
                    'total_copies': book.total_copies,
                    'available_copies': book.available_copies,
                    'shelf_location': book.shelf_location,
                    'status': book.get_status_display(),
                }
                books_data.append(book_data)
                
            return Response({
                'found': True,
                'books': books_data,
                'count': books.count()
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'found': False,
                'message': 'No books found matching the search term'
            }, status=status.HTTP_404_NOT_FOUND) 
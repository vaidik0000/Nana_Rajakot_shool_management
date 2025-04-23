from django.urls import path
from . import views

urlpatterns = [
    # Chatbot API endpoint for book search
    path('search/', views.BookSearchAPIView.as_view(), name='book_search_api'),
] 
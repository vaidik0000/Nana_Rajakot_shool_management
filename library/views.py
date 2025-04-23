from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import BookCategory, Book, BookIssue
from .forms import BookCategoryForm, BookForm, BookIssueForm, BookReturnForm
from core.decorators import teacher_required, student_required, admin_required, new_user_restricted

# Create your views here.

# Book Category Views
@login_required
def category_list(request):
    categories = BookCategory.objects.all()
    return render(request, 'library/category_list.html', {'categories': categories})

@teacher_required
@new_user_restricted
def category_create(request):
    if request.method == 'POST':
        form = BookCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book category created successfully.')
            return redirect('library:category_list')
    else:
        form = BookCategoryForm()
    return render(request, 'library/category_form.html', {'form': form, 'title': 'Add Book Category'})

@teacher_required
@new_user_restricted
def category_edit(request, pk):
    category = get_object_or_404(BookCategory, pk=pk)
    if request.method == 'POST':
        form = BookCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book category updated successfully.')
            return redirect('library:category_list')
    else:
        form = BookCategoryForm(instance=category)
    return render(request, 'library/category_form.html', {'form': form, 'title': 'Edit Book Category'})

@teacher_required
@new_user_restricted
def category_delete(request, pk):
    category = get_object_or_404(BookCategory, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Book category deleted successfully.')
        return redirect('library:category_list')
    return render(request, 'library/category_confirm_delete.html', {'category': category})

# Book Views
@login_required
def book_list(request):
    books = Book.objects.all()
    query = request.GET.get('q')
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(isbn__icontains=query) |
            Q(publisher__icontains=query)
        )
    return render(request, 'library/book_list.html', {'books': books})

@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    issues = book.issues.all().order_by('-issue_date')
    return render(request, 'library/book_detail.html', {'book': book, 'issues': issues})

@teacher_required
@new_user_restricted
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book added successfully.')
            return redirect('library:book_list')
    else:
        form = BookForm()
    return render(request, 'library/book_form.html', {'form': form, 'title': 'Add Book'})

@teacher_required
@new_user_restricted
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully.')
            return redirect('library:book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'library/book_form.html', {'form': form, 'title': 'Edit Book'})

@teacher_required
@new_user_restricted
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully.')
        return redirect('library:book_list')
    return render(request, 'library/book_confirm_delete.html', {'book': book})

# Book Issue Views
@login_required
def issue_list(request):
    issues = BookIssue.objects.all()
    status_filter = request.GET.get('status')
    if status_filter:
        issues = issues.filter(status=status_filter)
    return render(request, 'library/issue_list.html', {'issues': issues})

@teacher_required
@new_user_restricted
def issue_create(request):
    if request.method == 'POST':
        form = BookIssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.issued_by = request.user
            issue.issue_date = timezone.now().date()
            
            # Validate due date is in the future
            if issue.due_date <= issue.issue_date:
                messages.error(request, 'Due date must be in the future.')
                return render(request, 'library/issue_form.html', {'form': form, 'title': 'Issue Book'})
            
            # Validate book availability
            book = issue.book
            if book.available_copies <= 0:
                messages.error(request, 'No copies available for this book.')
                return redirect('library:issue_list')
            
            # Save the issue and update book availability
            issue.save()
            book.available_copies -= 1
            if book.available_copies == 0:
                book.status = 'borrowed'
            book.save()
            
            messages.success(request, 'Book issued successfully.')
            return redirect('library:issue_list')
    else:
        form = BookIssueForm()
    return render(request, 'library/issue_form.html', {'form': form, 'title': 'Issue Book'})

@teacher_required
@new_user_restricted
def issue_return(request, pk):
    issue = get_object_or_404(BookIssue, pk=pk)

    if issue.return_date:
        messages.warning(request, 'This book has already been returned.')
        return redirect('library:issue_detail', pk=issue.pk)

    if request.method == 'POST':
        form = BookReturnForm(request.POST, instance=issue)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.returned_to = request.user

            # Calculate fine if returned late
            if issue.return_date > issue.due_date:
                days_overdue = (issue.return_date - issue.due_date).days
                issue.fine_amount = days_overdue * 10
                issue.status = 'overdue'
            else:
                issue.status = 'returned'

            issue.save()

            # Update book availability
            book = issue.book
            book.available_copies += 1
            if book.available_copies == book.total_copies:
                book.status = 'available'
            book.save()

            messages.success(request, 'Book returned successfully.')
            return redirect('library:issue_detail', pk=issue.pk)
        else:
            messages.error(request, 'There was a problem with your submission. Please check the form.')
    else:
        issue.return_date = timezone.now().date()  # Set return date on GET
        form = BookReturnForm(instance=issue)

    return render(request, 'library/issue_return.html', {
        'form': form,
        'issue': issue,
        'title': 'Return Book'
    })

@login_required
def issue_detail(request, pk):
    issue = get_object_or_404(BookIssue, pk=pk)
    return render(request, 'library/issue_detail.html', {'issue': issue})

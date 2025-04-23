from django.db import models
from django.contrib.auth.models import User
from students.models import Student
from school_teachers.models import Teacher

class BookCategory(models.Model):
    CATEGORY_CHOICES = (
        ('romance', 'Romance'),
        ('scifi_fantasy', 'Sci-Fi/Fantasy'),
        ('action_adventure', 'Action Adventure/Thriller'),
        ('mystery', 'Mystery'),
        ('horror', 'Horror/Dystopian'),
        ('children', "Children's"),
    )

    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_name_display()

    class Meta:
        verbose_name_plural = "Book Categories"
        ordering = ['name']

class Book(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
    )

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    category = models.ForeignKey(BookCategory, on_delete=models.CASCADE, related_name='books')
    publisher = models.CharField(max_length=200)
    publication_year = models.PositiveIntegerField()
    edition = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    shelf_location = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        ordering = ['title']

class BookIssue(models.Model):
    STATUS_CHOICES = (
        ('issued', 'Issued'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('lost', 'Lost'),
    )

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issues')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='book_issues', null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='book_issues', null=True, blank=True)
    issue_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='issued')
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remarks = models.TextField(blank=True)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='issued_books')
    returned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='returned_books', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        borrower = self.student or self.teacher
        return f"{self.book.title} - {borrower}"

    class Meta:
        ordering = ['-issue_date']

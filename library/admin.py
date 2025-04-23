from django.contrib import admin
from .models import BookCategory, Book, BookIssue

@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'category', 'publisher', 'publication_year', 'status', 'available_copies', 'total_copies')
    list_filter = ('category', 'status', 'publication_year')
    search_fields = ('title', 'author', 'isbn', 'publisher')
    list_editable = ('status',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'isbn', 'category', 'publisher', 'publication_year', 'edition')
        }),
        ('Details', {
            'fields': ('description', 'total_copies', 'available_copies', 'shelf_location', 'status', 'cover_image')
        }),
    )

@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    list_display = ('book', 'get_borrower', 'issue_date', 'due_date', 'return_date', 'status', 'fine_amount')
    list_filter = ('status', 'issue_date', 'due_date', 'return_date')
    search_fields = ('book__title', 'book__author', 'student__first_name', 'student__last_name', 'teacher__first_name', 'teacher__last_name')
    raw_id_fields = ('book', 'student', 'teacher', 'issued_by', 'returned_to')
    date_hierarchy = 'issue_date'
    
    def get_borrower(self, obj):
        if obj.student:
            return f"Student: {obj.student.first_name} {obj.student.last_name}"
        elif obj.teacher:
            return f"Teacher: {obj.teacher.first_name} {obj.teacher.last_name}"
        return "Unknown"
    get_borrower.short_description = 'Borrower'

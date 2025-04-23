from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect, FileResponse, Http404
from django.db import IntegrityError
from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache

from .models import DocumentType, StudentDocument
from .forms import DocumentTypeForm, StudentDocumentForm
from students.models import Student

# Helper functions
def is_admin(user):
    """Check if user is admin or superuser"""
    return user.is_staff or user.is_superuser

# Document Type Views
class DocumentTypeListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = DocumentType
    template_name = 'documents/document_type_list.html'
    context_object_name = 'document_types'
    
    def test_func(self):
        return is_admin(self.request.user)

class DocumentTypeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = DocumentType
    form_class = DocumentTypeForm
    template_name = 'documents/document_type_form.html'
    success_url = reverse_lazy('documents:document_type_list')
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Document type created successfully!')
        return super().form_valid(form)

class DocumentTypeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = DocumentType
    form_class = DocumentTypeForm
    template_name = 'documents/document_type_form.html'
    success_url = reverse_lazy('documents:document_type_list')
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Document type updated successfully!')
        return super().form_valid(form)

class DocumentTypeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = DocumentType
    template_name = 'documents/document_type_confirm_delete.html'
    success_url = reverse_lazy('documents:document_type_list')
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def delete(self, request, *args, **kwargs):
        doc_type = self.get_object()
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(request, f'Document type "{doc_type.name}" deleted successfully!')
            return response
        except IntegrityError:
            messages.error(request, f'Cannot delete "{doc_type.name}" as it is currently in use. Deactivate it instead.')
            return HttpResponseRedirect(self.success_url)

# Student Document Matrix View
@login_required
@user_passes_test(is_admin)
def document_matrix_view(request):
    """
    Display the matrix of students and document types
    """
    # Clear cache to ensure we're getting the latest data
    cache.clear()
    
    # Get all active document types
    document_types = DocumentType.objects.filter(active=True)
    
    # Get all students
    students_list = Student.objects.all().order_by('first_name', 'last_name')
    
    # Handle search query
    search_query = request.GET.get('q', '')
    if search_query:
        # Filter students by name or ID
        students_list = students_list.filter(
            models.Q(first_name__icontains=search_query) | 
            models.Q(last_name__icontains=search_query) | 
            models.Q(roll_number__icontains=search_query) |
            models.Q(email__icontains=search_query)
        )
    
    # Paginate students list - display 10 students per page
    page = request.GET.get('page', 1)
    paginator = Paginator(students_list, 10)
    
    try:
        students = paginator.page(page)
    except PageNotAnInteger:
        students = paginator.page(1)
    except EmptyPage:
        students = paginator.page(paginator.num_pages)
    
    # Get all documents for the students on the current page
    # This provides better performance than querying for each cell in the template
    student_ids = [student.id for student in students]
    all_documents = StudentDocument.objects.filter(student_id__in=student_ids).select_related('student', 'document_type')
    
    # Create a lookup dictionary for quick document retrieval
    # Key format: "student_id_document_type_id"
    document_lookup = {}
    for doc in all_documents:
        key = f"{doc.student.id}_{doc.document_type.id}"
        document_lookup[key] = doc
    
    # For debugging
    print(f"Found {len(document_lookup)} documents for {len(student_ids)} students")
    for key, doc in document_lookup.items():
        print(f"Document mapping: {key} -> {doc.student.first_name} {doc.student.last_name} - {doc.document_type.name}")
    
    context = {
        'document_types': document_types,
        'students': students,
        'document_lookup': document_lookup,
        'search_query': search_query,
    }
    
    return render(request, 'documents/document_matrix.html', context)

# Student Document CRUD Views
@login_required
@user_passes_test(is_admin)
def upload_document_view(request, student_id, doc_type_id):
    """
    View to upload a new document for a student
    """
    student = get_object_or_404(Student, id=student_id)
    document_type = get_object_or_404(DocumentType, id=doc_type_id, active=True)
    
    # Check if document already exists
    existing_doc = StudentDocument.objects.filter(student=student, document_type=document_type).first()
    if existing_doc:
        messages.warning(request, f'A {document_type.name} document already exists for {student.first_name}. Please update it instead.')
        return redirect('documents:document_matrix')
    
    if request.method == 'POST':
        form = StudentDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.student = student
            document.document_type = document_type
            document.uploaded_by = request.user
            document.save()
            
            # Verify the document was saved correctly
            saved_doc = StudentDocument.objects.filter(student=student, document_type=document_type).first()
            if saved_doc:
                print(f"Successfully saved document: ID {saved_doc.id}, {student.first_name} {student.last_name} - {document_type.name}")
            else:
                print(f"WARNING: Document save operation reported success but document not found in database.")
                
            messages.success(request, f'{document_type.name} uploaded successfully for {student.first_name} {student.last_name}')
            
            # Use HttpResponseRedirect instead of redirect to avoid potential caching issues
            return HttpResponseRedirect(reverse('documents:document_matrix') + '?refresh=' + str(document.id))
    else:
        form = StudentDocumentForm()
    
    context = {
        'form': form,
        'student': student,
        'document_type': document_type,
        'is_update': False,
    }
    
    return render(request, 'documents/upload_document.html', context)

@login_required
@user_passes_test(is_admin)
def update_document_view(request, document_id):
    """
    View to update an existing document
    """
    document = get_object_or_404(StudentDocument, id=document_id)
    
    if request.method == 'POST':
        form = StudentDocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            updated_doc = form.save(commit=False)
            updated_doc.uploaded_by = request.user
            updated_doc.save()
            messages.success(request, f'Document updated successfully for {document.student.first_name} {document.student.last_name}')
            return HttpResponseRedirect(reverse('documents:document_matrix') + '?refresh=' + str(document.id))
    else:
        form = StudentDocumentForm(instance=document)
    
    context = {
        'form': form,
        'student': document.student,
        'document_type': document.document_type,
        'document': document,
        'is_update': True,
    }
    
    return render(request, 'documents/upload_document.html', context)

@login_required
@user_passes_test(is_admin)
def view_document_view(request, document_id):
    """
    View to display a document with options to download, update, or delete
    """
    document = get_object_or_404(StudentDocument, id=document_id)
    
    context = {
        'document': document,
    }
    
    return render(request, 'documents/view_document.html', context)

@login_required
@user_passes_test(is_admin)
def download_document_view(request, document_id):
    """
    View to download a document
    """
    document = get_object_or_404(StudentDocument, id=document_id)
    
    try:
        # Open the file in binary mode
        file_path = document.file.path
        response = FileResponse(open(file_path, 'rb'))
        # Set the Content-Disposition header to force download
        filename = document.filename()
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        messages.error(request, f'Error downloading file: {str(e)}')
        return redirect('documents:view_document', document_id=document_id)

@login_required
@user_passes_test(is_admin)
def delete_document_view(request, document_id):
    """
    View to delete a document with confirmation
    """
    document = get_object_or_404(StudentDocument, id=document_id)
    
    if request.method == 'POST':
        student_name = f"{document.student.first_name} {document.student.last_name}"
        document_type_name = document.document_type.name
        student_id = document.student.id  # Save before deletion
        document.file.delete(save=False)  # Delete the file from storage
        document.delete()  # Delete the database record
        messages.success(request, f'{document_type_name} for {student_name} has been deleted.')
        return HttpResponseRedirect(reverse('documents:document_matrix') + '?refresh=' + str(student_id))
    
    context = {
        'document': document,
    }
    
    return render(request, 'documents/delete_document.html', context)

@login_required
@user_passes_test(is_admin)
def search_documents_view(request):
    """
    View to search for documents
    """
    query = request.GET.get('q', '')
    
    if query:
        # Search for students matching the query
        students = Student.objects.filter(
            models.Q(first_name__icontains=query) | 
            models.Q(last_name__icontains=query) |
            models.Q(email__icontains=query) |
            models.Q(student_id__icontains=query)
        )
        
        # Get document types that match the query
        doc_types = DocumentType.objects.filter(name__icontains=query)
        
        # Get documents for those students or document types
        documents_list = StudentDocument.objects.filter(
            models.Q(student__in=students) |
            models.Q(document_type__in=doc_types) |
            models.Q(notes__icontains=query)
        ).select_related('student', 'document_type').order_by('-updated_at')
    else:
        documents_list = StudentDocument.objects.none()
    
    # Paginate documents list - display 20 documents per page
    page = request.GET.get('page', 1)
    paginator = Paginator(documents_list, 20)
    
    try:
        documents = paginator.page(page)
    except PageNotAnInteger:
        documents = paginator.page(1)
    except EmptyPage:
        documents = paginator.page(paginator.num_pages)
    
    context = {
        'documents': documents,
        'query': query,
    }
    
    return render(request, 'documents/search_documents.html', context)

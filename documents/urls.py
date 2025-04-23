from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # Document Types CRUD
    path('types/', views.DocumentTypeListView.as_view(), name='document_type_list'),
    path('types/create/', views.DocumentTypeCreateView.as_view(), name='document_type_create'),
    path('types/<int:pk>/update/', views.DocumentTypeUpdateView.as_view(), name='document_type_update'),
    path('types/<int:pk>/delete/', views.DocumentTypeDeleteView.as_view(), name='document_type_delete'),
    
    # Document Matrix
    path('', views.document_matrix_view, name='document_matrix'),
    path('search/', views.search_documents_view, name='search_documents'),
    
    # Student Documents CRUD
    path('upload/<int:student_id>/<int:doc_type_id>/', views.upload_document_view, name='upload_document'),
    path('update/<int:document_id>/', views.update_document_view, name='update_document'),
    path('view/<int:document_id>/', views.view_document_view, name='view_document'),
    path('download/<int:document_id>/', views.download_document_view, name='download_document'),
    path('delete/<int:document_id>/', views.delete_document_view, name='delete_document'),
] 
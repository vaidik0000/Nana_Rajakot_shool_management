# school_subjects/api/views.py

from rest_framework import viewsets
from subjects.models import Subject
from .serializers import SubjectSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class SubjectReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subject.objects.filter(is_active=True)
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

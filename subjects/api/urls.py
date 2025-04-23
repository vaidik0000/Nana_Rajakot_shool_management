# school_subjects/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubjectReadOnlyViewSet

router = DefaultRouter()
router.register(r'subjects', SubjectReadOnlyViewSet, basename='subject')

urlpatterns = [
    path('', include(router.urls)),
]

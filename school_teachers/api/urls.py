# school_teachers/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeacherViewSet
from . import views

router = DefaultRouter()
router.register(r'', TeacherViewSet, basename='teachers')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', views.TeacherSearchAPIView.as_view(), name='teacher_search_api'),
    path('schedule/<int:teacher_id>/', views.TeacherScheduleAPIView.as_view(), name='teacher_schedule_api'),
]

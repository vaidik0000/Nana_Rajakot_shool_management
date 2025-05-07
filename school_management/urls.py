from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Define URL patterns for the application
urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Main app URLs
    path('', include('core.urls')),
    path('teachers/', include('school_teachers.urls')),
    path('students/', include('students.urls')),
    path('subjects/', include('subjects.urls')),
    path('events/', include('events.urls')),
    path('timetable/', include('timetable.urls')),
    path('library/', include('library.urls')),
    path('attendance/', include('attendance.urls')),
    path('fees/', include('fees.urls')),
    path('documents/', include('documents.urls', namespace='documents')),

    # API endpoints
    path('api/', include('students.api.urls')),
    path('api/teachers/', include('school_teachers.api.urls')),
    path('api/token-auth/', obtain_auth_token),
    path('api/subjects/', include('subjects.api.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/library/', include('library.api.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

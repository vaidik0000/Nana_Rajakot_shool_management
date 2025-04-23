from django.utils.deprecation import MiddlewareMixin
from school_teachers.models import Teacher
from students.models import Student
from django.contrib.auth.models import User
import logging

# Create a logger for tracking user type detection
logger = logging.getLogger('user_type')

class UserTypeMiddleware(MiddlewareMixin):
    """
    Middleware to check if a user is a teacher or student and add that information to the request.
    """
    def process_request(self, request):
        # Always add an empty user_type field to prevent errors with anonymous users
        request.user_type = None
        request.student = None
        request.teacher = None
        
        if request.user.is_authenticated:
            # Debug user login
            print(f"[UserTypeMiddleware] Processing user {request.user.username}")
            
            # Refresh user to ensure permissions are up to date
            request.user.refresh_from_db()
            
            # Add user type information to request
            try:
                # Check if user is a teacher
                teacher = Teacher.objects.get(user=request.user)
                request.user_type = 'teacher'
                request.teacher = teacher
                print(f"[UserTypeMiddleware] User {request.user.username} identified as teacher: {teacher.first_name} {teacher.last_name}")
            except Teacher.DoesNotExist:
                # Not a teacher, check if it's a student
                try:
                    # First try to get student by user relationship
                    student = Student.objects.get(user=request.user)
                    request.user_type = 'student'
                    request.student = student
                    print(f"[UserTypeMiddleware] User {request.user.username} identified as student: {student.first_name} {student.last_name}")
                    
                    # Debug: Check for permissions
                    permissions = list(request.user.get_all_permissions())
                    direct_permissions = [f"{p.content_type.app_label}.{p.codename}" for p in request.user.user_permissions.all()]
                    print(f"[UserTypeMiddleware] Student permissions (direct only): {direct_permissions}")
                except Student.DoesNotExist:
                    # If not found by user, try by email
                    try:
                        # Since students might not have direct user relationship yet,
                        # try to match by email
                        student = Student.objects.get(email=request.user.email)
                        request.user_type = 'student'
                        request.student = student
                        print(f"[UserTypeMiddleware] User {request.user.username} matched by email to student: {student.first_name} {student.last_name}")
                        
                        # Update the user relationship if it's missing
                        if not student.user:
                            student.user = request.user
                            student.save()
                            print(f"[UserTypeMiddleware] Updated student {student.id} with user {request.user.id}")
                    except Student.DoesNotExist:
                        # Neither teacher nor student
                        request.user_type = 'admin'
                        print(f"[UserTypeMiddleware] User {request.user.username} identified as admin")
        else:
            print("[UserTypeMiddleware] No authenticated user")
        
        return None 
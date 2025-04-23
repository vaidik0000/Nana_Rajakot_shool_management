from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from django.http import HttpResponseForbidden

def teacher_required(view_func):
    """
    Decorator for views that checks that the user is a teacher.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if hasattr(request, 'user_type') and request.user_type == 'teacher':
                return view_func(request, *args, **kwargs)
            elif hasattr(request, 'user_type') and request.user_type == 'student':
                messages.error(request, "Students do not have permission to access this page.")
                return redirect('core:home')
            # Admin users (staff/superusers) should have full access
            elif request.user.is_staff or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
        # For unauthenticated users, redirect to login
        messages.error(request, "You need to be logged in as a teacher to access this page.")
        return redirect('core:login')
    return _wrapped_view

def student_required(view_func):
    """
    Decorator for views that checks that the user is a student.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if hasattr(request, 'user_type') and (request.user_type == 'student' or request.user_type == 'teacher'):
                return view_func(request, *args, **kwargs)
            # Admin users (staff/superusers) should have full access
            elif request.user.is_staff or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
        # For unauthenticated users, redirect to login
        messages.error(request, "You need to be logged in as a student to access this page.")
        return redirect('core:login')
    return _wrapped_view

def admin_required(view_func):
    """
    Decorator for views that checks that the user is an admin (staff/superuser).
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return view_func(request, *args, **kwargs)
        # For non-admin users, show access denied
        messages.error(request, "You don't have permission to access this page.")
        return redirect('core:home')
    return _wrapped_view

def new_user_restricted(view_func):
    """
    Decorator that prevents newly registered users from accessing certain
    management functions like event creation, library management, and attendance control.
    Only teachers, students, staff, and superusers can access these features.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            # Allow access if user is a recognized role (teacher, student) or admin
            if hasattr(request, 'user_type') and request.user_type in ['teacher', 'student']:
                return view_func(request, *args, **kwargs)
            elif request.user.is_staff or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                # Regular newly registered users without specific roles are restricted
                messages.error(request, "Your account hasn't been assigned appropriate permissions yet. Please contact an administrator.")
                return redirect('core:home')
        # For unauthenticated users, redirect to login
        messages.error(request, "You need to log in to access this page.")
        return redirect('core:login')
    return _wrapped_view 
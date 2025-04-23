from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('home/', login_required(views.home), name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('verify-signup-otp/', views.verify_signup_otp, name='verify_signup_otp'),
    path('logout/', LogoutView.as_view(next_page='core:login'), name='logout'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('verify-otp/<str:email>/', views.verify_otp, name='verify_otp'),
    path('set-new-password/', views.set_new_password, name='set_new_password'),
    
    # User permissions management
    path('permissions/', login_required(views.user_permissions), name='user_permissions'),
    path('permissions/update/<int:user_id>/', login_required(views.update_user_permissions), name='update_user_permissions'),
    
    # Debug tools
    path('debug/permissions/', login_required(views.debug_permissions), name='debug_permissions'),
    
    # API endpoints
    path('api/attendance/', login_required(views.attendance_data_api), name='attendance_data_api'),
] 
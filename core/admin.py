from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile

# Define an inline admin descriptor for Profile model
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profiles'

# Unregister the default User admin
admin.site.unregister(User)

# Register the User model with the Profile inline
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'picture')  # Display the user and picture fields in the admin list view
    search_fields = ('user__username', 'user__email')  # Allow searching by username and email

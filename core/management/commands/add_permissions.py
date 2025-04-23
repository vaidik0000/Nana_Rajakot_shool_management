from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from library.models import Book

class Command(BaseCommand):
    help = 'Add specific permissions to a user directly'
    
    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to give permissions to')
        parser.add_argument('--action', type=str, default='add', choices=['add', 'remove', 'list'], 
                           help='Action to perform')
    
    def handle(self, *args, **options):
        username = options['username']
        action = options['action']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} not found'))
            return
        
        # Get the content type for Book model
        book_content_type = ContentType.objects.get_for_model(Book)
        
        # Get all book permissions
        book_permissions = Permission.objects.filter(content_type=book_content_type)
        
        if action == 'list':
            self.stdout.write(self.style.SUCCESS(f'User {username} has these permissions:'))
            for perm in user.user_permissions.all():
                self.stdout.write(f"- {perm.content_type.app_label}.{perm.codename}")
            return
            
        if action == 'add':
            # Add all book permissions to the user
            for perm in book_permissions:
                user.user_permissions.add(perm)
                self.stdout.write(f"Added permission: {perm.content_type.app_label}.{perm.codename}")
            
            # Force refresh permissions cache
            user = User.objects.get(pk=user.pk)
            self.stdout.write(self.style.SUCCESS(f'Added library book permissions to {username}'))
        
        elif action == 'remove':
            # Remove all book permissions
            for perm in book_permissions:
                user.user_permissions.remove(perm)
                self.stdout.write(f"Removed permission: {perm.content_type.app_label}.{perm.codename}")
            
            # Force refresh permissions cache
            user = User.objects.get(pk=user.pk)
            self.stdout.write(self.style.SUCCESS(f'Removed library book permissions from {username}')) 
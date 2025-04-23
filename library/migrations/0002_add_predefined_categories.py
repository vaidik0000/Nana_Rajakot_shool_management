from django.db import migrations

def add_predefined_categories(apps, schema_editor):
    BookCategory = apps.get_model('library', 'BookCategory')
    
    categories = [
        ('romance', 'Romance'),
        ('scifi_fantasy', 'Sci-Fi/Fantasy'),
        ('action_adventure', 'Action Adventure/Thriller'),
        ('mystery', 'Mystery'),
        ('horror', 'Horror/Dystopian'),
        ('children', "Children's"),
    ]
    
    for code, name in categories:
        BookCategory.objects.get_or_create(
            name=code,
            defaults={'description': f'Books in the {name} category'}
        )

def remove_predefined_categories(apps, schema_editor):
    BookCategory = apps.get_model('library', 'BookCategory')
    BookCategory.objects.filter(name__in=[
        'romance', 'scifi_fantasy', 'action_adventure', 
        'mystery', 'horror', 'children'
    ]).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            add_predefined_categories,
            remove_predefined_categories
        ),
    ] 
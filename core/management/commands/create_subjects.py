from django.core.management.base import BaseCommand
from django.utils import timezone
from subjects.models import Subject
from school_teachers.models import Teacher
import random

class Command(BaseCommand):
    help = 'Creates sample subjects and assigns teachers'
    
    def handle(self, *args, **options):
        # Sample subjects
        subjects_data = [
            {'name': 'Mathematics', 'code': 'MATH101', 'credits': 5, 'description': 'Basic mathematics including algebra, geometry, and arithmetic'},
            {'name': 'English', 'code': 'ENG101', 'credits': 4, 'description': 'English language and literature'},
            {'name': 'Science', 'code': 'SCI101', 'credits': 5, 'description': 'General science covering physics, chemistry, and biology basics'},
            {'name': 'Social Studies', 'code': 'SOC101', 'credits': 4, 'description': 'History, geography, and civics'},
            {'name': 'Computer Science', 'code': 'CS101', 'credits': 3, 'description': 'Introduction to computers and basic programming'},
            {'name': 'Physical Education', 'code': 'PE101', 'credits': 2, 'description': 'Physical fitness and sports activities'},
            {'name': 'Art', 'code': 'ART101', 'credits': 2, 'description': 'Visual arts, painting, and drawing'},
            {'name': 'Music', 'code': 'MUS101', 'credits': 2, 'description': 'Music theory and practical lessons'},
            {'name': 'Geography', 'code': 'GEO101', 'credits': 3, 'description': 'Study of Earth features and human interactions'},
            {'name': 'History', 'code': 'HIS101', 'credits': 3, 'description': 'Study of past events and human civilizations'}
        ]
        
        # Get available teachers
        teachers = list(Teacher.objects.all())
        
        if not teachers:
            self.stdout.write(self.style.ERROR("No teachers found. Please create teachers first."))
            return
        
        # Create subjects
        created_count = 0
        for subject_data in subjects_data:
            # Skip if already exists
            if Subject.objects.filter(code=subject_data['code']).exists():
                self.stdout.write(f"Subject with code {subject_data['code']} already exists, skipping")
                continue
            
            # Assign a random teacher
            teacher = random.choice(teachers)
            
            # Create subject
            subject = Subject(
                name=subject_data['name'],
                code=subject_data['code'],
                description=subject_data['description'],
                teacher=teacher,
                credits=subject_data['credits'],
                is_active=True
            )
            subject.save()
            created_count += 1
            
        self.stdout.write(self.style.SUCCESS(f"Successfully created {created_count} subjects")) 
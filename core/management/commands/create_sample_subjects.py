from django.core.management.base import BaseCommand
from subjects.models import Subject
from school_teachers.models import Teacher
import random

class Command(BaseCommand):
    help = 'Create sample subjects for the school management system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of subjects to create (default: 10)',
        )

    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(f'Creating {count} sample subjects...')
        
        # Check if we have teachers in the system
        teachers = list(Teacher.objects.filter(is_active=True))
        if not teachers:
            self.stdout.write(self.style.WARNING('No active teachers found. Some subjects will not have teachers assigned.'))
        
        # List of sample subjects with their codes and descriptions
        sample_subjects = [
            {
                'name': 'Mathematics',
                'code': 'MATH101',
                'description': 'Introduction to mathematics including algebra, geometry, and basic calculus.',
                'credits': 4
            },
            {
                'name': 'Science',
                'code': 'SCI101',
                'description': 'General science course covering physics, chemistry, and biology basics.',
                'credits': 4
            },
            {
                'name': 'English',
                'code': 'ENG101',
                'description': 'English language and literature course focusing on reading, writing, and comprehension.',
                'credits': 3
            },
            {
                'name': 'History',
                'code': 'HIST101',
                'description': 'Introduction to world history and important historical events.',
                'credits': 3
            },
            {
                'name': 'Geography',
                'code': 'GEO101',
                'description': 'Study of earth, its features, and the distribution of life on earth including human life and the impact of human activities.',
                'credits': 3
            },
            {
                'name': 'Computer Science',
                'code': 'CS101',
                'description': 'Introduction to computer science, programming, and computational thinking.',
                'credits': 4
            },
            {
                'name': 'Physical Education',
                'code': 'PE101',
                'description': 'Physical fitness, sports, and health education.',
                'credits': 2
            },
            {
                'name': 'Art',
                'code': 'ART101',
                'description': 'Visual arts, drawing, painting, and art appreciation.',
                'credits': 2
            },
            {
                'name': 'Music',
                'code': 'MUS101',
                'description': 'Music theory, appreciation, and basic instrumental skills.',
                'credits': 2
            },
            {
                'name': 'Social Studies',
                'code': 'SOC101',
                'description': 'Study of human society, social relationships, and institutions.',
                'credits': 3
            },
            {
                'name': 'Physics',
                'code': 'PHYS201',
                'description': 'Advanced study of matter, energy, and their interactions.',
                'credits': 4
            },
            {
                'name': 'Chemistry',
                'code': 'CHEM201',
                'description': 'Study of the composition, structure, properties, and change of matter.',
                'credits': 4
            },
            {
                'name': 'Biology',
                'code': 'BIO201',
                'description': 'Study of living organisms and their interactions with each other and the environment.',
                'credits': 4
            },
            {
                'name': 'Environmental Science',
                'code': 'ENV201',
                'description': 'Study of environmental systems and how humans interact with the environment.',
                'credits': 3
            },
            {
                'name': 'Economics',
                'code': 'ECON201',
                'description': 'Study of production, consumption, and transfer of wealth.',
                'credits': 3
            },
            {
                'name': 'Psychology',
                'code': 'PSYCH201',
                'description': 'Study of mind and behavior, including consciousness, perception, intelligence, cognition, emotions, and personality.',
                'credits': 3
            },
            {
                'name': 'Foreign Language',
                'code': 'LANG201',
                'description': 'Study of a foreign language and its culture.',
                'credits': 3
            },
            {
                'name': 'Literature',
                'code': 'LIT201',
                'description': 'Advanced study of literary works, authors, and literary analysis.',
                'credits': 3
            },
            {
                'name': 'Advanced Mathematics',
                'code': 'MATH301',
                'description': 'Advanced topics in mathematics including calculus, statistics, and discrete mathematics.',
                'credits': 4
            },
            {
                'name': 'Computer Programming',
                'code': 'CS301',
                'description': 'Advanced programming concepts, algorithms, and software development.',
                'credits': 4
            }
        ]
        
        # Ensure we're not trying to create more subjects than we have in our sample list
        if count > len(sample_subjects):
            count = len(sample_subjects)
            self.stdout.write(self.style.WARNING(f'Limiting to {count} subjects (maximum in sample data)'))
        
        # Randomly select 'count' subjects from the sample list
        selected_subjects = random.sample(sample_subjects, count)
        
        # Track created and skipped subjects
        created_count = 0
        skipped_count = 0
        
        # Create subjects
        for subject_data in selected_subjects:
            # Check if subject with this code already exists
            if Subject.objects.filter(code=subject_data['code']).exists():
                self.stdout.write(f"Subject with code {subject_data['code']} already exists. Skipping.")
                skipped_count += 1
                continue
            
            # Assign a random teacher if available
            teacher = random.choice(teachers) if teachers else None
            
            # Create the subject
            subject = Subject.objects.create(
                name=subject_data['name'],
                code=subject_data['code'],
                description=subject_data['description'],
                teacher=teacher,
                credits=subject_data['credits'],
                is_active=True
            )
            
            self.stdout.write(self.style.SUCCESS(
                f"Created subject: {subject.name} ({subject.code})" + 
                (f" - Teacher: {teacher.first_name} {teacher.last_name}" if teacher else " - No teacher assigned")
            ))
            created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} subjects ({skipped_count} skipped)')) 
from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Event
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Creates sample school events'
    
    def handle(self, *args, **options):
        # Sample events
        events_data = [
            {
                'title': 'Annual Sports Day',
                'description': 'Annual sports competition with various track and field events, team sports, and individual competitions for all classes.',
                'event_type': 'sports',
                'location': 'School Playground'
            },
            {
                'title': 'Science Exhibition',
                'description': 'Students showcase science projects and experiments they have been working on throughout the term.',
                'event_type': 'academic',
                'location': 'School Auditorium'
            },
            {
                'title': 'Parent-Teacher Meeting',
                'description': 'Quarterly meeting where parents can meet with teachers to discuss student progress.',
                'event_type': 'academic',
                'location': 'School Classrooms'
            },
            {
                'title': 'Cultural Festival',
                'description': 'Annual cultural festival featuring music, dance, drama, and other cultural performances by students.',
                'event_type': 'cultural',
                'location': 'School Auditorium and Grounds'
            },
            {
                'title': 'Independence Day Celebration',
                'description': 'Celebration of national independence with flag hoisting, patriotic songs, and cultural programs.',
                'event_type': 'cultural',
                'location': 'School Assembly Ground'
            },
            {
                'title': 'Math Olympiad',
                'description': 'Mathematics competition for students to test their problem-solving abilities and mathematical skills.',
                'event_type': 'academic',
                'location': 'School Classrooms'
            },
            {
                'title': 'Annual Day',
                'description': 'School annual day celebration with performances, awards, and recognition of achievements.',
                'event_type': 'cultural',
                'location': 'School Auditorium'
            },
            {
                'title': 'Literary Week',
                'description': 'Week-long event with debates, quizzes, elocution contests, and other literary activities.',
                'event_type': 'academic',
                'location': 'School Library and Classrooms'
            },
            {
                'title': 'Cricket Tournament',
                'description': 'Inter-class cricket tournament for students of all age groups.',
                'event_type': 'sports',
                'location': 'School Cricket Ground'
            },
            {
                'title': 'Diwali Holiday',
                'description': 'School closure for Diwali festival celebrations.',
                'event_type': 'holiday',
                'location': 'N/A'
            }
        ]
        
        # Create events with randomized dates
        today = timezone.now().date()
        created_count = 0
        
        for event_data in events_data:
            # Generate random date within 6 months (past and future)
            days_delta = random.randint(-90, 90)  # Between 3 months past and 3 months future
            start_date = today + timedelta(days=days_delta)
            
            # If event is in the past, make sure it already ended
            if days_delta < 0:
                end_date = start_date + timedelta(days=random.randint(1, 3))
            else:  # Future event
                end_date = start_date + timedelta(days=random.randint(1, 5))
            
            # Skip if similar event already exists (by title and dates close to each other)
            existing_events = Event.objects.filter(title=event_data['title'])
            if existing_events.exists():
                skip = False
                for existing_event in existing_events:
                    # If dates are within 2 weeks of each other, consider it a duplicate
                    if abs((existing_event.start_date - start_date).days) < 14:
                        skip = True
                        break
                
                if skip:
                    self.stdout.write(f"Similar event to '{event_data['title']}' already exists, skipping")
                    continue
            
            # Create event
            event = Event(
                title=event_data['title'],
                description=event_data['description'],
                event_type=event_data['event_type'],
                start_date=start_date,
                end_date=end_date,
                location=event_data['location'],
                is_all_day=random.choice([True, False]),
            )
            event.save()
            created_count += 1
            
        self.stdout.write(self.style.SUCCESS(f"Successfully created {created_count} school events")) 
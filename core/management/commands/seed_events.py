from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Event
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Seeds the database with demo school events'
    
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating demo events...'))
        
        # Get today's date for reference
        today = date.today()
        
        # Create a list of demo events
        demo_events = [
            # Past events
            {
                'title': 'Annual Science Fair',
                'description': 'Students from all classes will present their science projects. Parents are invited to attend and see the innovative work of our students.',
                'event_type': 'academic',
                'start_date': today - timedelta(days=30),
                'end_date': today - timedelta(days=29),
                'location': 'School Auditorium',
                'is_all_day': True
            },
            {
                'title': 'Parent-Teacher Meeting',
                'description': 'Quarterly parent-teacher meeting to discuss student progress and address any concerns.',
                'event_type': 'academic',
                'start_date': today - timedelta(days=15),
                'end_date': today - timedelta(days=15),
                'location': 'Respective Classrooms',
                'is_all_day': False
            },
            
            # Current/Ongoing events
            {
                'title': 'Book Week',
                'description': 'A week-long celebration of reading with special activities, book exchanges, and guest author visits.',
                'event_type': 'academic',
                'start_date': today - timedelta(days=2),
                'end_date': today + timedelta(days=5),
                'location': 'School Library and Classrooms',
                'is_all_day': True
            },
            
            # Upcoming events
            {
                'title': 'Annual Sports Day',
                'description': 'Our annual sports event featuring track and field competitions, team sports, and awards ceremony. All students are expected to participate in at least one event.',
                'event_type': 'sports',
                'start_date': today + timedelta(days=15),
                'end_date': today + timedelta(days=16),
                'location': 'School Playground',
                'is_all_day': True
            },
            {
                'title': 'Mathematics Olympiad',
                'description': 'Inter-school mathematics competition for talented students. Winners will represent the school at the national level.',
                'event_type': 'academic',
                'start_date': today + timedelta(days=25),
                'end_date': today + timedelta(days=25),
                'location': 'School Auditorium',
                'is_all_day': False
            },
            {
                'title': 'Cultural Festival',
                'description': 'Annual cultural festival celebrating diversity with music, dance, art, and food from different cultures. Parents and community members are welcome to attend.',
                'event_type': 'cultural',
                'start_date': today + timedelta(days=45),
                'end_date': today + timedelta(days=47),
                'location': 'School Grounds',
                'is_all_day': True
            },
            {
                'title': 'Summer Break',
                'description': 'School will be closed for summer vacation. Classes will resume according to the academic calendar.',
                'event_type': 'holiday',
                'start_date': today + timedelta(days=60),
                'end_date': today + timedelta(days=90),
                'location': '',
                'is_all_day': True
            },
            {
                'title': 'Career Guidance Workshop',
                'description': 'Workshop for senior students with career counselors and professionals from various fields to help with future career planning.',
                'event_type': 'academic',
                'start_date': today + timedelta(days=10),
                'end_date': today + timedelta(days=10),
                'location': 'Conference Hall',
                'is_all_day': False
            },
            {
                'title': 'Independence Day Celebration',
                'description': 'Special assembly and cultural program to celebrate Independence Day. Flag hoisting ceremony will begin at 8:00 AM.',
                'event_type': 'cultural',
                'start_date': today + timedelta(days=20),
                'end_date': today + timedelta(days=20),
                'location': 'School Assembly Ground',
                'is_all_day': False
            },
            {
                'title': 'Inter-House Chess Tournament',
                'description': 'Annual chess competition between house teams. Students of all age groups can participate based on their skill level.',
                'event_type': 'sports',
                'start_date': today + timedelta(days=30),
                'end_date': today + timedelta(days=32),
                'location': 'Recreation Room',
                'is_all_day': False
            }
        ]
        
        # Create events in database
        events_created = 0
        for event_data in demo_events:
            event, created = Event.objects.get_or_create(
                title=event_data['title'],
                defaults={
                    'description': event_data['description'],
                    'event_type': event_data['event_type'],
                    'start_date': event_data['start_date'],
                    'end_date': event_data['end_date'],
                    'location': event_data['location'],
                    'is_all_day': event_data['is_all_day']
                }
            )
            if created:
                events_created += 1
                self.stdout.write(f"Created event: {event.title}")
            else:
                self.stdout.write(f"Event already exists: {event.title}")
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {events_created} demo events!')) 
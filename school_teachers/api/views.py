# school_teachers/api/views.py

from rest_framework import viewsets
from school_teachers.models import Teacher
from .serializers import TeacherSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]  
    search_fields = ['first_name', 'last_name', 'specialization', 'email']

class TeacherSearchAPIView(APIView):
    """
    API endpoint for searching teachers by name
    Used by the chatbot to find teacher details
    """
    def get(self, request):
        name = request.GET.get('name', '')
        
        if not name:
            return Response({
                'found': False,
                'message': 'No search term provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Split the name to search in both first_name and last_name
        name_parts = name.split()
        
        query = Q()
        for part in name_parts:
            query |= Q(first_name__icontains=part) | Q(last_name__icontains=part)
        
        teachers = Teacher.objects.filter(query)
        
        if teachers.exists():
            serializer = TeacherSerializer(teachers, many=True)
            return Response({
                'found': True,
                'teachers': serializer.data,
                'count': teachers.count()
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'found': False,
                'message': 'No teachers found matching the search term'
            }, status=status.HTTP_404_NOT_FOUND)

class TeacherScheduleAPIView(APIView):
    """
    API endpoint for retrieving a teacher's schedule
    """
    def get(self, request, teacher_id):
        try:
            teacher = Teacher.objects.get(id=teacher_id)
            
            # Get schedule
            # This is a placeholder - you should connect to your actual schedule model
            # For example: schedule = Schedule.objects.filter(teacher=teacher)
            
            # For now, returning demo data
            schedule_data = {
                'teacher_id': teacher_id,
                'teacher_name': f"{teacher.first_name} {teacher.last_name}",
                'subject': teacher.subject.name if hasattr(teacher, 'subject') and teacher.subject else "Not assigned",
                'classes_taught': [
                    {'day': 'Monday', 'periods': ['10A - Period 1', '11B - Period 3', '9C - Period 5']},
                    {'day': 'Tuesday', 'periods': ['11A - Period 2', '10B - Period 4', '9A - Period 6']},
                    {'day': 'Wednesday', 'periods': ['10A - Period 2', '11C - Period 5', '9B - Period 6']},
                    {'day': 'Thursday', 'periods': ['11B - Period 1', '10C - Period 3', '9C - Period 4']},
                    {'day': 'Friday', 'periods': ['10B - Period 2', '11A - Period 5', '9A - Period 6']}
                ]
            }
            
            return Response(schedule_data, status=status.HTTP_200_OK)
            
        except Teacher.DoesNotExist:
            return Response({
                'detail': 'Teacher not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
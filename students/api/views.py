from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from students.models import Student
from .serializers import StudentSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.db.models import Q


class StudentListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        students = Student.objects.all()

        # Filtering by query parameters
        class_name = request.query_params.get('class_name')
        gender = request.query_params.get('gender')
        is_active = request.query_params.get('is_active')

        if class_name:
            students = students.filter(class_name=class_name)
        if gender:
            students = students.filter(gender=gender)
        if is_active is not None:
            students = students.filter(is_active=is_active.lower() == 'true')

        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Student, pk=pk)

    def get(self, request, pk):
        student = self.get_object(pk)
        serializer = StudentSerializer(student)
        return Response(serializer.data)

    def put(self, request, pk):
        student = self.get_object(pk)
        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        student = self.get_object(pk)
        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StudentSearchAPIView(APIView):
    """
    API endpoint for searching students by name
    Used by the chatbot to find student details
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
        
        students = Student.objects.filter(query)
        
        if students.exists():
            serializer = StudentSerializer(students, many=True)
            return Response({
                'found': True,
                'students': serializer.data,
                'count': students.count()
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'found': False,
                'message': 'No students found matching the search term'
            }, status=status.HTTP_404_NOT_FOUND)


class StudentAttendanceAPIView(APIView):
    """
    API endpoint for retrieving a student's attendance records
    """
    def get(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
            
            # Get attendance records
            # This is a placeholder - you should connect to your actual attendance model
            # For example: attendance_records = Attendance.objects.filter(student=student)
            
            # For now, returning demo data
            attendance_data = {
                'student_id': student_id,
                'student_name': f"{student.first_name} {student.last_name}",
                'overall_percentage': '92%',
                'present_days': 85,
                'absent_days': 7,
                'late_days': 3,
                'total_days': 95
            }
            
            return Response(attendance_data, status=status.HTTP_200_OK)
            
        except Student.DoesNotExist:
            return Response({
                'detail': 'Student not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

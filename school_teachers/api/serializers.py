# school_teachers/api/serializers.py

from rest_framework import serializers
from school_teachers.models import Teacher

class TeacherSerializer(serializers.ModelSerializer):
    subject = serializers.SerializerMethodField()
    qualification = serializers.SerializerMethodField()
    experience = serializers.SerializerMethodField()
    classes_taught = serializers.SerializerMethodField()
    
    class Meta:
        model = Teacher
        fields = [
            'id', 'first_name', 'last_name', 'employee_id', 'subject',
            'qualification', 'experience', 'email', 'phone', 'address',
            'joining_date', 'classes_taught'
        ]
    
    def get_subject(self, obj):
        # Return subject name if the teacher has a subject assigned
        if hasattr(obj, 'subject') and obj.subject:
            return obj.subject.name
        return "Not assigned"
    
    def get_qualification(self, obj):
        # Return teacher's qualification
        if hasattr(obj, 'qualification') and obj.qualification:
            return obj.qualification
        return "Not available"
    
    def get_experience(self, obj):
        # Return teacher's experience
        if hasattr(obj, 'experience') and obj.experience:
            return f"{obj.experience} years"
        return "Not available"
    
    def get_classes_taught(self, obj):
        # Return classes taught by the teacher
        # This is a placeholder - in a real app you'd query the class/timetable models
        try:
            # Example of how you might fetch real data:
            # classes = Class.objects.filter(teachers=obj)
            # return [f"{cls.standard} {cls.section}" for cls in classes]
            
            # For demo purposes, return placeholder values
            return ["10A", "11B", "9C"]
        except:
            return []

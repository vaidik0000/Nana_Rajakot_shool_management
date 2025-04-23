# school_subjects/api/serializers.py

from rest_framework import serializers
from subjects.models import Subject

class SubjectSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'description', 'teacher_name', 'credits', 'is_active', 'created_at', 'updated_at']

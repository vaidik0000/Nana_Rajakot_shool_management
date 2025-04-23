from rest_framework import serializers
from ..models import Student

class StudentSerializer(serializers.ModelSerializer):
    class_name = serializers.SerializerMethodField()
    attendance = serializers.SerializerMethodField()
    fees_status = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'first_name', 'last_name', 'admission_number', 'roll_no',
            'class_name', 'date_of_birth', 'gender', 'email', 'phone',
            'address', 'parent_name', 'attendance', 'fees_status'
        ]
    
    def get_class_name(self, obj):
        # Return class name if the student has a class assigned
        if hasattr(obj, 'student_class') and obj.student_class:
            return f"{obj.student_class.standard} {obj.student_class.section}"
        return "Not assigned"
    
    def get_attendance(self, obj):
        # Get student's attendance percentage
        # This is a placeholder - in a real app you'd calculate from attendance records
        try:
            # You could calculate actual attendance here:
            # attendance_records = Attendance.objects.filter(student=obj)
            # total = attendance_records.count()
            # present = attendance_records.filter(status='present').count()
            # return f"{int((present/total) * 100)}%" if total > 0 else "N/A"
            
            # For demo purposes, return a fixed value
            return "92%"
        except:
            return "Not available"
    
    def get_fees_status(self, obj):
        # Get student's fee payment status
        # This is a placeholder since we don't have a fee payment system 
        try:
            # For demonstration purposes only
            return "Paid"
        except:
            return "Not available"
    
    def get_parent_name(self, obj):
        # Get parent's name if available
        if hasattr(obj, 'parent') and obj.parent:
            return obj.parent.name
        
        # If using a different parent field structure
        parent_fields = ['father_name', 'mother_name', 'guardian_name']
        for field in parent_fields:
            if hasattr(obj, field) and getattr(obj, field):
                return getattr(obj, field)
        
        return "Not available"

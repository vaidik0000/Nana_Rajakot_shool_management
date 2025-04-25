from django.db import models
from django.contrib.auth.models import User
from students.models import Student
from school_teachers.models import Teacher

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    remarks = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recorded_attendances')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'student__first_name']
        unique_together = ['student', 'date']

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.date} - {self.status}"

class TeacherAttendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    remarks = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='teacher_attendance_records')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'teacher__first_name']
        unique_together = ['teacher', 'date']

    def __str__(self):
        return f"{self.teacher.first_name} {self.teacher.last_name} - {self.date} - {self.status}"

class AttendanceReport(models.Model):
    """Model for storing generated attendance reports"""
    date = models.DateField()
    class_name = models.CharField(max_length=10, blank=True, null=True)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, blank=True, null=True)
    
    # Report statistics
    total_students = models.IntegerField(default=0)
    present_count = models.IntegerField(default=0)
    absent_count = models.IntegerField(default=0)
    late_count = models.IntegerField(default=0)
    half_day_count = models.IntegerField(default=0)
    
    # Calculated percentages
    present_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    absent_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    late_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    half_day_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Report metadata
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', 'class_name']
        
    def __str__(self):
        if self.student:
            return f"Attendance Report - {self.student.first_name} {self.student.last_name} - {self.date}"
        else:
            return f"Attendance Report - Class {self.class_name} - {self.date}"
    
    def save(self, *args, **kwargs):
        """Calculate percentages before saving"""
        total = self.total_students if self.total_students > 0 else 1  # Avoid division by zero
        
        self.present_percentage = round((self.present_count / total) * 100, 2)
        self.absent_percentage = round((self.absent_count / total) * 100, 2)
        self.late_percentage = round((self.late_count / total) * 100, 2)
        self.half_day_percentage = round((self.half_day_count / total) * 100, 2)
        
        super().save(*args, **kwargs)

from django.db import models
from school_teachers.models import Teacher
from students.models import Student

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='subjects')
    credits = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'

    def __str__(self):
        return f"{self.name} ({self.code})"

class StudentMark(models.Model):
    GRADE_CHOICES = [
        ('A+', 'A+'),
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E (Fail)'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='student_marks')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='assigned_marks')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, default='E')
    date = models.DateField()
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'student__first_name']
        verbose_name = 'Student Mark'
        verbose_name_plural = 'Student Marks'

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.subject.name} - {self.marks_obtained}/{self.total_marks}"
    
    def save(self, *args, **kwargs):
        # Calculate percentage
        if self.total_marks > 0:
            # Convert to float for the calculation to ensure proper division
            marks_float = float(self.marks_obtained)
            total_float = float(self.total_marks)
            percentage_value = (marks_float / total_float) * 100
            self.percentage = round(percentage_value, 2)
            
            # Determine grade based on percentage
            if self.percentage >= 90:
                self.grade = 'A+'
            elif self.percentage >= 75:
                self.grade = 'A'
            elif self.percentage >= 60:
                self.grade = 'B'
            elif self.percentage >= 50:
                self.grade = 'C'
            elif self.percentage >= 33:
                self.grade = 'D'
            else:
                self.grade = 'E'
        else:
            self.percentage = 0
            self.grade = 'E'
            
        super().save(*args, **kwargs)

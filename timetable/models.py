from django.db import models
from school_teachers.models import Teacher
from subjects.models import Subject

class TimeTable(models.Model):
    DAY_CHOICES = (
        ('sunday', 'Sunday'),
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    )

    CLASS_CHOICES = (
        ('1', 'Class 1'),
        ('2', 'Class 2'),
        ('3', 'Class 3'),
        ('4', 'Class 4'),
        ('5', 'Class 5'),
        ('6', 'Class 6'),
        ('7', 'Class 7'),
        ('8', 'Class 8'),
      

    )

    PERIOD_CHOICES = (
        ('1', '1st Period'),
        ('2', '2nd Period'),
        ('3', '3rd Period'),
        ('4', '4th Period'),
        ('5', '5th Period'),
        ('6', '6th Period'),
        ('7', '7th Period'),
        ('8', '8th Period'),
    )

    class_name = models.CharField(max_length=2, choices=CLASS_CHOICES)
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    period = models.CharField(max_length=2, choices=PERIOD_CHOICES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_class_name_display()} - {self.get_day_display()} - {self.get_period_display()}"

    class Meta:
        ordering = ['class_name', 'day', 'period']
        unique_together = ['class_name', 'day', 'period']  # Ensure no duplicate periods for same class and day

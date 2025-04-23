from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
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

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    roll_number = models.CharField(max_length=20, unique=True)
    class_name = models.CharField(max_length=2, choices=CLASS_CHOICES)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    parent_name = models.CharField(max_length=100)
    parent_phone = models.CharField(max_length=15)
    parent_email = models.EmailField(blank=True, null=True)
    admission_date = models.DateField(auto_now_add=True)
    profile_picture = models.ImageField(upload_to='student_profiles/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Fields for fee management
    fee_status = models.CharField(max_length=20, default='unpaid')
    last_payment_date = models.DateField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.roll_number}"

    # Django automatically provides get_<field_name>_display() methods for fields with choices
    # But we're adding a helper method in case it's used without the django-generated method
    def get_class_name_display(self):
        return dict(self.CLASS_CHOICES).get(self.class_name, self.class_name)
        
    def get_gender_display(self):
        return dict(self.GENDER_CHOICES).get(self.gender, self.gender)
    
    def save(self, *args, **kwargs):
        if not self.user and self.email:
            # Create a user with email as username
            # Check if username already exists
            username = self.email
            user_count = User.objects.filter(username=username).count()
            if user_count > 0:
                # If username exists, append roll number
                username = f"{self.email}_{self.roll_number}"
            
            user = User.objects.create_user(
                username=username,
                email=self.email,
                password=f"student_{self.roll_number}"  # Default password based on roll number
            )
            # Set user as inactive until admin approves
            user.is_active = True
            user.save()
            self.user = user
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['class_name', 'roll_number']

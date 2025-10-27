from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    full_name = models.CharField(max_length=100)
    emp_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
class Leave(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(Profile, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.employee.full_name} - {self.status}"
    
    def __str__(self):
        return f"{self.full_name} ({self.emp_id})"
    




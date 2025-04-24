from django.db import models
from accounts.models import CustomUser as User
from Courses.models import Course
from teacher.models import Instructor

class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="payments")
    amount = models.FloatField()
    method = models.CharField(max_length=50)  
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.status}"



class MonthlyCourseStats(models.Model):
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    month = models.DateField()  # use the first day of the month (e.g., 2025-04-01)
    total_enrollments = models.PositiveIntegerField()
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # course.price * total_enrollments
    instructor_share = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    platform_share = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    paid_to_instructor = models.BooleanField(default=False)
    paid_on = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('instructor', 'course', 'month')

    def __str__(self):
        return f"{self.course.title} - {self.month.strftime('%B %Y')}"
    
    
    
class InstructorPayout(models.Model):
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    month = models.DateField() 
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payout_method = models.CharField(max_length=50)
    payout_reference = models.CharField(max_length=100, blank=True, null=True)  
    notes = models.TextField(blank=True)
    is_paid = models.BooleanField(default=False)
    paid_on = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        unique_together = ('instructor', 'month')

    def __str__(self):
        return f"Payout to {self.instructor.user.username} for {self.month.strftime('%B %Y')}"
    
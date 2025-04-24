
from django.db import models
from django.utils.text import slugify
from Categories.models import Category
from teacher.models import Instructor
import cloudinary
import cloudinary.uploader
import cloudinary.models
from accounts.models import CustomUser as User

class Course(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )

    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    thumbnail = cloudinary.models.CloudinaryField("image", blank=True, null=True)
    preview_video = cloudinary.models.CloudinaryField("video", resource_type="video", blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_compleated=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)  # Auto-generate slug from title
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title




class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    payment = models.BooleanField(default=False)  # True if payment is successful
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Course completion percentage
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.status})"


class CourseReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Student reporting the course
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # Course being reported
    reason = models.TextField()  # Student explains why they are reporting
    status = models.CharField(
        max_length=10,
        choices=[
            ('Pending', 'Pending'),
            ('Verified', 'Verified'),
            ('Rejected', 'Rejected')
        ],
        default='Pending'
    )  # Admin verification status
    created_at = models.DateTimeField(auto_now_add=True)  # When the report was made
    updated_at = models.DateTimeField(auto_now=True)  # Last updated

    def __str__(self):
        return f"Report by {self.user.username} - {self.course.title} ({self.status})"

class StudentCourseProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed_lessons_count = models.PositiveIntegerField(default=0)
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} - {self.course} - {self.progress}%"

    





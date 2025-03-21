from django.db import models
from Courses.models import Course  
import cloudinary
import cloudinary.uploader
import cloudinary.models





class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    description = models.TextField()
    video_url = models.URLField(blank=True, null=True)  # Store URL of uploaded video
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

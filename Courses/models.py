from django.db import models
from django.utils.text import slugify
from Categories.models import Category
from teacher.models import Instructor
import cloudinary
import cloudinary.uploader
import cloudinary.models

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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)  # Auto-generate slug from title
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

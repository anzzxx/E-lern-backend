from django.db import models
from accounts.models import CustomUser
from django.db import models
from datetime import date
# from Courses.models import Course

class Instructor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="instructor_profile")
    name = models.CharField(max_length=255)
    phone = models.BigIntegerField()
    bio = models.TextField()
    experience = models.CharField(max_length=255)
    organisation = models.TextField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.name


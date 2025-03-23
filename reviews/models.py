from django.db import models
from Courses.models import Course
from accounts.models import CustomUser
class Review(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE,related_name="reviews")
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    rating=models.IntegerField(choices=[(i,i)for i in range(1,6)])
    comment=models.TextField(blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)

    # class Meta:
    #     unique_together=['course','user'] #one riew per use course

    def __str__(self):
        
        return f"{self.user.username} - {self.course.title} ({self.rating})"
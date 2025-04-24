from django.db import models
from Courses.models import Course
class Test(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    title=models.CharField(max_length=100)
    

class Question(models.Model):
    test=models.ForeignKey(Test,on_delete=models.CASCADE)
    text=models.TextField()

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text=models.TextField()
    is_correct=models.BooleanField(default=False)






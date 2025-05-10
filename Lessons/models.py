from django.utils import timezone 
from django.db import models
import cloudinary
import cloudinary.uploader
import cloudinary.models
from Courses.models import Course,StudentCourseProgress 
from accounts.models import CustomUser as User
from django.contrib.auth import get_user_model


User = get_user_model()


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    description = models.TextField()
    video_url = models.URLField(blank=True, null=True)  # Store URL of uploaded video
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class LessonProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'lesson')

    def __str__(self):
        return f"{self.student} - {self.lesson} - {'Done' if self.completed else 'Pending'}"

    def save(self, *args, **kwargs):
        is_new_completion = self.completed and not self.completed_at
        if is_new_completion:
            self.completed_at = timezone.now()

        super().save(*args, **kwargs)

        if is_new_completion:
            update_student_course_progress(self.student, self.lesson.course)


# Utility function
def update_student_course_progress(student, course):
    total_lessons = Lesson.objects.filter(course=course).count()
    completed_lessons = LessonProgress.objects.filter(
        student=student, lesson__course=course, completed=True
    ).count()

    progress_percent = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0

    progress_obj, created = StudentCourseProgress.objects.get_or_create(
        student=student,
        course=course,
        defaults={
            'completed_lessons_count': completed_lessons,
            'progress': progress_percent,
            'is_completed': completed_lessons == total_lessons
        }
    )

    if not created:
        progress_obj.completed_lessons_count = completed_lessons
        progress_obj.progress = progress_percent
        progress_obj.is_completed = completed_lessons == total_lessons
        progress_obj.save()



class CourseComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course_id = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    mentions = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}"      
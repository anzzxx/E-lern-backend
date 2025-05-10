from rest_framework import serializers
from .models import Course
import cloudinary
import cloudinary.uploader
import cloudinary.api
import io
from teacher.models import Instructor
from django.shortcuts import get_object_or_404
from .models import Enrollment, Course, CourseReport, StudentCourseProgress
from accounts.models import CustomUser as User
from Lessons.models import Lesson


class LessonSerializer(serializers.ModelSerializer):
    """
    Serializer for the Lesson model.
    """
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'video_url']


class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer for the Course model, which includes instructor and lessons.
    """
    instructor = serializers.SerializerMethodField(read_only=True)  # Only for retrieval
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            "id", "title", "description", "price", "thumbnail", 
            "preview_video", "status", "is_active", "instructor",
            'lessons'
        ]

    def get_instructor(self, obj):
        """
        Retrieve the instructor details for a course.
        """
        if obj.instructor:
            return {
                "id": obj.instructor.id,
                "user_id": obj.instructor.user.id,  # Extract only the ID
                "name": obj.instructor.name,
            }
        return None

    def create(self, validated_data):
        """
        Custom creation method for a course, including file uploads for thumbnail and preview video.
        """
        request = self.context["request"]
        user = request.user
        instructor = get_object_or_404(Instructor, user=user.id)
        validated_data["instructor"] = instructor  # Assign instructor
        thumbnail = request.FILES.get("thumbnail")
        preview_video = request.FILES.get("prev_vdo")

        if thumbnail:
            thumbnail_data = io.BytesIO(thumbnail.read())
            uploaded_image = cloudinary.uploader.upload(thumbnail_data)
            validated_data["thumbnail"] = uploaded_image["secure_url"]

        if preview_video:
            video_data = io.BytesIO(preview_video.read())
            uploaded_video = cloudinary.uploader.upload_large(video_data, resource_type="video")
            validated_data["preview_video"] = uploaded_video["secure_url"]

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Custom update method for a course, including file uploads for thumbnail and preview video.
        """
        request = self.context["request"]
        thumbnail = request.FILES.get("image")
        preview_video = request.FILES.get("video")

        if thumbnail:
            thumbnail_data = io.BytesIO(thumbnail.read())  # Read file into memory
            uploaded_image = cloudinary.uploader.upload(thumbnail_data)
            instance.thumbnail = uploaded_image["secure_url"]

        if preview_video:
            video_data = io.BytesIO(preview_video.read())  # Read file into memory
            uploaded_video = cloudinary.uploader.upload_large(video_data, resource_type="video")
            instance.preview_video = uploaded_video["secure_url"]

        return super().update(instance, validated_data)


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User (CustomUser) model.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # Add fields you want to include


class EnrolledCourseSerializer(serializers.ModelSerializer):
    """
    Serializer for enrolled courses with additional details such as progress and status.
    """
    instructor_name = serializers.CharField(source='instructor.user.get_full_name')
    enrollment_status = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    enrolled_date = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'slug', 'thumbnail', 
            'instructor_name', 'price', 'enrollment_status', 
            'progress', 'enrolled_date', 'preview_video',
        ]

    def get_enrollment_status(self, obj):
        """
        Retrieve the enrollment status for a user in a course.
        """
        enrollment = obj.enrollments.filter(user=self.context['request'].user).first()
        return enrollment.get_status_display() if enrollment else None

    def get_progress(self, obj):
        """
        Retrieve the progress of a user in a course.
        """
        enrollment = obj.enrollments.filter(user=self.context['request'].user).first()
        return enrollment.progress if enrollment else 0

    def get_enrolled_date(self, obj):
        """
        Retrieve the date a user enrolled in a course.
        """
        enrollment = obj.enrollments.filter(user=self.context['request'].user).first()
        return enrollment.enrolled_at if enrollment else None


class CourseReportSerializer(serializers.ModelSerializer):
    """
    Serializer for course reports, displaying user, course, and report status.
    """
    user = serializers.SerializerMethodField()  # Show user in response

    class Meta:
        model = CourseReport
        fields = ['id', 'user', 'course', 'reason', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']

    def get_user(self, obj):
        """
        Retrieve the username of the user who reported the course.
        """
        return obj.user.username  # Show username instead of ID

    def create(self, validated_data):
        """
        Set the user automatically when creating a course report.
        """
        validated_data['user'] = self.context['request'].user  # Set user automatically
        return super().create(validated_data)


class ReportUserSerializer(serializers.ModelSerializer):
    """
    Serializer for reporting user details including their avatar.
    """
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'avatar']

    def get_avatar(self, obj):
        """
        Retrieve the avatar URL of the user or a placeholder image if none exists.
        """
        if obj.profile_picture:
            return obj.profile_picture.url
        return "https://via.placeholder.com/60"


class ReportCourseSerializer(serializers.ModelSerializer):
    """
    Serializer for reporting course details including instructor and thumbnail.
    """
    instructor = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'image', 'instructor', 'description']

    def get_instructor(self, obj):
        """
        Retrieve the instructor's username for the reported course.
        """
        return obj.instructor.user.username

    def get_image(self, obj):
        """
        Retrieve the thumbnail image URL of the course or a placeholder if none exists.
        """
        if obj.thumbnail:
            return obj.thumbnail.url
        return "https://via.placeholder.com/300x150"


class CourseReportViewSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing course reports with user and course details.
    """
    user = ReportUserSerializer(read_only=True)
    course = ReportCourseSerializer(read_only=True)
    reportedAt = serializers.DateTimeField(source='created_at', format='%Y-%m-%d %H:%M')

    class Meta:
        model = CourseReport
        fields = ['id', 'user', 'course', 'reason', 'reportedAt']


class StudentsProgressSerializer(serializers.ModelSerializer):
    """
    Serializer for student course progress, including lesson count.
    """
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = StudentCourseProgress
        fields = "__all__"

    def get_lesson_count(self, obj):
        """
        Retrieve the number of lessons for a course in student progress.
        """
        return obj.course.lessons.count()

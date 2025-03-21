from rest_framework import serializers
from .models import Course
import cloudinary
import cloudinary.uploader
import cloudinary.api
import io
from teacher.models import Instructor
from django.shortcuts import get_object_or_404
from .models import Enrollment,Course
from accounts.models import CustomUser as User
from Lessons.models import Lesson

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'video_url']

class CourseSerializer(serializers.ModelSerializer):
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
        if obj.instructor:
            return {
                "id": obj.instructor.id,
                "user_id": obj.instructor.user.id,  # Extract only the ID
                "name": obj.instructor.name,  
            }
        return None

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        print(f" user@@{user}")
        instructor = get_object_or_404(Instructor, user=user.id)
        validated_data["instructor"] = instructor  # Assign instructor
        print(f'{instructor}')
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
        request = self.context["request"]
        # print(f"request....{request.FILES}")
        thumbnail = request.FILES.get("image")
        preview_video = request.FILES.get("video")

        if thumbnail:
            # print(f"thumbnile:{thumbnail}")
            thumbnail_data = io.BytesIO(thumbnail.read())  # Read file into memory
            uploaded_image = cloudinary.uploader.upload(thumbnail_data)
            instance.thumbnail = uploaded_image["secure_url"]
    

        if preview_video:
            # print(f"preview_video:{preview_video}")
            video_data = io.BytesIO(preview_video.read())  # Read file into memory
            uploaded_video = cloudinary.uploader.upload_large(video_data, resource_type="video")
            instance.preview_video = uploaded_video["secure_url"]

          

        return super().update(instance, validated_data)

# serializers.py


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # Add fields you want to include


# serializers.py
class EnrollmentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Nested serializer for user
    course = CourseSerializer(read_only=True)  # Nested serializer for course

    class Meta:
        model = Enrollment
        fields = ['id', 'user', 'course', 'payment', 'status', 'progress', 'enrolled_at']        
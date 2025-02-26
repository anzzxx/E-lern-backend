from rest_framework import serializers
from .models import Course
import cloudinary
import cloudinary.uploader
import cloudinary.api
import io
from teacher.models import Instructor
from django.shortcuts import get_object_or_404
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id","title", "description", "price", "thumbnail", "preview_video","status","is_active"]


    def create(self, validated_data):
        request = self.context["request"]
        user=request.user
       
        instructor = get_object_or_404(Instructor, user=user.id)
        validated_data["instructor"] = instructor

        thumbnail = request.FILES.get("thumbnail")
        preview_video = request.FILES.get("prev_vdo")

        if thumbnail:
            thumbnail_data = io.BytesIO(thumbnail.read())  # Read file into memory
            uploaded_image = cloudinary.uploader.upload(thumbnail_data)
            validated_data["thumbnail"] = uploaded_image["secure_url"]

        if preview_video:
            # print(preview_video)
            video_data = io.BytesIO(preview_video.read())  # Read file into memory
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

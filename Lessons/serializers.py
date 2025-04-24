from rest_framework import serializers
from .models import Lesson,LessonProgress
from Courses.models import Course
import cloudinary.uploader

class LessonSerializer(serializers.ModelSerializer):
    video_file = serializers.FileField(write_only=True, required=False)  # Accept file upload
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), write_only=True
    )  # Expect course_id from request
    course_name = serializers.SerializerMethodField() 
    video_url = serializers.URLField(read_only=True)
    course_id = serializers.IntegerField(source="course.id", read_only=True)
    course_name = serializers.CharField(source="course.title", read_only=True)
    class Meta:
        model = Lesson
        fields = ['id', 'course_id', 'course','course_name', 'title', 'description',  'video_file','video_url']  

   
    def create(self, validated_data):
        video_file = validated_data.pop('video_file', None)
        if video_file:
            print(video_file)
            upload_result = cloudinary.uploader.upload(video_file, resource_type="video")
            validated_data['video_url'] = upload_result.get('url')

        return Lesson.objects.create(**validated_data)

    def update(self, instance, validated_data):
        video_file = validated_data.pop('video_file', None)

        if video_file:
            upload_result = cloudinary.uploader.upload(video_file, resource_type="video")
            instance.video_url = upload_result.get('url')
        else:
            instance.video_url = None   

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.course = validated_data.get('course', instance.course)  # Ensure course updates correctly
        instance.save()
        return instance

class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = "__all__" 
        extra_kwargs = {'student': {'read_only': True}} 

    # def create(self, validated_data):
    #     student = self.context['request'].user
    #     validated_data['student'] = student  # Ensure student is saved with the progress
    #     return super().create(validated_data)
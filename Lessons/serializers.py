from rest_framework import serializers
from .models import Lesson, LessonProgress, CourseComment
from Courses.models import Course
import cloudinary.uploader


class LessonSerializer(serializers.ModelSerializer):
    """
    Serializer for Lesson model that handles creation and updating of lessons,
    including video file uploads to Cloudinary.
    """
    video_file = serializers.FileField(write_only=True, required=False)
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), write_only=True
    )
    course_name = serializers.SerializerMethodField()
    video_url = serializers.URLField(read_only=True)
    course_id = serializers.IntegerField(source="course.id", read_only=True)
    course_name = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id',
            'course_id',
            'course',
            'course_name',
            'title',
            'description',
            'video_file',
            'video_url'
        ]

    def create(self, validated_data):
        """
        Create a new Lesson instance with optional video file upload.
        
        Args:
            validated_data: Validated data for lesson creation
            
        Returns:
            Lesson: The created lesson instance
        """
        video_file = validated_data.pop('video_file', None)
        if video_file:
            print(video_file)
            upload_result = cloudinary.uploader.upload(
                video_file,
                resource_type="video"
            )
            validated_data['video_url'] = upload_result.get('url')

        return Lesson.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update an existing Lesson instance with optional video file upload.
        
        Args:
            instance: Lesson instance to update
            validated_data: Validated data for lesson update
            
        Returns:
            Lesson: The updated lesson instance
        """
        video_file = validated_data.pop('video_file', None)

        if video_file:
            upload_result = cloudinary.uploader.upload(
                video_file,
                resource_type="video"
            )
            instance.video_url = upload_result.get('url')
        else:
            instance.video_url = None

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get(
            'description',
            instance.description
        )
        instance.course = validated_data.get('course', instance.course)
        instance.save()
        return instance


class LessonProgressSerializer(serializers.ModelSerializer):
    """
    Serializer for LessonProgress model tracking student progress through lessons.
    """
    class Meta:
        model = LessonProgress
        fields = "__all__"
        extra_kwargs = {'student': {'read_only': True}}


class CourseCommentSerializer(serializers.ModelSerializer):
    """
    Serializer for CourseComment model that includes user details and reply information.
    """
    user = serializers.SerializerMethodField()
    reply_to = serializers.SerializerMethodField()

    class Meta:
        model = CourseComment
        fields = [
            'id',
            'user',
            'message',
            'mentions',
            'reply_to',
            'created_at'
        ]

    def get_user(self, obj):
        """
        Get user information for the comment.
        
        Args:
            obj: CourseComment instance
            
        Returns:
            dict: User information including id, username, and profile picture
        """
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'profile_picture': obj.user.profile_picture.url
            if obj.user.profile_picture else None
        }

    def get_reply_to(self, obj):
        """
        Get reply information if the comment is a reply to another comment.
        
        Args:
            obj: CourseComment instance
            
        Returns:
            dict/None: Reply information or None if not a reply
        """
        if obj.reply_to:
            return {
                'id': obj.reply_to.id,
                'user': {
                    'username': obj.reply_to.user.username,
                },
                'message': obj.reply_to.message
            }
        return None
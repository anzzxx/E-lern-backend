from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Instructor
from payment.models import InstructorPayout
from Courses.models import Enrollment

User = get_user_model()


class InstructorSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed instructor information.
    Includes related user and profile picture.
    """
    user = serializers.StringRelatedField()
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Instructor
        fields = [
            'user', 'id', 'name', 'bio', 'experience',
            'organisation', 'phone', 'profile_picture'
        ]

    def get_profile_picture(self, obj):
        """
        Returns the URL of the instructor's profile picture.
        """
        if obj.user and obj.user.profile_picture:
            return obj.user.profile_picture.url
        return None


class InstructorListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing instructors with limited information.
    Includes email and profile picture from related user.
    """
    email = serializers.EmailField(source='user.email', read_only=True)
    profile_picture = serializers.ImageField(source='user.profile_picture', read_only=True)

    class Meta:
        model = Instructor
        fields = ['id', 'name', 'email', 'bio', 'profile_picture', 'phone']


class InstructorPayoutStatsSerializer(serializers.Serializer):
    """
    Serializer for instructor payout statistics.
    """
    instructor_id = serializers.IntegerField()
    instructor_name = serializers.CharField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    payout_count = serializers.IntegerField()
    paid_payout_count = serializers.IntegerField()
    unpaid_payout_count = serializers.IntegerField()


class InstructorStudentListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing students enrolled with an instructor.
    Includes student name, email, and profile picture URL.
    """
    student_name = serializers.CharField(source='username')
    students_email = serializers.EmailField(source='email')
    student_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['student_name', 'students_email', 'student_profile']

    def get_student_profile(self, obj):
        """
        Returns the absolute URL of the student's profile picture.
        """
        if obj.profile_picture:
            request = self.context.get('request')
            profile_url = obj.profile_picture.url
            return request.build_absolute_uri(profile_url) if request else profile_url
        return None


class InstructorAvgRatingSerializer(serializers.Serializer):
    """
    Serializer for representing average rating of an instructor.
    """
    avg_rating = serializers.FloatField(allow_null=True)


class SalesDataSerializer(serializers.Serializer):
    """
    Serializer for monthly sales data.
    """
    month = serializers.CharField()
    year = serializers.IntegerField()
    purchases = serializers.IntegerField()
    earnings = serializers.DecimalField(max_digits=10, decimal_places=2)


class InstructorSalesSerializer(serializers.ModelSerializer):
    """
    Serializer for representing instructor sales data per enrollment.
    Includes user and course information.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'username', 'course_title', 'enrolled_at']

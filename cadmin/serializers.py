from rest_framework import serializers

from accounts.models import CustomUser
from Courses.models import Course
from teacher.models import Instructor


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.
    Returns user id, username, email, and is_active status.
    Username and email are read-only fields.
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'is_active']
        read_only_fields = ['id', 'username', 'email']


class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer for the Course model.
    Includes all fields and a read-only instructor name from the related Instructor model.
    """
    instructor = serializers.CharField(source="instructor.name", read_only=True)

    class Meta:
        model = Course
        fields = '__all__'


class TotalEnrolledStudentsSerializer(serializers.Serializer):
    """
    Serializer to represent the total number of enrolled students.
    """
    total_enrolled = serializers.IntegerField()


class TotalRevenueSerializer(serializers.Serializer):
    """
    Serializer to represent the total revenue from course enrollments.
    """
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)


class CourseAnalyticsSerializer(serializers.Serializer):
    """
    Serializer to represent analytical data for a course, including
    title, total enrollment, average review, revenue, and active status.
    """
    title = serializers.CharField()
    total_enrollment = serializers.IntegerField()
    avg_review = serializers.FloatField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    is_active = serializers.BooleanField()

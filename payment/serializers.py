from rest_framework import serializers, generics
from .models import Payment, MonthlyCourseStats
from accounts.models import CustomUser
from Courses.models import Course
from rest_framework import serializers
from .models import InstructorPayout
class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    course = serializers.StringRelatedField()

    class Meta:
        model = Payment
        fields = ['id','user','course','method','amount','status','created_at','updated_at','transaction_id']
        


class EnrollmentCountSerializer(serializers.Serializer):
    course_title = serializers.CharField()
    month = serializers.DateField()
    enrollment_count = serializers.IntegerField()
        

class MonthlyCourseStatsSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title')
    class Meta:
        model = MonthlyCourseStats
        fields = [
            'id', 'course_title', 'month', 'total_enrollments',
            'total_amount', 'instructor_share', 'platform_share',
            'paid_to_instructor', 'paid_on'
        ]        



class InstructorPayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstructorPayout
        fields = '__all__'   
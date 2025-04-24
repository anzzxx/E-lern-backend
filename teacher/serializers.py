from rest_framework import serializers
from .models import Instructor


class InstructorSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = Instructor
        fields = ['user','id', 'name', 'bio', 'experience', 'organisation', 'phone']

class InstructorListSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(source='user.email', read_only=True)
    profile_picture=serializers.ImageField(source='user.profile_picture', read_only=True)
    class Meta:
        model = Instructor
        fields = ['id', 'name','email', 'bio', 'profile_picture', 'phone']

# class InstructorPaymentSerializer(serializers.ModelSerializer):
#     instructor_name = serializers.CharField(source='instructor.name', read_only=True)  

#     class Meta:
#         model = InstructorPayment
#         fields = ['id', 'instructor', 'instructor_name', 'month', 'year', 'amount', 'payment_date', 'status']

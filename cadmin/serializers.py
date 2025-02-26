from rest_framework import serializers
from accounts.models import CustomUser  
from Courses.models import Course
from teacher.models import Instructor  # Import Instructor model

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser  
        fields = ['id', 'username', 'email','is_active']  
        read_only_fields = ['id', 'username', 'email', ] 



class CourseSerializer(serializers.ModelSerializer):
    instructor = serializers.CharField(source="instructor.name", read_only=True)           
    class Meta:
        model = Course
        fields = '__all__'  # Keeps all fields but replaces instructor with email


from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()  
    class Meta:
        model = Review
        fields =['id','course','rating','comment','created_at','user_details',]
        read_only_fields = ['id','created_at','user_details',]

    def validate(self,data):
        user=self.context['request'].user
        course=data['course']

        # if Review.objects.filter(user=user,course=course).exists():
        #     raise serializers.ValidationError('You have already reviewed this course')

        return data     

    def get_user_details(self, obj):
        """Fetch user details (username & email) from related user object"""
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "email": obj.user.email,
            "profile": obj.user.profile_picture.url if obj.user.profile_picture else None,
        }       
from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the Review model.

    Adds user details via a computed field and includes validation logic.
    """
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id',
            'course',
            'rating',
            'comment',
            'created_at',
            'user_details',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'user_details',
        ]

    def validate(self, data):
        """
        Validate review data. You can add custom validation logic here if needed.
        """
        user = self.context['request'].user
        course = data['course']
        return data

    def get_user_details(self, obj):
        """
        Fetch user details (username, email, and profile picture URL) 
        from the related user object.
        """
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "email": obj.user.email,
            "profile": obj.user.profile_picture.url if obj.user.profile_picture else None,
        }

from rest_framework import serializers,generics
from .models import Test,Question,Answer

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = '__all__'
    
    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters long.")
        return value

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
    
    def validate_text(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Question text must be at least 10 characters long.")
        return value

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'
    
    def validate_text(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Answer text must be at least 3 characters long.")
        return value

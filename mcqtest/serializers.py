from rest_framework import serializers, generics
from .models import Test, Question, Answer


class TestSerializer(serializers.ModelSerializer):
    """
    Serializer for Test model that includes question count and title validation.
    """
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = '__all__'

    def get_question_count(self, obj):
        """
        Returns the number of questions associated with this test.
        
        Args:
            obj: Test instance
            
        Returns:
            int: Count of questions for this test
        """
        return obj.question_set.count()

    def validate_title(self, value):
        """
        Validate that the test title is at least 5 characters long.
        
        Args:
            value: Title value to validate
            
        Returns:
            str: Validated title
            
        Raises:
            ValidationError: If title is too short
        """
        if len(value) < 5:
            raise serializers.ValidationError(
                "Title must be at least 5 characters long."
            )
        return value


class AnswerSerializer(serializers.ModelSerializer):
    """
    Serializer for Answer model with text validation.
    """
    class Meta:
        model = Answer
        fields = '__all__'

    def validate_text(self, value):
        """
        Validate that the answer text is at least 3 characters long.
        
        Args:
            value: Answer text to validate
            
        Returns:
            str: Validated answer text
            
        Raises:
            ValidationError: If answer text is too short
        """
        if len(value) < 3:
            raise serializers.ValidationError(
                "Answer text must be at least 3 characters long."
            )
        return value


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for Question model that includes nested answers and text validation.
    """
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = '__all__'

    def validate_text(self, value):
        """
        Validate that the question text is at least 10 characters long.
        
        Args:
            value: Question text to validate
            
        Returns:
            str: Validated question text
            
        Raises:
            ValidationError: If question text is too short
        """
        if len(value) < 10:
            raise serializers.ValidationError(
                "Question text must be at least 10 characters long."
            )
        return value
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Count

from .models import Test, Question, Answer
from .serializers import TestSerializer, QuestionSerializer, AnswerSerializer
from teacher.models import Instructor
from Courses.models import Course


class TestView(APIView):
    """API endpoint for retrieving tests associated with a course."""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        Retrieve all tests for a specific course with question counts.
        
        Args:
            request: HTTP request object
            pk: Primary key of the course
            
        Returns:
            Response: List of tests with question counts or error message
        """
        try:
            tests = Test.objects.filter(course=pk).annotate(
                question_count=Count('question')
            )
            serializer = TestSerializer(tests, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TestCreateView(APIView):
    """API endpoint for creating and updating tests."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Create a new test.
        
        Args:
            request: HTTP request object with test data
            
        Returns:
            Response: Created test data or error message
        """
        try:
            serializer = TestSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, pk):
        """
        Update an existing test.
        
        Args:
            request: HTTP request object with updated test data
            pk: Primary key of the test to update
            
        Returns:
            Response: Updated test data or error message
        """
        try:
            test = Test.objects.get(pk=pk)
            serializer = TestSerializer(
                test,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Test.DoesNotExist:
            return Response(
                {"error": "Test not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuestionView(APIView):
    """API endpoint for retrieving questions for a specific test."""
    permission_classes = [IsAuthenticated]

    def get(self, request, testId):
        """
        Retrieve all questions for a specific test.
        
        Args:
            request: HTTP request object
            testId: Primary key of the test
            
        Returns:
            Response: List of questions or error message
        """
        try:
            questions = Question.objects.filter(test_id=testId)
            serializer = QuestionSerializer(questions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuestionCreateView(APIView):
    """API endpoint for creating and updating questions."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Create a new question.
        
        Args:
            request: HTTP request object with question data
            
        Returns:
            Response: Created question data or error message
        """
        try:
            serializer = QuestionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, pk):
        """
        Update an existing question.
        
        Args:
            request: HTTP request object with updated question data
            pk: Primary key of the question to update
            
        Returns:
            Response: Updated question data or error message
        """
        try:
            question = Question.objects.get(pk=pk)
            serializer = QuestionSerializer(
                question,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Question.DoesNotExist:
            return Response(
                {"error": "Question not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AnswerView(APIView):
    """API endpoint for retrieving answers for a specific question."""
    permission_classes = [IsAuthenticated]

    def get(self, request, questionId):
        """
        Retrieve all answers for a specific question.
        
        Args:
            request: HTTP request object
            questionId: Primary key of the question
            
        Returns:
            Response: List of answers or error message
        """
        try:
            answers = Answer.objects.filter(question_id=questionId)
            serializer = AnswerSerializer(answers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AnswerCreateView(APIView):
    """API endpoint for creating, updating and deleting answers."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Create a new answer.
        
        Args:
            request: HTTP request object with answer data
            
        Returns:
            Response: Created answer data or error message
        """
        try:
            serializer = AnswerSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, pk):
        """
        Update an existing answer.
        
        Args:
            request: HTTP request object with updated answer data
            pk: Primary key of the answer to update
            
        Returns:
            Response: Updated answer data or error message
        """
        try:
            answer = Answer.objects.get(pk=pk)
            serializer = AnswerSerializer(
                answer,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Answer.DoesNotExist:
            return Response(
                {"error": "Answer not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, pk):
        """
        Delete an existing answer.
        
        Args:
            request: HTTP request object
            pk: Primary key of the answer to delete
            
        Returns:
            Response: Success status or error message
        """
        try:
            answer = Answer.objects.get(pk=pk)
            answer.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Answer.DoesNotExist:
            return Response(
                {"error": "Answer not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
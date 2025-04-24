from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Test, Question, Answer
from .serializers import TestSerializer, QuestionSerializer, AnswerSerializer
from teacher.models import Instructor
from Courses.models import Course
from django.db.models import Count
class TestView(APIView):
    """Handles GET Retrieve all"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Retrieve tests for a course, including question counts."""
        try:
            tests = Test.objects.filter(course=pk).annotate(
                question_count=Count('question')  
            )
            serializer = TestSerializer(tests, many=True)
            # Return empty array instead of 404 when no tests found
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TestCreateView(APIView):
    def post(self, request):
        """Create a new test"""
        try:
            serializer = TestSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                print('created')
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            print('not created')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    

    # def put(self, request, pk):
    #     """Update a specific test"""
    #     try:
    #         test = Test.objects.get(pk=pk)
    #         serializer = TestSerializer(test, data=request.data, partial=True)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response(serializer.data, status=status.HTTP_200_OK)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     except Test.DoesNotExist:
    #         return Response({"error": "Test not found"}, status=status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class QuestionView(APIView):
    """Handles GET Retrieve all questions for a particular test"""
    permission_classes = [IsAuthenticated]

    def get(self, request, testId):
        """Retrieve questions for a specific test ID"""
        try:
            questions = Question.objects.filter(test_id=testId)
            serializer = QuestionSerializer(questions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class QustionCreateView(APIView):
    """Handles POST create New Qustion """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        """Create a new question"""
        try:
            serializer = QuestionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def put(self, request, pk):
    #     """Update a specific question"""
    #     try:
    #         question = Question.objects.get(pk=pk)
    #         serializer = QuestionSerializer(question, data=request.data, partial=True)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response(serializer.data, status=status.HTTP_200_OK)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     except Question.DoesNotExist:
    #         return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AnswerView(APIView):
    """Handles GET (Retrieve all), POST (Create), and PUT (Update specific Answer)"""
    permission_classes = [IsAuthenticated]

    def get(self, request,qustionId):
        print(qustionId,"qustion id")
        """Retrieve all answers"""
        try:
            answers = Answer.objects.all()
            serializer = AnswerSerializer(answers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AnswerCreateView(APIView):
    """Handles POST create New Answer """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        """Create a new answer"""
        try:
            serializer = AnswerSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def put(self, request, pk):
    #     """Update a specific answer"""
    #     try:
    #         answer = Answer.objects.get(pk=pk)
    #         serializer = AnswerSerializer(answer, data=request.data, partial=True)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response(serializer.data, status=status.HTTP_200_OK)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     except Answer.DoesNotExist:
    #         return Response({"error": "Answer not found"}, status=status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

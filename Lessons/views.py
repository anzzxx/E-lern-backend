from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.utils import timezone

from .models import Lesson, LessonProgress, CourseComment
from .serializers import (
    LessonSerializer,
    LessonProgressSerializer,
    CourseCommentSerializer
)
from accounts.models import CustomUser


class LessonListCreateView(generics.ListCreateAPIView):
    """
    API endpoint that allows listing and creating lessons.
    Supports filtering by course_id query parameter.
    """
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Get lessons filtered by course_id if provided in query params.
        
        Returns:
            QuerySet: Filtered lessons or empty queryset if no course_id provided
        """
        course_id = self.request.query_params.get("course_id")
        if course_id:
            return Lesson.objects.filter(course_id=course_id)
        return Lesson.objects.none()  # or raise exception if you prefer

    def create(self, request, *args, **kwargs):
        """
        Create a new lesson with custom success/error response format.
        
        Returns:
            Response: Standardized response with success status and message
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            lesson = serializer.save()
            return Response({
                "success": True,
                "message": "Lesson created successfully",
                "data": LessonSerializer(lesson).data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Error creating lesson",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint that allows retrieving, updating and deleting individual lessons.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        """
        Update a lesson with custom success/error response format.
        
        Returns:
            Response: Standardized response with success status and message
        """
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        print(request.data)
        if serializer.is_valid():
            lesson = serializer.save()
            return Response({
                "success": True,
                "message": "Lesson updated successfully",
                "data": LessonSerializer(lesson).data
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "message": "Error updating lesson",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LessonProgressCreateUpdateView(generics.ListCreateAPIView):
    """
    API endpoint for tracking and updating lesson progress for authenticated users.
    """
    serializer_class = LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Get lesson progress records for the current user.
        
        Returns:
            QuerySet: Filtered by the authenticated user
        """
        return LessonProgress.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        """
        Create or update lesson progress record, preventing duplicate completions.
        
        Args:
            serializer: Validated serializer instance
            
        Raises:
            ValidationError: If lesson is already marked as completed
        """
        lesson = serializer.validated_data['lesson']
        student = self.request.user

        existing_progress = LessonProgress.objects.filter(
            student=student,
            lesson=lesson
        ).first()

        if existing_progress:
            if existing_progress.completed:
                raise ValidationError("You have already completed this lesson.")
            else:
                existing_progress.completed = True
                existing_progress.completed_at = timezone.now()
                existing_progress.save()
                return existing_progress

        serializer.save(student=student)


class CourseCommentList(APIView):
    """
    API endpoint for listing course comments with related user and reply information.
    """
    serializer_class = CourseCommentSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        """
        Get latest 50 comments for a course.
        
        Args:
            request: HTTP request object
            course_id: ID of the course to get comments for
            
        Returns:
            Response: Serialized comment data
        """
        print("entered")
        comments = CourseComment.objects.filter(
            course_id=course_id
        ).select_related('user', 'reply_to').order_by('created_at')[:50]

        serializer = self.serializer_class(comments, many=True)
        return Response(serializer.data)
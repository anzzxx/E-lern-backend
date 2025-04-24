from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Lesson,LessonProgress
from .serializers import LessonSerializer,LessonProgressSerializer
from accounts.models import CustomUser

class LessonListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        course_id = self.request.query_params.get("course_id")
        if course_id:
            return Lesson.objects.filter(course_id=course_id)
        return Lesson.objects.none()  # or raise exception if you prefer

    def create(self, request, *args, **kwargs):
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
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        """Custom response for updating lesson"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
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
    serializer_class = LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LessonProgress.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
       
        lesson = serializer.validated_data['lesson']
        student = self.request.user

        existing_progress = LessonProgress.objects.filter(student=student, lesson=lesson).first()

        if existing_progress:
            if existing_progress.completed:
                raise ValidationError("You have already completed this lesson.")
            else:
                existing_progress.completed = True
                existing_progress.completed_at = timezone.now()
                existing_progress.save()
                return existing_progress

        serializer.save(student=student)
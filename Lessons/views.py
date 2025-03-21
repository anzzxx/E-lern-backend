from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Lesson
from .serializers import LessonSerializer

class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]  # JWT Authentication required

    def create(self, request, *args, **kwargs):
        """Custom response for lesson creation"""
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
